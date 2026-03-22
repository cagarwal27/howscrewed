document.addEventListener('DOMContentLoaded', () => {

  // --- 1. Scroll Reveal Animation ---
  // Fade-in elements as they enter the viewport using IntersectionObserver.
  // Falls back to showing everything immediately if observer is unsupported.

  const revealElements = document.querySelectorAll('.scroll-reveal');

  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    revealElements.forEach(el => revealObserver.observe(el));
  } else {
    revealElements.forEach(el => el.classList.add('visible'));
  }

  // --- 2. Animated Money Counter ---
  // Counts from $0 to the data-target value over ~2s with cubic ease-out.

  const counter = document.getElementById('money-counter');

  if (counter) {
    const target = parseInt(counter.dataset.target, 10) || 0;
    let counted = false;

    const formatMoney = (n) =>
      '$' + Math.floor(n).toLocaleString('en-US');

    const animateCounter = () => {
      if (counted) return;
      counted = true;

      const duration = 2000;
      const start = performance.now();

      const tick = (now) => {
        const elapsed = Math.min(now - start, duration);
        const progress = elapsed / duration;
        // Cubic ease-out: fast start, gentle finish
        const eased = 1 - Math.pow(1 - progress, 3);

        counter.textContent = formatMoney(target * eased);

        if (elapsed < duration) {
          requestAnimationFrame(tick);
        } else {
          counter.textContent = formatMoney(target);
        }
      };

      requestAnimationFrame(tick);
    };

    if ('IntersectionObserver' in window) {
      const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            animateCounter();
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });

      counterObserver.observe(counter);
    } else {
      animateCounter();
    }
  }

  // --- 3. Smooth Scroll Fallback ---
  // Handles [data-scroll-to] clicks for browsers without CSS scroll-behavior.

  document.querySelectorAll('[data-scroll-to]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const targetEl = document.querySelector(btn.dataset.scrollTo);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

});
