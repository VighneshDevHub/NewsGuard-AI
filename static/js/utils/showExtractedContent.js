/**
 * Show content extracted from URLs
 * @param {Array} urls - URLs to extract content from
 * @param {string} originalNews - Original news content
 */
async function showExtractedContent(urls, originalNews) {
    const loadingSpinner = document.getElementById('loading-spinner');
    
    try {
        // Show loading spinner
        if (loadingSpinner) {
            loadingSpinner.classList.remove('hidden');
        }
        
        const response = await fetch('/extracted_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                urls: urls,
                news: originalNews
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to extract content');
        }

        // Get the HTML content and replace the entire page
        const htmlContent = await response.text();
        document.documentElement.innerHTML = htmlContent;

        // Hide loading spinner after new page content is loaded
        const newLoadingSpinner = document.getElementById('loading-spinner');
        if (newLoadingSpinner) {
            newLoadingSpinner.classList.add('hidden');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Error extracting content from URLs');
        // Hide loading spinner on error
        if (loadingSpinner) {
            loadingSpinner.classList.add('hidden');
        }
    }
}

// Export the function
export default showExtractedContent; 