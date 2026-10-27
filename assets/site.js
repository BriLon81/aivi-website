/* aivilabs.io — form handlers for the study request (/study/) and the
   findings signup (home page). Same pattern as report.html: validate, POST
   JSON with an AbortController timeout, show the result inline, and put the
   button back on failure. Each form carries a hidden "website" honeypot that
   real visitors leave empty; it is posted as-is and the service drops any
   submission that fills it. */
(function () {
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var STUDY_ENDPOINT = 'https://api.aivilabs.io/study/request';
  var FINDINGS_ENDPOINT = 'https://api.aivilabs.io/findings/signup';
  var TIMEOUT_MS = 15000;

  var okSvg = '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.4"/><path d="M6 10.2l2.6 2.6L14 7.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function value(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    return el ? String(el.value || '').trim() : '';
  }

  function wire(opts) {
    var form = document.getElementById(opts.formId);
    if (!form) return;
    var btn = form.querySelector('button[type=submit]');
    var errEl = form.querySelector('.form-error');
    var busy = false;
    function showErr(msg) { errEl.textContent = msg; errEl.style.display = 'block'; }
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (busy) return;
      errEl.style.display = 'none'; errEl.textContent = '';
      var payload = opts.build(form, showErr);
      if (!payload) return;

      busy = true;
      var label = btn.textContent;
      btn.disabled = true; btn.textContent = 'Sending…';
      var controller = new AbortController();
      var timer = setTimeout(function () { controller.abort(); }, TIMEOUT_MS);
      fetch(opts.endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload), signal: controller.signal
      }).then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json().catch(function () { return {}; });
      }).then(function () {
        clearTimeout(timer);
        form.innerHTML = '<div class="form-success" role="status">' + okSvg + '<div>' + opts.success + '</div></div>';
      }).catch(function (err) {
        clearTimeout(timer);
        if (window.console && console.error) console.error(opts.formId + ' failed:', err);
        busy = false; btn.disabled = false; btn.textContent = label;
        showErr('Something went wrong — please try again.');
      });
    });
  }

  // /study/ — {name, email, company, question, website} -> /study/request
  wire({
    formId: 'study-form',
    endpoint: STUDY_ENDPOINT,
    success: 'Thanks — we’ve got it. We’ll reply by email.',
    build: function (form, showErr) {
      var name = value(form, 'name');
      var email = value(form, 'email');
      var company = value(form, 'company');
      var question = value(form, 'question');
      if (!EMAIL_RE.test(email)) { showErr('Please enter a valid work email address.'); return null; }
      if (!company) { showErr('Please tell us your business or brand.'); return null; }
      if (!question) { showErr('Please tell us what you want to know.'); return null; }
      return { name: name, email: email, company: company, question: question, website: value(form, 'website') };
    }
  });

  // home — {email, consent_text, website} -> /findings/signup
  // consent_text is the exact wording shown under the field (the CASL record).
  wire({
    formId: 'findings-form',
    endpoint: FINDINGS_ENDPOINT,
    success: 'You’re on the list. We’ll email you when a study finds something new.',
    build: function (form, showErr) {
      var email = value(form, 'email');
      if (!EMAIL_RE.test(email)) { showErr('Please enter a valid email address.'); return null; }
      var consent = form.querySelector('#findings-consent');
      return { email: email, consent_text: consent ? consent.textContent.trim() : '', website: value(form, 'website') };
    }
  });
})();
