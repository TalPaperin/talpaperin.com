// Outcomes-based quote builder for /pricing. No backend: answer questions ->
// recommended package, monthly outcome + cost, a branded printable quote, and a
// pre-filled email to Tal. Bilingual (all strings come from data attributes).
(function () {
  var calc = document.querySelector('.quote-calc');
  if (!calc) return;

  var tiers = JSON.parse(calc.getAttribute('data-tiers') || '[]');
  var L = JSON.parse(calc.getAttribute('data-labels') || '{}');
  var subject = calc.getAttribute('data-subject') || 'Quote request';
  var R1 = +calc.getAttribute('data-sdr-r1'), R2 = +calc.getAttribute('data-sdr-r2'), R3 = +calc.getAttribute('data-sdr-r3');
  var repsQ = calc.querySelector('.qc-q-reps');
  var result = calc.querySelector('.qc-result');
  var isHe = L.lang === 'he';

  var st = { tier: null, sdr: 0, reps: 1, mk: 0, mkname: '', mkout: '' };

  function money(n) { return '$' + (n || 0).toLocaleString('en-US'); }
  function sdrPrice(n) { n = +n || 0; if (n <= 0) return 0; if (n === 1) return R1; if (n === 2) return R2; return n * R3; }
  function repsLabel(n) { return n >= 3 ? '3+' : String(n); }
  function cost() { return (st.tier != null ? tiers[st.tier].price : 0) + (st.sdr ? sdrPrice(st.reps) : 0) + (+st.mk || 0); }

  function outcomeLines() {
    var out = [];
    if (st.tier != null) out.push(tiers[st.tier].outcome);
    if (st.sdr) out.push(L.sdr_outcome.replace('{n}', repsLabel(st.reps)).replace('{s}', st.reps > 1 ? 's' : ''));
    if (st.mk && st.mkout) out.push(st.mkout);
    return out;
  }
  function lineItems() {
    var items = [];
    if (st.tier != null) items.push([tiers[st.tier].name + ' (' + tiers[st.tier].commit + ')', tiers[st.tier].price]);
    if (st.sdr) items.push(['SDR team (' + repsLabel(st.reps) + ' rep' + (st.reps > 1 ? 's' : '') + ')', sdrPrice(st.reps)]);
    if (st.mk) items.push([st.mkname, +st.mk]);
    return items;
  }

  function renderResult() {
    if (st.tier == null) { result.innerHTML = '<p class="qc-prompt">' + L.prompt + '</p>'; return; }
    var bullets = outcomeLines().map(function (t) { return '<li>' + t + '</li>'; }).join('');
    result.innerHTML =
      '<div class="qc-rec-label">' + L.recommended + '</div>' +
      '<div class="qc-rec-name">' + tiers[st.tier].name + '</div>' +
      '<div class="qc-sub-h">' + L.outcome_h + '</div>' +
      '<ul class="qc-out">' + bullets + '</ul>' +
      '<div class="qc-sub-h">' + L.cost_h + '</div>' +
      '<div class="qc-cost">' + money(cost()) + '<span>' + L.mo + '</span></div>';
    var m = calc.querySelector('.qc-email-btn');
    if (m) m.setAttribute('href', 'mailto:tal@ksw.solutions?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(emailBody()));
  }

  function emailBody() {
    var lines = [L.quote_title + ' — talpaperin.com', ''];
    if (st.tier != null) lines.push(L.recommended + ': ' + tiers[st.tier].name);
    lines.push('', L.outcome_h + ':');
    outcomeLines().forEach(function (t) { lines.push('- ' + t); });
    lines.push('', L.cost_h + ': ' + money(cost()) + L.mo);
    var name = val('.qc-name'), email = val('.qc-email'), company = val('.qc-company');
    if (name || email || company) {
      lines.push('', '---');
      if (name) lines.push('Name: ' + name);
      if (email) lines.push('Email: ' + email);
      if (company) lines.push('Company: ' + company);
    }
    return lines.join('\n');
  }
  function val(sel) { var e = calc.querySelector(sel); return e ? e.value : ''; }

  // chip selection
  calc.querySelectorAll('.qc-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var set = chip.getAttribute('data-set');
      calc.querySelectorAll('.qc-chip[data-set="' + set + '"]').forEach(function (c) { c.classList.remove('sel'); });
      chip.classList.add('sel');
      if (set === 'tier') st.tier = +chip.getAttribute('data-tier');
      else if (set === 'team') {
        st.sdr = +chip.getAttribute('data-sdr');
        if (st.sdr) {
          if (repsQ) repsQ.classList.add('show');
          var sel = calc.querySelector('.qc-chip[data-set="reps"].sel');
          if (!sel) { var first = calc.querySelector('.qc-chip[data-set="reps"]'); if (first) { first.classList.add('sel'); st.reps = +first.getAttribute('data-reps'); } }
        } else { if (repsQ) repsQ.classList.remove('show'); }
      } else if (set === 'reps') st.reps = +chip.getAttribute('data-reps');
      else if (set === 'mk') { st.mk = +chip.getAttribute('data-mk'); st.mkname = chip.getAttribute('data-mkname') || ''; st.mkout = chip.getAttribute('data-mkout') || ''; }
      renderResult();
    });
  });
  ['.qc-name', '.qc-email', '.qc-company'].forEach(function (s) { var e = calc.querySelector(s); if (e) e.addEventListener('input', renderResult); });

  // branded printable quote
  function printQuote() {
    if (st.tier == null) { alert(L.prompt); return; }
    var dir = L.dir || 'ltr';
    var dateStr = new Date().toLocaleDateString(isHe ? 'he-IL' : 'en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    var rows = lineItems().map(function (it) {
      return '<tr><td>' + it[0] + '</td><td class="p">' + money(it[1]) + L.mo + '</td></tr>';
    }).join('');
    var bullets = outcomeLines().map(function (t) { return '<li>' + t + '</li>'; }).join('');
    var name = val('.qc-name'), email = val('.qc-email'), company = val('.qc-company');
    var who = [name, company, email].filter(Boolean).join(' · ');
    var css = 'body{font-family:Arial,Helvetica,sans-serif;color:#0b0f14;margin:0;padding:40px;background:#fff}' +
      '.q{max-width:640px;margin:0 auto}' +
      '.brand{font-weight:800;font-size:30px;letter-spacing:1px;color:#0b0f14}' +
      '.tag{color:#2563EB;font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:1px;margin-top:2px}' +
      '.bar{height:4px;background:#2563EB;border-radius:3px;margin:16px 0 24px}' +
      'h1{font-size:22px;margin:0 0 4px}.muted{color:#667;font-size:13px}' +
      '.who{margin:14px 0;font-size:14px}' +
      '.rec{margin:22px 0 6px;font-size:12px;color:#2563EB;font-weight:700;text-transform:uppercase;letter-spacing:1px}' +
      '.recn{font-size:24px;font-weight:800;margin:0 0 14px}' +
      'h3{font-size:13px;text-transform:uppercase;letter-spacing:.5px;color:#556;margin:20px 0 8px}' +
      'ul{margin:0;padding-inline-start:20px}li{margin:6px 0;font-size:14px}' +
      'table{width:100%;border-collapse:collapse;margin-top:8px;font-size:14px}' +
      'td{padding:10px 0;border-bottom:1px solid #e5e8ee}.p{text-align:end;font-weight:700;white-space:nowrap}' +
      '.total td{border-top:2px solid #0b0f14;border-bottom:none;font-size:18px;font-weight:800;padding-top:12px}' +
      '.terms{color:#667;font-size:12px;margin-top:22px}' +
      '.foot{margin-top:20px;font-size:14px}.foot a{color:#2563EB}' +
      '@media print{.noprint{display:none}}' +
      '.noprint{margin-top:26px}.pbtn{background:#2563EB;color:#fff;border:0;border-radius:8px;padding:12px 20px;font-size:15px;font-weight:700;cursor:pointer}';
    var html = '<!doctype html><html lang="' + (L.lang || 'en') + '" dir="' + dir + '"><head><meta charset="utf-8">' +
      '<title>' + L.quote_title + ' — Tal Paperin</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>' + css + '</style></head><body><div class="q">' +
      '<div class="brand">' + (L.brand || 'TAL PAPERIN') + '</div><div class="tag">' + (L.tagline || '') + '</div><div class="bar"></div>' +
      '<h1>' + L.quote_title + '</h1><div class="muted">' + dateStr + '</div>' +
      (who ? '<div class="who">' + who + '</div>' : '') +
      '<div class="rec">' + L.recommended + '</div><div class="recn">' + tiers[st.tier].name + '</div>' +
      '<h3>' + L.outcome_h + '</h3><ul>' + bullets + '</ul>' +
      '<table>' + rows + '<tr class="total"><td>' + L.cost_h + '</td><td class="p">' + money(cost()) + L.mo + '</td></tr></table>' +
      '<p class="terms">' + L.terms + '</p>' +
      '<div class="foot">' + L.book + ': <a href="' + L.book_url + '">' + L.book_url + '</a> · <a href="mailto:tal@ksw.solutions">tal@ksw.solutions</a></div>' +
      '<div class="noprint"><button class="pbtn" onclick="window.print()">' + L.print + '</button></div>' +
      '</div></body></html>';
    var w = window.open('', '_blank');
    if (!w) return;
    w.document.open(); w.document.write(html); w.document.close();
    w.focus();
    setTimeout(function () { try { w.print(); } catch (e) {} }, 400);
    try { gtag('event', 'quote_download'); } catch (e) {}
  }

  var dl = calc.querySelector('.qc-download');
  if (dl) dl.addEventListener('click', printQuote);
  var mb = calc.querySelector('.qc-email-btn');
  if (mb) mb.addEventListener('click', function () { try { gtag('event', 'quote_email'); } catch (e) {} });

  renderResult();
})();
