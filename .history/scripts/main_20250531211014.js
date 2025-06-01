document.addEventListener('DOMContentLoaded', function () {
  const animatedElements = document.querySelectorAll('.animate-on-scroll');

  if (!('IntersectionObserver' in window)) {
    // Fallback สำหรับ browser เก่า
    animatedElements.forEach(el => {
      const animation = el.getAttribute('data-animate') || 'animate__fadeInUp';
      el.classList.add('animate__animated', animation);
    });
    return;
  }

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      const el = entry.target;
      const animation = el.getAttribute('data-animate') || 'animate__fadeInUp';
      const delay = el.getAttribute('data-delay') || '0s';

      if (entry.isIntersecting) {
        el.classList.add('animate__animated', animation);
        el.style.setProperty('--animate-delay', delay);
        el.classList.add('animate__delay');
      } else {
        el.classList.remove('animate__animated', animation);
        el.classList.remove('animate__delay');
      }
    });
  }, {
    rootMargin: '0px 0px -10% 0px',
    threshold: 0.1
  });

  animatedElements.forEach(el => observer.observe(el));
});