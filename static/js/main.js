/**
 * VoteSecure — Main JavaScript
 * Security: disables right-click + F12 during voting sessions.
 */

(function () {
  'use strict';

  const isVotingPage = window.location.pathname.includes('/votes/ballot/');

  if (isVotingPage) {
    document.addEventListener('contextmenu', function (e) {
      e.preventDefault();
      showSecurityWarning('Right-click is disabled during voting.');
      return false;
    });

    document.addEventListener('keydown', function (e) {
      const blockedKeys = ['F12'];
      const blockedCombos = [
        e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C'),
        e.ctrlKey && e.key === 'U',
        e.ctrlKey && e.key === 'S',
      ];
      if (blockedKeys.includes(e.key) || blockedCombos.some(Boolean)) {
        e.preventDefault();
        showSecurityWarning('Developer tools are disabled during voting for security.');
        return false;
      }
    });

    let devToolsWarned = false;
    setInterval(function () {
      const threshold = 160;
      const widthDiff = window.outerWidth - window.innerWidth > threshold;
      const heightDiff = window.outerHeight - window.innerHeight > threshold;
      if ((widthDiff || heightDiff) && !devToolsWarned) {
        devToolsWarned = true;
        showSecurityWarning('Developer tools detected. This activity has been logged.');
      }
    }, 2000);
  }

  function showSecurityWarning(msg) {
    let toast = document.getElementById('securityToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'securityToast';
      toast.setAttribute('role', 'alert');
      toast.style.cssText = `
        position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
        background: #B71C1C; color: #fff; padding: 12px 24px; border-radius: 8px;
        font-weight: 600; z-index: 9999; box-shadow: 0 8px 24px rgba(0,0,0,.3);
        max-width: 90vw; text-align: center; font-family: 'DM Sans', sans-serif; font-size: .9rem;
      `;
      document.body.appendChild(toast);
    }
    toast.textContent = '🔒 ' + msg;
    toast.style.display = 'block';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => { toast.style.display = 'none'; }, 4000);
  }

  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(100%)';
      alert.style.transition = 'all .4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 6000);
  });

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/static/js/sw.js').catch(function (err) {
        console.warn('Service Worker registration failed:', err);
      });
    });
  }

  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.textContent = 'Skip to main content';
  skipLink.className = 'skip-link';
  skipLink.style.cssText = `
    position: absolute; top: -40px; left: 0; background: #0D47A1;
    color: #fff; padding: 8px 16px; z-index: 9999; border-radius: 0 0 8px 0;
    font-weight: 600; transition: top .2s;
  `;
  skipLink.addEventListener('focus', () => { skipLink.style.top = '0'; });
  skipLink.addEventListener('blur', () => { skipLink.style.top = '-40px'; });
  document.body.insertBefore(skipLink, document.body.firstChild);

})();
