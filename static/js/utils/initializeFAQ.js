/**
 * Initialize FAQ accordion functionality
 */
function initializeFAQ() {
    const faqCards = document.querySelectorAll('.faq-card');
    
    faqCards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('active');
            const content = this.querySelector('p');
            
            if (this.classList.contains('active')) {
                content.style.maxHeight = content.scrollHeight + 'px';
                content.style.marginTop = '1rem';
            } else {
                content.style.maxHeight = '0';
                content.style.marginTop = '0';
            }
        });
    });
}

// Export the function
export default initializeFAQ; 