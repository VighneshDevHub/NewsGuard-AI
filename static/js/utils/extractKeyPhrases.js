/**
 * Extract key phrases from the provided text
 */
async function extractKeyPhrases() {
    const newsInput = document.getElementById('news-input').value;
    const extractButton = document.getElementById('extract-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultSection = document.getElementById('result-section');
    const headlinesList = document.getElementById('headlines-list');

    if (!newsInput.trim()) {
        alert('Please enter some text to analyze');
        return;
    }

    // Show loading spinner and hide previous results
    extractButton.disabled = true;
    loadingSpinner.classList.remove('hidden');  // Show the loader
    resultSection.classList.add('hidden');     // Hide result section
    headlinesList.innerHTML = '';               // Clear previous headlines

    try {
        // Make API call to Flask backend
        const response = await fetch('/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ news: newsInput }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        console.log(result);  // Debug output

        // Check for key phrases and handle missing data gracefully
        const headlines = result.key_phrases?.news_headline || [];

        if (headlines.length === 0) {
            alert('No headlines were found. Please try with different text.');
            return;
        }

        // Display only 3 headlines
        headlines.slice(0, 3).forEach((headline) => {
            const listItem = document.createElement('li');
            listItem.textContent = headline;
            headlinesList.appendChild(listItem);
        });

        // Show results
        resultSection.classList.remove('hidden');  // Show the result section
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while extracting key phrases. Please try again.');
    } finally {
        extractButton.disabled = false;
        loadingSpinner.classList.add('hidden');   // Hide the loader
    }
}

// Export the function
export default extractKeyPhrases; 