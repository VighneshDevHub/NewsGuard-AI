/**
 * Initialize hover animations for info items
 */
function initializeInfoItems() {
    const infoItems = document.querySelectorAll('.info-item');
    
    infoItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            const icon = item.querySelector('.info-icon i');
            icon.style.transform = 'scale(1.2) rotate(5deg)';
        });
        
        item.addEventListener('mouseleave', () => {
            const icon = item.querySelector('.info-icon i');
            icon.style.transform = 'scale(1) rotate(0deg)';
        });
    });
}

// Export the function
export default initializeInfoItems; 