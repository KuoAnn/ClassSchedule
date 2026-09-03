// 03-status.js — 標記今天，並依現在時間標出結束／進行中
(function(){
  var td = (new Date().getDay() + 6) % 7;
  document.querySelectorAll('[data-day="' + td + '"]').forEach(function(el){
    el.classList.add('today');
  });
})();
// 當天課程三種狀態：已結束（反灰淡化）／進行中（只留 live-pulse 圖示）／待開課（不標）
var STATE = {
  done: {zh: '結束', en: 'Ended'},
  live: {zh: '進行中', en: 'Live'}
};
function axisY(minuteOfDay){
  var ax = window.SCHEDULE && window.SCHEDULE.axis;
  if (!ax || !ax.length) return null;
  var last = ax[ax.length - 1];
  if (minuteOfDay === last.m) return last.y;
  if (minuteOfDay < ax[0].m || minuteOfDay > last.m) return null;
  for (var i = 1; i < ax.length; i++) {
    var a = ax[i - 1], b = ax[i];
    if (minuteOfDay > b.m) continue;
    if (b.m === a.m) return b.y;
    return a.y + (minuteOfDay - a.m) * (b.y - a.y) / (b.m - a.m);
  }
  return null;
}
function updateNowLine(td, now){
  var root = document.documentElement;
  var sheet = document.getElementById('sheet');
  var cols = document.querySelectorAll('.cols .col');
  for (var i = 0; i < cols.length; i++) {
    var old = cols[i].querySelector('.nowline');
    if (old) old.style.display = 'none';
  }
  if (root.classList.contains('nv') || !sheet || sheet.classList.contains('flat')) return;
  var col = document.querySelector('.cols .col[data-day="' + td + '"]');
  if (!col) return;
  var evs = col.querySelectorAll('.ev[data-start][data-end]');
  if (!evs.length) return;
  var inClass = false;
  for (var j = 0; j < evs.length; j++) {
    var st = +evs[j].dataset.start, en = +evs[j].dataset.end;
    if (now >= st && now < en) { inClass = true; break; }
  }
  if (!inClass) return;
  var y = axisY(now);
  if (y === null) return;
  var line = col.querySelector('.nowline');
  if (!line) {
    line = document.createElement('i');
    line.className = 'nowline';
    line.setAttribute('aria-hidden', 'true');
    col.appendChild(line);
  }
  line.style.top = y + 'px';
  line.style.display = '';
}
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
        if (state === 'live') {
          chip.innerHTML = '';
          chip.setAttribute('aria-label', STATE[state].zh + ' ' + STATE[state].en);
        } else {
          chip.removeAttribute('aria-label');
          chip.innerHTML = '<span class="zh" lang="zh-Hant">' + STATE[state].zh +
                           '</span><span class="en" lang="en">' + STATE[state].en + '</span>';
        }
      }
    } else if (chip) {
      chip.remove();
    }
  });
  updateNowLine(td, now);
}
markPast();
setInterval(markPast, 60000);
