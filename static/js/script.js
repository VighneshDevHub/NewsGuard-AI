async function extractKeyPhrases() {
    const newsInput = document.getElementById('news-input').value;
    const extractButton = document.getElementById('extract-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultSection = document.getElementById('result-section');

    // Show loading spinner and hide results
    extractButton.disabled = true;
    loadingSpinner.classList.remove('hidden');
    resultSection.classList.add('hidden');

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

        // Update UI with results
        document.getElementById('key-phrases').textContent = JSON.stringify(result.key_phrases, null, 2);

        // Show results and hide loading spinner
        resultSection.classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while extracting key phrases. Please try again.');
    } finally {
        extractButton.disabled = false;
        loadingSpinner.classList.add('hidden');
    }
}