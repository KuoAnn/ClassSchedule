// 02-fit.js — 卡片內容超出高度時逐級縮字（f1–f4）
function fitCells(){
  var els = document.querySelectorAll('.ev'), steps = ['f1','f2','f3','f4'];
  for (var i = 0; i < els.length; i++){
    var el = els[i];
    el.classList.remove('f1','f2','f3','f4');
    for (var j = 0; j < steps.length; j++){
      if (el.scrollHeight <= el.clientHeight) break;
      if (j) el.classList.remove(steps[j-1]);
      el.classList.add(steps[j]);
    }
  }
}
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(fitCells);
