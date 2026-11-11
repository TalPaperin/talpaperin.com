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

  var wa = document.querySelector('.wa-float');

  // WhatsApp: the bubble is visible from the first screen on every device. Prefilled message, plus a
  // small label with an honest status by Israel time (stays on desktop, shows once and folds on phones).
  // Tal is on WhatsApp about 19 hours a day (Tal, 2026-11-11), so there is no hours limit and no
  // "night" state. The only offline window is Friday 15:00 to Saturday 21:00 Israel time.
  // No reply-time number is shown.
  if (wa) {
    var he = (document.documentElement.getAttribute('lang') || '').indexOf('he') === 0;
    var T = he ? {
      msg: 'היי טל, הגעתי דרך האתר ואשמח לדבר.', page: 'הייתי בעמוד',
      names: { pricing: 'תמחור', contact: 'צור קשר', about: 'אודות', 'case-studies': 'מקרי מבחן', recommendations: 'המלצות', services: 'שירותים', guides: 'מדריכים', answers: 'תשובות', blog: 'בלוג', 'sales-cost-calculator': 'מחשבון עלות המכירות', privacy: 'פרטיות', challenges: 'אתגרים' },
      title: 'כתבו לטל בוואטסאפ', close: 'סגירה',
      on: 'אני זמין בוואטסאפ רוב שעות היממה ועונה אישית.',
      off: 'אני לא זמין עד מוצאי שבת. השאירו הודעה ואענה אז.'
    } : {
      msg: 'Hi Tal, I found your site and want to talk.', page: 'I was on',
      names: { pricing: 'Pricing', contact: 'Contact', about: 'About', 'case-studies': 'Case Studies', recommendations: 'Recommendations', services: 'Services', guides: 'Guides', answers: 'Answers', blog: 'Blog', 'sales-cost-calculator': 'Sales cost calculator', privacy: 'Privacy' },
      title: 'Message Tal on WhatsApp', close: 'Close',
      on: "I'm on WhatsApp most of the day and reply personally.",
      off: "I'm offline until Saturday night, Israel time. Leave a message and I reply then."
    };
    // A readable page name, never a raw path. The homepage gets the plain message.
    var segs = location.pathname.replace(/\/+$/, '').split('/').filter(function (p) { return p && p !== 'he'; });
    var pageName = '';
    if (segs.length === 1 && T.names[segs[0]]) pageName = T.names[segs[0]];
    else if (segs.length) {
      var h1 = document.querySelector('h1');
      pageName = h1 ? (h1.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 70) : '';
    }
    var href = 'https://wa.me/972545308119?text=' + encodeURIComponent(T.msg + (pageName ? ' (' + T.page + ': ' + pageName + ')' : ''));
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
    var small = !(window.matchMedia && matchMedia('(min-width:900px) and (hover:hover)').matches);
    var seen = false;
    try { seen = sessionStorage.getItem('wa_label_seen') === '1'; } catch (x) {}
    if (!dismissed && !(small && seen)) {
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
      var expired = false;
      var place = function () {
        var nearEnd = window.innerHeight + window.scrollY > document.documentElement.scrollHeight - 220;
        box.classList.toggle('on', !nearEnd && !expired);
      };
      setTimeout(function () { place(); window.addEventListener('scroll', place, { passive: true }); }, 1200);
      if (small) {
        // Phones: the bubble is always there; the label shows once per visit, then folds away.
        try { sessionStorage.setItem('wa_label_seen', '1'); } catch (e) {}
        setTimeout(function () { expired = true; place(); }, 9200);
      }
    }
  }

  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f && f.classList && f.classList.contains('sub-form')) ev('newsletter_signup', {});
  }, true);

  // Fold-out sections (pricing page): a link to #id opens the <details> it points at.
  function openTarget() {
    var id = (location.hash || '').slice(1);
    if (!id) return;
    var el = null;
    try { el = document.getElementById(decodeURIComponent(id)); } catch (x) {}
    if (el && el.tagName === 'DETAILS' && !el.open) { el.open = true; el.scrollIntoView(); }
  }
  window.addEventListener('hashchange', openTarget);
  openTarget();
  document.addEventListener('click', function (e) {
    var a = up(e.target, function (h) { return h.charAt(0) === '#' && h.length > 1; });
    if (!a) return;
    var el = document.getElementById(a.getAttribute('href').slice(1));
    if (el && el.tagName === 'DETAILS') el.open = true;
  });

  // Cookie consent, Europe only. The head snippet sets Google Consent Mode defaults: analytics
  // cookies are denied for EEA, UK and Swiss visitors until they accept here. Everyone else sees
  // no banner. The choice is kept in localStorage ('tp_consent' = yes | no) and can be reopened
  // from any link marked data-consent-reset (the privacy page has one).
  // LinkedIn Insight Tag: paste the partner ID from Campaign Manager below to switch it on.
  // It loads straight away outside Europe and only after "OK" inside Europe.
  // An ad ACCOUNT id is not a partner id: do not put one here.
  var LI_PARTNER_ID = '';
  var heLang = (document.documentElement.getAttribute('lang') || '').indexOf('he') === 0;
  function inEurope() {
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
      return /^(Europe|Arctic)\//.test(tz) || /^Atlantic\/(Reykjavik|Canary|Madeira|Azores|Faroe)$/.test(tz) ||
        /^Asia\/(Nicosia|Famagusta)$/.test(tz);
    } catch (x) { return false; }
  }
  function getConsent() { try { return localStorage.getItem('tp_consent'); } catch (x) { return null; } }
  function loadLinkedIn() {
    if (!LI_PARTNER_ID || window._linkedin_partner_id) return;
    window._linkedin_partner_id = LI_PARTNER_ID;
    window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
    window._linkedin_data_partner_ids.push(LI_PARTNER_ID);
    if (!window.lintrk) { window.lintrk = function (a, b) { window.lintrk.q.push([a, b]); }; window.lintrk.q = []; }
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://snap.licdn.com/li.lms-analytics/insight.min.js';
    document.head.appendChild(s);
  }
  function setConsent(v) {
    try { localStorage.setItem('tp_consent', v); } catch (x) {}
    var g = v === 'yes' ? 'granted' : 'denied';
    try { gtag('consent', 'update', { analytics_storage: g, ad_storage: g, ad_user_data: g, ad_personalization: g }); } catch (x) {}
    if (v === 'yes') loadLinkedIn();
  }
  function showConsent() {
    if (document.querySelector('.consent')) return;
    var C = heLang ? {
      t: 'עוגיות: אני משתמש באנליטיקה כדי לראות אילו עמודים מועילים' + (LI_PARTNER_ID ? ', וב-LinkedIn כדי למדוד את הפרסום שלי' : '') + '. אפשר לספור את הביקור שלכם?',
      yes: 'אישור', no: 'לא תודה', more: 'פרטיות', href: '/he/privacy', label: 'הסכמה לעוגיות'
    } : {
      t: 'Cookies: I use analytics to see which pages are useful' + (LI_PARTNER_ID ? ', and LinkedIn to measure my ads' : '') + '. OK to count your visit?',
      yes: 'OK', no: 'No thanks', more: 'Privacy', href: '/privacy', label: 'Cookie consent'
    };
    var box = document.createElement('div');
    box.className = 'consent'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', C.label);
    var p = document.createElement('p'); p.appendChild(document.createTextNode(C.t + ' '));
    var more = document.createElement('a'); more.href = C.href; more.textContent = C.more; p.appendChild(more);
    var row = document.createElement('div'); row.className = 'consent-btns';
    [['yes', C.yes], ['no', C.no]].forEach(function (o) {
      var b = document.createElement('button'); b.type = 'button'; b.className = o[0]; b.textContent = o[1];
      b.addEventListener('click', function () { setConsent(o[0]); box.parentNode.removeChild(box); });
      row.appendChild(b);
    });
    box.appendChild(p); box.appendChild(row);
    document.body.appendChild(box);
  }
  var eu = inEurope(), choice = getConsent();
  if (!eu || choice === 'yes') loadLinkedIn();
  if (eu && !choice) showConsent();
  document.addEventListener('click', function (e) {
    var el = e.target;
    while (el && el !== document) {
      if (el.hasAttribute && el.hasAttribute('data-consent-reset')) { e.preventDefault(); showConsent(); return; }
      el = el.parentNode;
    }
  });
})();
