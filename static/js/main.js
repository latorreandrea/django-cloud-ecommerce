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
});