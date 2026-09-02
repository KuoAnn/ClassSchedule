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
  fitCells();
  measureDock();
  // layout() 先跑：它會依螢幕寬算出 --dayw，syncRows() 才量得到對的卡片高度
  if (v === 'n') requestAnimationFrame(function(){ layout(); syncRows(); goDay(cur + NDAYS, false); updateDock(); });
  else { ndock.classList.remove('show'); requestAnimationFrame(showToday); }
}
// 寬版是原尺寸的海報（--sheetw 比手機寬），螢幕塞不下時整份文件會橫向捲動 ——
// 停在最左邊等於停在星期一，所以有橫向溢出時就把「今天」那一欄帶進畫面。
// 只動水平位置：垂直位置是使用者剛剛在看的地方，不要一起跳掉。
function showToday(){
  var de = document.documentElement;
  if (de.classList.contains('nv')) return;
  var vw = window.innerWidth || de.clientWidth;
  if (de.scrollWidth <= vw + 4) return;          // 桌機放得下整張，不要自作主張捲動
  var col = document.querySelector('.cols .col.today');
  if (!col) return;
  var r = col.getBoundingClientRect();
  var sx = window.pageXOffset || 0;
  window.scrollTo({left: Math.max(0, sx + r.left - (vw - r.width) / 2),
                   top: window.pageYOffset || 0});
}
vseg.addEventListener('click', function(e){
  var b = e.target.closest('button'); if(!b) return;
  setView(b.dataset.v);
});
setView(document.documentElement.classList.contains('nv') ? 'n' : 'w');
