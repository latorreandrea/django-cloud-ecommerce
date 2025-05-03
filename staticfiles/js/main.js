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

    // Variant image preview (for product cards)
    const variantImages = document.querySelectorAll('.variant-image');
    variantImages.forEach(image => {
        image.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const newImageUrl = this.getAttribute('data-image-url');
            const mainImage = document.getElementById('main-image-' + productId);
            if (mainImage) {
                mainImage.setAttribute('src', newImageUrl);
            }
        });
    });
    
    // Toast notifications
    document.querySelectorAll('.toast').forEach(function(toastEl) {
        var toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();
    });
});