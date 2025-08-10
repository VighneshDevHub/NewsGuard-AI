/**
 * JavaScript for search results page
 */

// Import the needed functions
import showExtractedContent from './utils/showExtractedContent.js';
import analyzeAuthenticity from './utils/analyzeAuthenticity.js';
import updateScoreChart from './utils/updateScoreChart.js';
import saveArticle from './utils/saveArticle.js';

// Make functions available globally
window.showExtractedContent = showExtractedContent;
window.analyzeAuthenticity = analyzeAuthenticity;
window.updateScoreChart = updateScoreChart;
window.saveArticle = saveArticle;

// Initialize any event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to analyze buttons if they exist
    const analyzeButtons = document.querySelectorAll('.analyze-button');
    if (analyzeButtons.length) {
        analyzeButtons.forEach(button => {
            button.addEventListener('click', analyzeAuthenticity);
        });
    }
    
    // Add event listeners to "View Full Content" buttons
    const viewContentButtons = document.querySelectorAll('.view-content-button');
    if (viewContentButtons.length) {
        viewContentButtons.forEach(button => {
            button.addEventListener('click', function() {
                const url = this.dataset.url;
                const newsContent = document.querySelector('.news-content');
                const originalNews = newsContent ? newsContent.textContent : '';
                
                if (url) {
                    showExtractedContent([url], originalNews);
                }
            });
        });
    }
});