document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('scrollToTopBtn');
    const navbar = document.querySelector('.navbar');

    function checkNavbar() {
        if (!navbar || !btn) return;
        const rect = navbar.getBoundingClientRect();
        // Se la navbar è fuori dallo schermo in alto, mostra il bottone
        if (rect.bottom < 0) {
            btn.style.display = 'block';
        } else {
            btn.style.display = 'none';
        }
    }

    window.addEventListener('scroll', checkNavbar);

    if (btn) {
        btn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }


    // Fade-in on scroll for cards
    const fadeEls = document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        fadeEls.forEach(el => observer.observe(el));
    } else {
        // Fallback: show all if IntersectionObserver not supported
        fadeEls.forEach(el => el.classList.add('visible'));
    }
});