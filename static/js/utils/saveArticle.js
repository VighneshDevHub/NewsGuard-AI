/**
 * Save an article to the user's saved articles list
 * @param {string} articleUrl - URL of the article to save
 * @param {string} articleTitle - Title of the article
 * @param {string} articleContent - Content of the article
 * @param {string} articleSource - Source of the article
 * @param {string} imageUrl - URL of the article image
 */
async function saveArticle(articleUrl, articleTitle, articleContent, articleSource, imageUrl) {
    try {
        // Make API call to save the article
        const response = await fetch('/save_article', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                article_url: articleUrl,
                article_title: articleTitle,
                article_content: articleContent,
                article_source: articleSource,
                image_url: imageUrl
            }),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to save article');
        }
        
        const result = await response.json();
        
        // Show success message
        alert(result.message || 'Article saved successfully!');
        
        // Update button state if it exists
        const saveButton = document.querySelector(`[data-url="${articleUrl}"]`);
        if (saveButton) {
            saveButton.innerHTML = '<i class="fas fa-check"></i> Saved';
            saveButton.disabled = true;
        }
        
        return result;
    } catch (error) {
        console.error('Error saving article:', error);
        alert(error.message || 'An error occurred while saving the article');
        return null;
    }
}

// Export the function
export default saveArticle;