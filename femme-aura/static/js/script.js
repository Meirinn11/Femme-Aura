// Animasi sederhana
document.addEventListener('DOMContentLoaded', function() {
    // Animasi tombol
    const buttons = document.querySelectorAll('button, a.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'scale(1.02)';
        });
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
        });
    });
});