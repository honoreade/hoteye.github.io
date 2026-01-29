

function setupHlsPlayerOverlay(videoId, overlayId, hlsUrl) {
  const video = document.getElementById(videoId);
  const overlay = document.getElementById(overlayId);
  let hlsLoaded = false;
  let hlsInstance = null;

  function showOverlay() {
    overlay.removeAttribute('hidden');
    video.pause();
    video.currentTime = 0;
    video.load();
  }
  function hideOverlay() {
    overlay.setAttribute('hidden', '');
  }

  function startStream() {
    if (!hlsLoaded && Hls.isSupported()) {
      hlsInstance = new Hls();
      hlsInstance.loadSource(hlsUrl);
      hlsInstance.attachMedia(video);
      hlsInstance.on(Hls.Events.MANIFEST_PARSED, function () {
        video.play();
      });
      hlsInstance.on(Hls.Events.ERROR, function (event, data) {
        if (data.fatal) {
          showOverlay();
          hlsInstance.destroy();
          hlsLoaded = false;
        }
      });
      hlsLoaded = true;
    } else {
      video.play();
    }
    hideOverlay();
  }

  overlay.addEventListener('click', startStream);
  video.addEventListener('play', hideOverlay);
  video.addEventListener('pause', function() {
    if (video.currentTime === 0 || video.ended) {
      showOverlay();
    }
  });

  // Show overlay on load
  showOverlay();
}

setupHlsPlayerOverlay('rtv-video', 'rtv-overlay', 'https://5c46fa289c89f.streamlock.net:443/rtv25/rtv/playlist.m3u8');
setupHlsPlayerOverlay('kc2-video', 'kc2-overlay', 'https://5c46fa289c89f.streamlock.net:443/kc2/kc2/playlist.m3u8');
