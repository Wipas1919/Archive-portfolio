/* -------------------  Scroll-animation (เดิม) ------------------- */
document.addEventListener('DOMContentLoaded', () => {
  const animatedElements = document.querySelectorAll('.animate-on-scroll');

  if (!('IntersectionObserver' in window)) {
    animatedElements.forEach(el => {
      const animation = el.dataset.animate || 'animate__fadeInUp';
      el.classList.add('animate__animated', animation);
    });
    return;
  }

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      const el       = entry.target;
      const anim     = el.dataset.animate || 'animate__fadeInUp';
      const delay    = el.dataset.delay   || '0s';

      if (entry.isIntersecting) {
        el.classList.add('animate__animated', anim);
        el.style.setProperty('--animate-delay', delay);
        el.classList.add('animate__delay');
      } else {
        el.classList.remove('animate__animated', anim, 'animate__delay');
      }
    });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });

  animatedElements.forEach(el => observer.observe(el));
});

/* -------------------  เพิ่มส่วนแสดง Project Blog ------------------- */
function renderProject(blogJson) {
  const container = document.getElementById('proj-content'); // <div id="proj-content"></div>
  container.innerHTML = '';

  blogJson.content.forEach(block => {
    if (block.type === 'text') {
      const p = document.createElement('p');
      p.innerHTML = block.value;              // ใช้ innerHTML เพื่อ render <strong> ฯลฯ

      /* ✅ ถ้ามี key indent:true หรือ class:"indent" ก็ใส่ class เพื่อเยื้องเฉพาะย่อหน้า */
      if (block.indent || block.class === 'indent') p.classList.add('indent');

      container.appendChild(p);
    }
    if (block.type === 'image') {
      const img = document.createElement('img');
      img.src = block.value;
      img.alt = block.caption || '';
      container.appendChild(img);
    }
  });
}

/* ตัวอย่างโหลด JSON */
fetch('../data/project-details.json')
  .then(r => r.json())
  .then(json => renderProject(json['End-to-End Data Engineering Journey']))
  .catch(console.error);
