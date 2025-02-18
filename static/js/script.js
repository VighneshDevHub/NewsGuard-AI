async function extractKeyPhrases() {
    const newsInput = document.getElementById('news-input').value;
    const extractButton = document.getElementById('extract-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultSection = document.getElementById('result-section');
    const headlinesList = document.getElementById('headlines-list');

    // Show loading spinner and hide previous results
    extractButton.disabled = true;
    loadingSpinner.classList.remove('hidden');
    resultSection.classList.add('hidden');
    headlinesList.innerHTML = '';  // Clear previous headlines

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
            alert('No headlines were found.');
        }

        // Display only 3 headlines
        headlines.slice(0, 3).forEach((headline) => {
            const listItem = document.createElement('li');
            listItem.textContent = headline;
            headlinesList.appendChild(listItem);
        });

        // Show results and hide the loading spinner
        resultSection.classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while extracting key phrases. Please try again.');
    } finally {
        extractButton.disabled = false;
        loadingSpinner.classList.add('hidden');
    }
}


async function searchNews() {
    const newsInput = document.getElementById('news-input').value;
    const searchButton = document.getElementById('search-button');
    const searchResultsList = document.getElementById('search-results-list');
    const loadingSpinner = document.getElementById('loading-spinner');

    // Show loading spinner and hide previous results
    searchButton.disabled = true;
    loadingSpinner.classList.remove('hidden');
    searchResultsList.innerHTML = '';  // Clear previous search results

    try {
        // Make API call to Flask backend to perform search
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

        // Display Google search results
        const searchResults = result.google_search_results;

        searchResults.forEach((url) => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = url;
            link.textContent = url;
            link.target = '_blank';  // Open in a new tab
            listItem.appendChild(link);
            searchResultsList.appendChild(listItem);
        });

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during the Google search. Please try again.');
    } finally {
        searchButton.disabled = false;
        loadingSpinner.classList.add('hidden');
    }
}

// async function extractKeyPhrases() {
//     const newsInput = document.getElementById('news-input').value;
//     const extractButton = document.getElementById('extract-button');
//     const loadingSpinner = document.getElementById('loading-spinner');
//     const resultSection = document.getElementById('result-section');
//     const headlinesList = document.getElementById('headlines-list');

//     // Show loading spinner and hide previous results
//     extractButton.disabled = true;
//     loadingSpinner.classList.remove('hidden');
//     resultSection.classList.add('hidden');
//     headlinesList.innerHTML = '';  // Clear previous headlines

//     try {
//         // Make API call to Flask backend
//         const response = await fetch('/extract', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ news: newsInput }),
//         });

//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }

//         const result = await response.json();
//         console.log(result);  // Debug output

//         // Extract the headlines from the returned JSON object
//         const headlines = result.key_phrases.news_headline;

//         // Display only 3 headlines
//         headlines.slice(0, 3).forEach((headline) => {
//             const listItem = document.createElement('li');
//             listItem.textContent = headline;
//             headlinesList.appendChild(listItem);
//         });

//         // Show results and hide the loading spinner
//         resultSection.classList.remove('hidden');
//     } catch (error) {
//         console.error('Error:', error);
//         alert('An error occurred while extracting key phrases. Please try again.');
//     } finally {
//         extractButton.disabled = false;
//         loadingSpinner.classList.add('hidden');
//     }
// }
