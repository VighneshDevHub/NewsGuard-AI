/**
 * Main JavaScript file for the contact page
 */

// Import functions
import initializeFAQ from './utils/initializeFAQ.js';
import initializeContactForm from './utils/initializeContactForm.js';
import initializeInfoItems from './utils/initializeInfoItems.js';
import initializeSocialLinks from './utils/initializeSocialLinks.js';
import showNotification from './utils/showNotification.js';

// Make notification function available globally
window.showNotification = showNotification;

// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFAQ();
    initializeContactForm();
    initializeInfoItems();
    initializeSocialLinks();
}); 