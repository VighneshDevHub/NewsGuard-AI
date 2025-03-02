/**
 * Initialize hover animations for social links
 */
function initializeSocialLinks() {
    const socialLinks = document.querySelectorAll('.social-link');
    
    socialLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            const icon = link.querySelector('i');
            icon.style.transform = 'translateY(-3px)';
        });
        
        link.addEventListener('mouseleave', () => {
            const icon = link.querySelector('i');
            icon.style.transform = 'translateY(0)';
        });
    });
}

// Export the function
export default initializeSocialLinks; 