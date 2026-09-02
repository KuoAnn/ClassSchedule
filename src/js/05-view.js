// 05-view.js — 寬版／窄版切換並記住選擇
var vseg = document.getElementById('view');
function setView(v){
  document.documentElement.className = (v === 'n' ? 'nv' : 'wv');
  Array.prototype.forEach.call(vseg.children, function(x){
    var on = x.dataset.v === v;
    x.classList.toggle('on', on);
    x.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
  try { localStorage.setItem('yoga-view', v); } catch(e) {}
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
