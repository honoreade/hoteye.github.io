
function setupHlsPlayerOnClick(videoId, hlsUrl) {
  var video = document.getElementById(videoId);
  let hlsLoaded = false;
  let hlsInstance = null;
  video.addEventListener('click', function handlePlay() {
    if (!hlsLoaded && Hls.isSupported()) {
      hlsInstance = new Hls();
      hlsInstance.loadSource(hlsUrl);
      hlsInstance.attachMedia(video);
      hlsInstance.on(Hls.Events.MANIFEST_PARSED, function () {
        video.play();
      });
      hlsLoaded = true;
    } else if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  });
}

setupHlsPlayerOnClick('rtv-video', 'https://5c46fa289c89f.streamlock.net:443/rtv25/rtv/playlist.m3u8');
setupHlsPlayerOnClick('kc2-video', 'https://5c46fa289c89f.streamlock.net:443/kc2/kc2/playlist.m3u8');
