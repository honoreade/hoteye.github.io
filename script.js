
var video = document.getElementById('rtv-video');
var hlsUrl = 'https://5c46fa289c89f.streamlock.net:443/rtv25/rtv/playlist.m3u8';
if(Hls.isSupported()) {
  var hls = new Hls();
  hls.loadSource(hlsUrl);
  hls.attachMedia(video);
  hls.on(Hls.Events.MANIFEST_PARSED,function() {
    // video.play(); // Disabled auto-play
  });
}

var kc2Video = document.getElementById('kc2-video');
var kc2HlsUrl = 'https://5c46fa289c89f.streamlock.net:443/kc2/kc2/playlist.m3u8';
if(Hls.isSupported()) {
  var kc2Hls = new Hls();
  kc2Hls.loadSource(kc2HlsUrl);
  kc2Hls.attachMedia(kc2Video);
  kc2Hls.on(Hls.Events.MANIFEST_PARSED,function() {
    // kc2Video.play(); // Disabled auto-play
  });
}
