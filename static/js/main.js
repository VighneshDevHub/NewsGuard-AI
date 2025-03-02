/**
 * Main JavaScript file for the NewsAuth application
 */

// Import functions
import extractKeyPhrases from './utils/extractKeyPhrases.js';
import searchNews from './utils/searchNews.js';
import showExtractedContent from './utils/showExtractedContent.js';
import analyzeAuthenticity from './utils/analyzeAuthenticity.js';
import updateScoreChart from './utils/updateScoreChart.js';

// Make functions available globally
window.extractKeyPhrases = extractKeyPhrases;
window.searchNews = searchNews;
window.showExtractedContent = showExtractedContent;
window.analyzeAuthenticity = analyzeAuthenticity;
window.updateScoreChart = updateScoreChart;

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners to buttons if they exist
    const extractButton = document.getElementById('extract-button');
    const searchButton = document.getElementById('search-button');
    const analyzeButton = document.getElementById('analyze-button');
    
    if (extractButton) {
        extractButton.addEventListener('click', extractKeyPhrases);
    }
    
    if (searchButton) {
        searchButton.addEventListener('click', searchNews);
    }
    
    if (analyzeButton) {
        analyzeButton.addEventListener('click', analyzeAuthenticity);
    }
}); 