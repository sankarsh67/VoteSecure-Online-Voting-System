/**
 * VoteSecure — Session Timer (FIXED VERSION)
 * Counts down 5-minute inactivity timeout.
 * Resets on user activity. Warns at 30s, auto-redirects at 0.
 * FIX: Removed the buggy AJAX check that was causing premature logout
 * (it was hitting /accounts/login/ which always redirects for logged-in users).
 */

(function () {
  'use strict';

  const SESSION_DURATION = 300; // 5 minutes — match Django SESSION_COOKIE_AGE
  const WARN_AT = 30;

  let remaining = SESSION_DURATION;
  let timerInterval = null;
  const timerEl = document.getElementById('sessionTimer');

  function formatTime(secs) {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `⏱ ${m}:${s.toString().padStart(2, '0')}`;
  }

  function updateDisplay() {
    if (!timerEl) return;
    timerEl.textContent = formatTime(remaining);
    timerEl.classList.remove('warning', 'danger');
    if (remaining <= WARN_AT && remaining > 10) timerEl.classList.add('warning');
    if (remaining <= 10) timerEl.classList.add('danger');
  }

  function resetTimer() {
    remaining = SESSION_DURATION;
    updateDisplay();
  }

  function tick() {
    if (remaining <= 0) {
      clearInterval(timerInterval);
      window.location.href = '/accounts/login/?timeout=1';
      return;
    }
    remaining--;
    updateDisplay();
  }

  const RESET_EVENTS = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll', 'click'];
  RESET_EVENTS.forEach(function (evt) {
    document.addEventListener(evt, resetTimer, { passive: true });
  });

  timerInterval = setInterval(tick, 1000);
  updateDisplay();

  // FIXED: Use a safe API endpoint instead of /accounts/login/ which
  // always redirects authenticated users and caused false session-expiry.
  setInterval(async function () {
    try {
      const res = await fetch('/api/turnout/', {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      if (res.status === 401) {
        window.location.href = '/accounts/login/?timeout=1';
      }
    } catch (_) { /* network error — ignore */ }
  }, 60000); // check every 60s

})();
