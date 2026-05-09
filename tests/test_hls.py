import os
import subprocess
import time
import unittest
from playwright.sync_api import sync_playwright

class TestHLSSupport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start a local server to serve the files
        cls.server_process = subprocess.Popen(
            ["python3", "-m", "http.server", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait for the server to be ready
        max_retries = 10
        for i in range(max_retries):
            try:
                import urllib.request
                urllib.request.urlopen("http://localhost:8000", timeout=1)
                break
            except:
                time.sleep(1)
        else:
            raise Exception("Server failed to start")

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_hls_not_supported_fallback(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Mock Hls.isSupported to return false
            page.add_init_script("""
                window.Hls = {
                    isSupported: () => false
                };
            """)

            # Block ALL external requests
            def block_external(route):
                url = route.request.url
                if "localhost" in url:
                    route.continue_()
                else:
                    route.abort()
            page.route("**/*", block_external)

            # Navigate to the page
            page.goto("http://localhost:8000", wait_until="commit")

            # Wait for our scripts to load
            page.wait_for_selector(".play-overlay", state="attached")

            # Spy on video.play and mock canPlayType
            page.evaluate("""
                window.playCalled = false;
                window.srcSet = null;

                const originalCanPlayType = HTMLVideoElement.prototype.canPlayType;
                HTMLVideoElement.prototype.canPlayType = function(type) {
                    if (type === 'application/vnd.apple.mpegurl') {
                        return 'probably';
                    }
                    return originalCanPlayType.call(this, type);
                };

                const video = document.querySelector('video');

                // Intercept src setting
                Object.defineProperty(video, 'src', {
                    set: function(val) {
                        window.srcSet = val;
                        this.setAttribute('src', val);
                    },
                    get: function() {
                        return this.getAttribute('src');
                    }
                });

                video.play = function() {
                    window.playCalled = true;
                    return Promise.resolve();
                };
            """)

            # Click the first overlay
            page.dispatch_event(".play-overlay", "click")

            # Emulate loadedmetadata event since it waits for it
            page.evaluate("document.querySelector('video').dispatchEvent(new Event('loadedmetadata'))")

            # Check if play was called
            play_called = page.evaluate("window.playCalled")
            src_set = page.evaluate("window.srcSet")

            self.assertTrue(play_called, "video.play() should be called even if HLS is not supported")
            self.assertIsNotNone(src_set, "Source should be set in fallback case")
            self.assertTrue(src_set.endswith('.m3u8'), f"Source should be set to an HLS URL (.m3u8) in fallback case, got {src_set}")

            browser.close()

    def test_hls_supported_initialization(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Mock Hls.isSupported to return true and mock Hls constructor
            page.add_init_script("""
                window.hlsInstances = [];
                window.Hls = class {
                    static isSupported() { return true; }
                    constructor() {
                        this.url = null;
                        window.hlsInstances.push(this);
                    }
                    loadSource(url) { this.url = url; }
                    attachMedia(media) { this.media = media; }
                    on(event, callback) {
                        if (event === 'hlsManifestParsed') {
                            this.manifestParsedCallback = callback;
                        }
                    }
                    destroy() {}
                };
                window.Hls.Events = {
                    MANIFEST_PARSED: 'hlsManifestParsed',
                    ERROR: 'hlsError'
                };
            """)

            # Block ALL external requests
            def block_external(route):
                url = route.request.url
                if "localhost" in url:
                    route.continue_()
                else:
                    route.abort()
            page.route("**/*", block_external)

            page.goto("http://localhost:8000", wait_until="commit")
            page.wait_for_selector(".play-overlay", state="attached")

            # Click the first overlay
            page.dispatch_event(".play-overlay", "click")

            # Verify Hls instance was created and configured
            hls_info = page.evaluate("""
                () => {
                    if (window.hlsInstances.length === 0) return null;
                    const inst = window.hlsInstances[0];
                    return {
                        url: inst.url,
                        hasMedia: !!inst.media
                    };
                }
            """)

            self.assertIsNotNone(hls_info)
            self.assertTrue(hls_info['url'].endswith('.m3u8'))
            self.assertTrue(hls_info['hasMedia'])

            browser.close()

    def test_hls_fatal_error(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Mock Hls.isSupported to return true and mock Hls constructor
            page.add_init_script("""
                window.hlsInstances = [];
                window.Hls = class {
                    static isSupported() { return true; }
                    constructor() {
                        this.url = null;
                        this.destroyed = false;
                        window.hlsInstances.push(this);
                    }
                    loadSource(url) { this.url = url; }
                    attachMedia(media) { this.media = media; }
                    on(event, callback) {
                        if (event === 'hlsManifestParsed') {
                            this.manifestParsedCallback = callback;
                        } else if (event === 'hlsError') {
                            this.errorCallback = callback;
                        }
                    }
                    destroy() { this.destroyed = true; }
                };
                window.Hls.Events = {
                    MANIFEST_PARSED: 'hlsManifestParsed',
                    ERROR: 'hlsError'
                };
            """)

            # Block ALL external requests
            def block_external(route):
                url = route.request.url
                if "localhost" in url:
                    route.continue_()
                else:
                    route.abort()
            page.route("**/*", block_external)

            page.goto("http://localhost:8000", wait_until="commit")
            page.wait_for_selector(".play-overlay", state="attached")

            # Click the first overlay
            page.dispatch_event(".play-overlay", "click")

            # Emulate HLS Fatal Error and check overlay
            result = page.evaluate("""
                () => {
                    const inst = window.hlsInstances[0];
                    if (inst && inst.errorCallback) {
                        // Call the error callback with a fatal error
                        inst.errorCallback('hlsError', { fatal: true });

                        // Check if overlay is shown
                        const overlay = document.querySelector('.play-overlay');
                        const isHidden = overlay.hasAttribute('hidden');

                        return {
                            overlayHidden: isHidden,
                            hlsDestroyed: inst.destroyed
                        };
                    }
                    return null;
                }
            """)

            self.assertIsNotNone(result)
            self.assertFalse(result['overlayHidden'], "Overlay should be visible after fatal error")
            self.assertTrue(result['hlsDestroyed'], "Hls instance should be destroyed after fatal error")

            browser.close()

if __name__ == "__main__":
    unittest.main()
