// 06-filter.js — 分類篩選（單選，再點取消）與 aria-live 朗讀
// 4.1.3 篩選結果用 aria-live 朗讀
function announce(){
  var live = document.getElementById('live');
  if (!live) return;
  var en = document.getElementById('sheet').classList.contains('en');
  if (picked === null) {
    live.textContent = en ? 'Showing all classes' : '顯示全部課程';
  } else {
    var n = document.querySelectorAll('.ev.match').length;
    var k = document.querySelector('.key[data-cat="' + picked + '"]');
    var lab = k ? (k.querySelector(en ? '.en' : '.zh') || {}).textContent : picked;
    live.textContent = en ? ('Filtered: ' + lab + ', ' + n + ' classes')
                          : ('已篩選：' + lab + '，共 ' + n + ' 堂');
  }
}
// 分類篩選：單選，再點同一個即取消
var picked = null;
function applyFilter(){
  var sheet = document.getElementById('sheet'), keys = document.querySelector('.keys');
  var on = picked !== null;
  sheet.classList.toggle('on', on);
  keys.classList.toggle('on', on);
  document.querySelectorAll('.key').forEach(function(k){
    k.classList.toggle('sel', k.dataset.cat === picked);
    k.setAttribute('aria-pressed', k.dataset.cat === picked ? 'true' : 'false');
  });
  document.querySelectorAll('.ev,.lc').forEach(function(ev){
    ev.classList.toggle('match', ev.dataset.cat === picked);
  });
  announce();
}
document.querySelector('.keys').addEventListener('click', function(e){
  var k = e.target.closest('.key'); if(!k) return;
  picked = (picked === k.dataset.cat) ? null : k.dataset.cat;
  applyFilter();
});
document.getElementById('clear').addEventListener('click', function(){
  picked = null; applyFilter();
});
