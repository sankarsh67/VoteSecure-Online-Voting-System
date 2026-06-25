/**
 * VoteSecure — Dark Mode Toggle
 * Saves preference to localStorage, applies before page render.
 */

(function () {
  'use strict';

  const savedTheme = localStorage.getItem('vs_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);

  function toggleDarkMode() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('vs_theme', next);
    const btn = document.getElementById('darkModeBtn');
    if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
  }

  window.toggleDarkMode = toggleDarkMode;

  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('darkModeBtn');
    if (btn) btn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
  });

})();
