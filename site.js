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

  // WhatsApp: prefilled message, and on desktop a small label with an honest status by Israel time.
  // Tal is on WhatsApp about 19 hours a day (Tal, 2026-11-11), so there is no hours limit and no
  // "night" state. The only offline window is Friday 15:00 to Saturday 21:00 Israel time.
  // No reply-time number is shown.
  if (wa) {
    var he = (document.documentElement.getAttribute('lang') || '').indexOf('he') === 0;
    var T = he ? {
      msg: 'היי טל, הגעתי דרך האתר ואשמח לדבר.', page: 'עמוד',
      title: 'כתבו לטל בוואטסאפ', close: 'סגירה',
      on: 'אני זמין בוואטסאפ רוב שעות היממה ועונה אישית.',
      off: 'אני לא זמין עד מוצאי שבת. השאירו הודעה ואענה אז.'
    } : {
      msg: 'Hi Tal, I found your site and want to talk.', page: 'Page',
      title: 'Message Tal on WhatsApp', close: 'Close',
      on: "I'm on WhatsApp most of the day and reply personally.",
      off: "I'm offline until Saturday night, Israel time. Leave a message and I reply then."
    };
    var href = 'https://wa.me/972545308119?text=' + encodeURIComponent(T.msg + ' (' + T.page + ': ' + location.pathname + ')');
    wa.setAttribute('href', href);

    var status = 'on';
    try {
      var parts = new Intl.DateTimeFormat('en-US', { timeZone: 'Asia/Jerusalem', weekday: 'short', hour: 'numeric', hour12: false }).formatToParts(new Date());
      var day = '', hour = 0;
      for (var i = 0; i < parts.length; i++) {
        if (parts[i].type === 'weekday') day = parts[i].value;
        if (parts[i].type === 'hour') hour = parseInt(parts[i].value, 10) % 24;
      }
      if ((day === 'Fri' && hour >= 15) || (day === 'Sat' && hour < 21)) status = 'off';
    } catch (x) { status = ''; }

    var dismissed = false;
    try { dismissed = sessionStorage.getItem('wa_label_off') === '1'; } catch (x) {}
    if (!dismissed && window.matchMedia && matchMedia('(min-width:900px) and (hover:hover)').matches) {
      var box = document.createElement('div');
      box.className = 'wa-label';
      var link = document.createElement('a');
      link.href = href; link.target = '_blank'; link.rel = 'noopener';
      link.setAttribute('data-cta', 'wa-label');
      var b = document.createElement('b'); b.textContent = T.title; link.appendChild(b);
      if (status) { var sp = document.createElement('span'); sp.textContent = T[status]; link.appendChild(sp); }
      var x = document.createElement('button');
      x.type = 'button'; x.setAttribute('aria-label', T.close); x.textContent = '×';
      x.addEventListener('click', function () {
        box.parentNode.removeChild(box);
        try { sessionStorage.setItem('wa_label_off', '1'); } catch (e) {}
      });
      box.appendChild(link); box.appendChild(x);
      document.body.appendChild(box);
      var place = function () {
        var nearEnd = window.innerHeight + window.scrollY > document.documentElement.scrollHeight - 220;
        box.classList.toggle('on', !nearEnd);
      };
      setTimeout(function () { place(); window.addEventListener('scroll', place, { passive: true }); }, 1500);
    }
  }

  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f && f.classList && f.classList.contains('sub-form')) ev('newsletter_signup', {});
  }, true);
})();
