// 03-status.js — 標記今天，並依現在時間標出結束／進行中
(function(){
  var td = (new Date().getDay() + 6) % 7;
  document.querySelectorAll('[data-day="' + td + '"]').forEach(function(el){
    el.classList.add('today');
  });
})();
// 當天課程三種狀態：已結束（反灰淡化）／進行中（標籤＋外圈）／待開課（不標）
var STATE = {
  done: {zh: '結束', en: 'Ended'},
  live: {zh: '進行中', en: 'Live'}
};
function markPast(){
  var d = new Date(), td = (d.getDay() + 6) % 7, now = d.getHours() * 60 + d.getMinutes();
  document.querySelectorAll('.ev,.lc').forEach(function(el){
    var host = el.closest('[data-day]');
    var today = !!host && +host.dataset.day === td;
    var st = +el.dataset.start, en = +el.dataset.end;
    var state = '';
    if (today) {
      if (now >= en) state = 'done';
      else if (now >= st) state = 'live';
    }
    el.classList.toggle('st-done', state === 'done');
    el.classList.toggle('st-live', state === 'live');
    var slot = el.querySelector('.nr'), chip = el.querySelector('.stt');
    if (state && slot) {
      if (!chip) {
        chip = document.createElement('i');
        chip.className = 'stt';
        slot.appendChild(chip);
      }
      if (chip.dataset.s !== state) {
        chip.dataset.s = state;
        chip.innerHTML = '<span class="zh" lang="zh-Hant">' + STATE[state].zh +
                         '</span><span class="en" lang="en">' + STATE[state].en + '</span>';
      }
    } else if (chip) {
      chip.remove();
    }
  });
}
markPast();
setInterval(markPast, 60000);
