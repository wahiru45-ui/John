// 대기시간 계산 (cam.html · wait.html 같이 씀)
var WAIT_DEFAULT = { tables: 16, meal: 30, base: 10, per: 0.5, win: 15, empty: 90 };

function waitCfg(w) {
  var c = {}, k, src = (w && w.cfg) || {};
  for (k in WAIT_DEFAULT) c[k] = typeof src[k] === "number" ? src[k] : WAIT_DEFAULT[k];
  return c;
}

// 한국 시간 기준 홀 영업 여부 (11시~21시, 일요일 휴무)
function hallOpen(now) {
  var d = new Date(now + 9 * 3600e3), h = d.getUTCHours() + d.getUTCMinutes() / 60;
  return d.getUTCDay() !== 0 && h >= 11 && h < 21;
}

function calcWait(w, now) {
  w = w || {};
  var c = waitCfg(w), camsObj = w.cams || {}, cams = [], zones = [], k;
  for (k in camsObj) {
    var x = camsObj[k];
    if (x && x.at && now - x.at < 120000) { cams.push(x); (x.st || []).forEach(function (z) { zones.push(z); }); }
  }
  var free = zones.filter(function (z) { return !z.occ; }).length;
  var seat = null;
  if (zones.length) {
    if (free > 0) seat = 0;
    else {
      var left = zones.map(function (z) { return c.meal - (now - (z.since || now)) / 60000; });
      seat = Math.max(3, Math.round(Math.min.apply(null, left)));
    }
  }
  var dishes = w.food && now - w.food.at < 300000 ? w.food.dishes || 0 : 0;
  var food = Math.min(60, Math.round(c.base + dishes * c.per));
  var manual = w.manual && w.manual.until > now ? w.manual.min : null;
  var total = manual != null ? manual : (seat || 0) + food;
  var people = cams.reduce(function (s, x) { return s + (x.people || 0); }, 0);
  var level = total <= 15 ? "여유" : total <= 30 ? "보통" : "혼잡";
  return { cfg: c, cams: cams.length, zones: zones.length, free: free, seat: seat, food: food,
           dishes: dishes, manual: manual, total: total, people: people, level: level, open: hallOpen(now) };
}
