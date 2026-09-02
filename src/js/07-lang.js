// 07-lang.js — 中英切換
function applyLang(l){
  var sheet = document.getElementById('sheet'), en = (l === 'en');
  sheet.classList.toggle('en', en);
  document.documentElement.lang = en ? 'en' : 'zh-Hant';
  var seg = document.getElementById('lang');
  Array.prototype.forEach.call(seg.children, function(x){
    var on = x.dataset.l === l;
    x.classList.toggle('on', on);
    x.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
  // 卡片的無障礙名稱也要跟著換語言
  document.querySelectorAll('[data-lab-en]').forEach(function(el){
    if (!el.dataset.labZh) el.dataset.labZh = el.getAttribute('aria-label');
    el.setAttribute('aria-label', en ? el.dataset.labEn : el.dataset.labZh);
  });
  announce();
}
document.getElementById('lang').addEventListener('click', function(e){
  var b = e.target.closest('button'); if(!b) return;
  applyLang(b.dataset.l);
  fitCells();
  syncRows();
});
