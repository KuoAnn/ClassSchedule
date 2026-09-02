// 05-view.js — 寬版／窄版切換並記住選擇
var vseg = document.getElementById('view');
function setView(v){
  // 用 toggle 而不是直接指派 className：01-boot.js 掛的 .liff 要留著
  document.documentElement.classList.toggle('nv', v === 'n');
  document.documentElement.classList.toggle('wv', v !== 'n');
  Array.prototype.forEach.call(vseg.children, function(x){
    var on = x.dataset.v === v;
    x.classList.toggle('on', on);
    x.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
  try { localStorage.setItem('yoga-view', v); } catch(e) {}
  // 兩種版型要的 viewport 不同（窄版跟裝置寬、寬版是固定寬海報），切換時一起換
  setViewport(v === 'n');
  fitCells();
  measureDock();
  if (v === 'n') requestAnimationFrame(function(){ syncRows(); layout(); goDay(cur + NDAYS, false); updateDock(); });
  else ndock.classList.remove('show');
}
vseg.addEventListener('click', function(e){
  var b = e.target.closest('button'); if(!b) return;
  setView(b.dataset.v);
});
setView(document.documentElement.classList.contains('nv') ? 'n' : 'w');
