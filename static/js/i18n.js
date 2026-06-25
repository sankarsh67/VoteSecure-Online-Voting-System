/**
 * VoteSecure — Internationalization (i18n)
 * Supports: English (en) and Hindi (hi)
 */

const TRANSLATIONS = {
  en: {
    'nav.logout': 'Logout',
    'footer.rights': '© 2024 VoteSecure Election Commission. All rights reserved.',
    'login.title': 'Secure Login',
    'login.email': 'Email Address',
    'login.password': 'Password',
    'otp.title': 'Enter OTP',
    'otp.label': 'One-Time Password',
    'ballot.cast_btn': 'Review & Cast Vote',
    'thanks.title': 'Your Vote Has Been Recorded!',
  },
  hi: {
    'nav.logout': 'लॉग आउट',
    'footer.rights': '© 2024 वोटसिक्योर चुनाव आयोग। सर्वाधिकार सुरक्षित।',
    'login.title': 'सुरक्षित लॉगिन',
    'login.email': 'ईमेल पता',
    'login.password': 'पासवर्ड',
    'otp.title': 'OTP दर्ज करें',
    'otp.label': 'वन-टाइम पासवर्ड',
    'ballot.cast_btn': 'समीक्षा करें और वोट डालें',
    'thanks.title': 'आपका वोट दर्ज हो गया है!',
  }
};

let currentLang = localStorage.getItem('vs_lang') || 'en';

function applyTranslations(lang) {
  currentLang = lang;
  localStorage.setItem('vs_lang', lang);
  const t = TRANSLATIONS[lang] || TRANSLATIONS.en;
  document.querySelectorAll('[data-i18n]').forEach(function (el) {
    const key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });
  const select = document.getElementById('langToggle');
  if (select) select.value = lang;
  document.documentElement.lang = lang;
}

function toggleLanguage(lang) { applyTranslations(lang); }

document.addEventListener('DOMContentLoaded', function () {
  applyTranslations(currentLang);
});
