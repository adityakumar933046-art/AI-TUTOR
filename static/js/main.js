// EduVerse AI Kids - Client JavaScript

document.addEventListener('DOMContentLoaded', () => {
  // Theme Toggle Handler
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const currentTheme = localStorage.getItem('eduverse_theme') || 'light';
  
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateThemeIcon(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('eduverse_theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggleBtn) return;
    const icon = themeToggleBtn.querySelector('i');
    if (icon) {
      icon.className = theme === 'dark' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars-fill text-primary';
    }
  }

  // Password Strength Meter
  const passwordInput = document.getElementById('reg-password');
  const strengthMeter = document.getElementById('password-strength-bar');

  if (passwordInput && strengthMeter) {
    passwordInput.addEventListener('input', () => {
      const val = passwordInput.value;
      let score = 0;
      if (val.length >= 8) score += 25;
      if (/[A-Z]/.test(val)) score += 25;
      if (/[a-z]/.test(val)) score += 25;
      if (/[0-9]/.test(val) || /[^A-Za-z0-9]/.test(val)) score += 25;

      strengthMeter.style.width = score + '%';

      if (score <= 25) {
        strengthMeter.style.backgroundColor = '#ef4444';
      } else if (score <= 50) {
        strengthMeter.style.backgroundColor = '#f59e0b';
      } else if (score <= 75) {
        strengthMeter.style.backgroundColor = '#3b82f6';
      } else {
        strengthMeter.style.backgroundColor = '#10b981';
      }
    });
  }
});
