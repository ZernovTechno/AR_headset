function enterFullScreen(element) {
          if(element.requestFullscreen) {
            element.requestFullscreen();
          }else if (element.mozRequestFullScreen) {
            element.mozRequestFullScreen();     // Firefox
          }else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();  // Safari
          }else if(element.msRequestFullscreen) {
            element.msRequestFullscreen();      // IE/Edge
          }
        };

let btn = document.getElementById("full_screen");
btn.addEventListener("click", function(){
  let videoEle = document.querySelector('div');
  enterFullScreen(videoEle);
});