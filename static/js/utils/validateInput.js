/**
 * Validate form input and display error messages
 * @param {Event} e - Input event
 */
function validateInput(e) {
    const input = e.target;
    const wrapper = input.closest('.input-wrapper');
    
    if (input.checkValidity()) {
        wrapper.classList.remove('error');
        wrapper.classList.add('valid');
    } else {
        wrapper.classList.add('error');
        wrapper.classList.remove('valid');
    }
    
    // Show validation message
    let errorMessage = input.validationMessage;
    if (!input.value && input.required) {
        errorMessage = `${input.placeholder} is required`;
    }
    
    // Update or create error message element
    let errorElement = wrapper.querySelector('.error-message');
    if (!errorElement && errorMessage) {
        errorElement = document.createElement('span');
        errorElement.className = 'error-message';
        wrapper.appendChild(errorElement);
    }
    if (errorElement) {
        errorElement.textContent = errorMessage;
    }
}

// Export the function
export default validateInput; 