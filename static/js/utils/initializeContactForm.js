/**
 * Initialize contact form with floating labels and validation
 */
function initializeContactForm() {
    const contactForm = document.querySelector('.contact-form');
    const formInputs = contactForm.querySelectorAll('input, textarea');
    
    // Add floating label effect
    formInputs.forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.className = 'input-wrapper';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        input.addEventListener('focus', () => wrapper.classList.add('focused'));
        input.addEventListener('blur', () => {
            if (!input.value) wrapper.classList.remove('focused');
        });
        
        // Add validation on input
        input.addEventListener('input', validateInput);
    });
    
    // Form submission
    contactForm.addEventListener('submit', handleFormSubmit);
}

// Import dependencies
import validateInput from './validateInput.js';
import handleFormSubmit from './handleFormSubmit.js';

// Export the function
export default initializeContactForm; 