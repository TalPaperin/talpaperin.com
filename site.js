/* Site-wide conversion layer. Loaded with defer on every page.
   1. Every Calendly link opens the booking popup in place, never a new tab (the widget loads
      on demand and falls back to the plain link only if it cannot load). The header
      "Let's Talk" button is NOT a Calendly link: it goes to the contact page.
   2. GA4 events: book_a_call (click), calendly_time_selected, calendly_booked + generate_lead
      (a completed booking), whatsapp_click, email_click, phone_click, newsletter_signup. */
(function () {
  var CAL_CSS = 'https://assets.calendly.com/assets/external/widget.css';
  var CAL_JS = 'https://assets.calendly.com/assets/external/widget.js';
  var state = 0, waiters = []; // 0 idle, 1 loading, 2 ready

  function ev(name, params) {
    try {
      var p = params || {};
      p.page_path = location.pathname;
      if (typeof gtag === 'function') gtag('event', name, p);
    } catch (e) {}
  }
  function ready() { return !!(window.Calendly && window.Calendly.initPopupWidget); }
  function settle(ok) {
    state = ok ? 2 : 0;
    var w = waiters; waiters = [];
    for (var i = 0; i < w.length; i++) w[i](ok);
  }
  function loadCal(cb) {
    if (ready()) { state = 2; if (cb) cb(true); return; }
    if (cb) waiters.push(cb);
    if (state === 1) return;
    state = 1;
    if (!document.querySelector('link[href="' + CAL_CSS + '"]')) {
      var l = document.createElement('link'); l.rel = 'stylesheet'; l.href = CAL_CSS;
      document.head.appendChild(l);
    }
    var s = document.querySelector('script[src="' + CAL_JS + '"]');
    if (!s) { s = document.createElement('script'); s.src = CAL_JS; s.async = true; document.head.appendChild(s); }
    s.addEventListener('load', function () { settle(true); });
    s.addEventListener('error', function () { settle(false); });
    var n = 0, t = setInterval(function () {
      if (ready()) { clearInterval(t); if (state !== 2) settle(true); }
      else if (++n > 80) clearInterval(t);
    }, 100);
  }
  function up(el, test) {
    while (el && el !== document) {
      if (el.tagName === 'A' && test(el.getAttribute('href') || '')) return el;
      el = el.parentNode;
    }
    return null;
  }
  function isCal(h) { return /^https?:\/\/(www\.)?calendly\.com\//.test(h); }
  function label(a) {
    var t = a.getAttribute('data-cta') || (a.textContent || '').replace(/\s+/g, ' ').trim() || a.getAttribute('aria-label') || '';
    return t.slice(0, 60);
  }

  // Warm the widget up as soon as a visitor shows intent, so the popup opens instantly.
  ['pointerover', 'touchstart', 'focusin'].forEach(function (t) {
    document.addEventListener(t, function (e) {
      if (state === 0 && up(e.target, isCal)) loadCal();
    }, { passive: true, capture: true });
  });

  document.addEventListener('click', function (e) {
    var a = up(e.target, isCal);
    if (a) {
      ev('book_a_call', { link_text: label(a) });
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      e.preventDefault();
      var href = a.href, done = false;
      var fallback = setTimeout(function () { if (!done) { done = true; location.href = href; } }, 3000);
      loadCal(function (ok) {
        if (done) return;
        done = true; clearTimeout(fallback);
        if (ok) { try { Calendly.initPopupWidget({ url: href }); return; } catch (x) {} }
        location.href = href;
      });
      return;
    }
    a = up(e.target, function (h) { return /^\/(he\/)?contact\/?$/.test(h); });
    if (a) { ev('lets_talk_click', { link_text: label(a) }); return; }
    a = up(e.target, function (h) { return /^https?:\/\/(wa\.me|api\.whatsapp\.com)\//.test(h); });
    if (a) { ev('whatsapp_click', { link_text: label(a) }); return; }
    a = up(e.target, function (h) { return h.indexOf('mailto:') === 0; });
    if (a) { ev('email_click', { link_text: label(a) }); return; }
    a = up(e.target, function (h) { return h.indexOf('tel:') === 0; });
    if (a) { ev('phone_click', {}); }
  });

  // Calendly posts these from the popup: this is the real conversion.
  window.addEventListener('message', function (e) {
    if (e.origin !== 'https://calendly.com') return;
    var d = e.data || {};
    if (d.event === 'calendly.date_and_time_selected') ev('calendly_time_selected', {});
    if (d.event === 'calendly.event_scheduled') {
      ev('calendly_booked', {});
      ev('generate_lead', { method: 'calendly' });
    }
  });

  // Phones: keep the WhatsApp bubble off the first screen so it never covers the opening copy.
  var wa = document.querySelector('.wa-float');
  if (wa && window.matchMedia && matchMedia('(max-width:680px)').matches) {
    var show = function () {
      var on = window.scrollY > 320;
      wa.style.opacity = on ? '' : '0';
      wa.style.pointerEvents = on ? '' : 'none';
    };
    wa.style.transition = 'opacity .25s';
    show();
    window.addEventListener('scroll', show, { passive: true });
  }

  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f && f.classList && f.classList.contains('sub-form')) ev('newsletter_signup', {});
  }, true);
})();
