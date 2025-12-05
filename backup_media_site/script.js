function setupHlsPlayer(videoId, hlsUrl) {
  var video = document.getElementById(videoId);
  if (Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource(hlsUrl);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, function () {
      // video.play(); // Auto-play is disabled for better user experience
    });
  }
}

setupHlsPlayer('rtv-video', 'https://5c46fa289c89f.streamlock.net:443/rtv25/rtv/playlist.m3u8');
setupHlsPlayer('kc2-video', 'https://5c46fa289c89f.streamlock.net:443/kc2/kc2/playlist.m3u8');
