// Interactive quote builder for /pricing. No backend: live total, download, and
// a pre-filled email to Tal. Bilingual (reads labels straight from the DOM).
(function () {
  var calc = document.querySelector('.quote-calc');
  if (!calc) return;
  var cro = calc.querySelector('.qc-cro');
  var sdr = calc.querySelector('.qc-sdr');
  var mk = calc.querySelector('.qc-mk');
  var amount = calc.querySelector('.qc-amount');
  var perLabel = amount ? (amount.querySelector('span') ? amount.querySelector('span').textContent : '/mo') : '/mo';
  var dl = calc.querySelector('.qc-download');
  var mailBtn = calc.querySelector('.qc-email-btn');
  var subject = calc.getAttribute('data-subject') || 'Quote request';

  function sdrPrice(n) {
    n = parseInt(n || 0, 10);
    if (isNaN(n) || n <= 0) return 0;
    var r1 = +sdr.dataset.r1, r2 = +sdr.dataset.r2, r3 = +sdr.dataset.r3;
    if (n === 1) return r1;
    if (n === 2) return r2;
    return n * r3;
  }
  function total() {
    return (+cro.value || 0) + sdrPrice(sdr.value) + (+mk.value || 0);
  }
  function money(n) { return '$' + n.toLocaleString('en-US'); }

  function quoteText() {
    var lines = ['Quote from talpaperin.com', ''];
    if (+cro.value) lines.push('Fractional CRO: ' + cro.options[cro.selectedIndex].text);
    var n = parseInt(sdr.value || 0, 10);
    if (n > 0) lines.push('SDRs: ' + n + ' rep' + (n > 1 ? 's' : '') + ' (' + money(sdrPrice(n)) + '/mo)');
    if (+mk.value) lines.push('Marketing: ' + mk.options[mk.selectedIndex].text);
    lines.push('', 'Estimated monthly total: ' + money(total()) + '/mo');
    var name = (calc.querySelector('.qc-name') || {}).value || '';
    var email = (calc.querySelector('.qc-email') || {}).value || '';
    var company = (calc.querySelector('.qc-company') || {}).value || '';
    if (name || email || company) {
      lines.push('', '---');
      if (name) lines.push('Name: ' + name);
      if (email) lines.push('Email: ' + email);
      if (company) lines.push('Company: ' + company);
    }
    return lines.join('\n');
  }

  function refresh() {
    if (amount) amount.innerHTML = money(total()) + '<span>' + perLabel + '</span>';
    if (mailBtn) {
      mailBtn.setAttribute('href',
        'mailto:tal@ksw.solutions?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(quoteText()));
    }
  }

  [cro, sdr, mk].forEach(function (el) {
    if (el) { el.addEventListener('change', refresh); el.addEventListener('input', refresh); }
  });
  ['.qc-name', '.qc-email', '.qc-company'].forEach(function (sel) {
    var el = calc.querySelector(sel);
    if (el) el.addEventListener('input', refresh);
  });

  if (dl) {
    dl.addEventListener('click', function () {
      var blob = new Blob([quoteText()], { type: 'text/plain' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url; a.download = 'talpaperin-quote.txt';
      document.body.appendChild(a); a.click();
      document.body.removeChild(a); URL.revokeObjectURL(url);
      try { gtag('event', 'quote_download'); } catch (e) {}
    });
  }
  if (mailBtn) {
    mailBtn.addEventListener('click', function () { try { gtag('event', 'quote_email'); } catch (e) {} });
  }
  refresh();
})();
