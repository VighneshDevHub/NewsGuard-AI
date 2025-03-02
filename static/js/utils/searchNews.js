/**
 * Search for news articles based on the input text
 */
async function searchNews() {
    const newsInput = document.getElementById('news-input').value;
    const searchButton = document.getElementById('search-button');
    const loadingSpinner = document.getElementById('loading-spinner');

    if (!newsInput.trim()) {
        alert('Please enter some text to analyze');
        return;
    }

    try {
        // Show loading state
        searchButton.disabled = true;
        if (loadingSpinner) {
            loadingSpinner.classList.remove('hidden');
        }

        // First get headlines
        const extractResponse = await fetch('/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ news: newsInput }),
        });

        if (!extractResponse.ok) {
            throw new Error('Failed to extract headlines');
        }

        const extractResult = await extractResponse.json();
        const headlines = extractResult.key_phrases?.news_headline || [];

        if (headlines.length === 0) {
            throw new Error('No headlines were extracted');
        }

        // Send to results page
        const resultsResponse = await fetch('/results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                news: newsInput,
                headlines: headlines
            }),
        });

        if (!resultsResponse.ok) {
            throw new Error('Failed to get results');
        }

        // Get the HTML content and replace the current page
        const htmlContent = await resultsResponse.text();
        document.documentElement.innerHTML = htmlContent;

        // Hide loading spinner after new page content is loaded
        const newLoadingSpinner = document.getElementById('loading-spinner');
        if (newLoadingSpinner) {
            newLoadingSpinner.classList.add('hidden');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during the search process. Please try again.');
        if (loadingSpinner) {
            loadingSpinner.classList.add('hidden');
        }
    } finally {
        searchButton.disabled = false;
    }
}

// Export the function
export default searchNews; 