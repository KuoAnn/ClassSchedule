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
  // 網址帶 ?v= 進來的（LINE 交給外部瀏覽器存圖那條路）只是借過一次，
  // 不要蓋掉這台瀏覽器自己記住的選擇；存完圖 09-liff.js 會把參數清掉
  if (!qparam('v')) { try { localStorage.setItem('yoga-view', v); } catch(e) {} }
  // 兩種版型要的 viewport 不同（窄版跟裝置寬、寬版是固定寬海報），切換時一起換
  setViewport(v === 'n');
  fitCells();
  measureDock();
  // layout() 先跑：它會依螢幕寬算出 --dayw，syncRows() 才量得到對的卡片高度
  if (v === 'n') requestAnimationFrame(function(){ layout(); syncRows(); goDay(cur + NDAYS, false); updateDock(); });
  else ndock.classList.remove('show');
}
vseg.addEventListener('click', function(e){
  var b = e.target.closest('button'); if(!b) return;
  setView(b.dataset.v);
});
setView(document.documentElement.classList.contains('nv') ? 'n' : 'w');
