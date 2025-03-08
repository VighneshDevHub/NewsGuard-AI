/**
 * Analyze the authenticity of news compared to verified articles
 */
async function analyzeAuthenticity() {
    const analyzeButton = document.getElementById('analyze-button');
    const analysisResults = document.getElementById('analysis-results');
    
    try {
        // Show loading state
        analyzeButton.disabled = true;
        analyzeButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        
        // Get original news and verified articles
        const originalNews = document.querySelector('.news-content').textContent;
        const verifiedArticles = Array.from(document.querySelectorAll('.news-card')).map(card => ({
            content: card.querySelector('.description').textContent
        }));
        
        // Make API call
        const response = await fetch('/analyze_authenticity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                original_news: originalNews,
                verified_articles: verifiedArticles
            }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze authenticity');
        }
        
        const result = await response.json();
        
        // Update UI with the authenticity score
        if (analysisResults) {
            // Update the score percentage
            const scoreElement = document.getElementById('authenticity-score');
            if (scoreElement) {
                scoreElement.textContent = result.authenticity_score;
            }
            
            // Update key findings list
            const findingsList = document.getElementById('key-findings-list');
            if (findingsList && result.key_findings) {
                findingsList.innerHTML = '';
                result.key_findings.forEach(finding => {
                    const li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
            }
            
            // Update differences list
            const differencesList = document.getElementById('differences-list');
            if (differencesList && result.differences) {
                differencesList.innerHTML = '';
                result.differences.forEach(difference => {
                    const li = document.createElement('li');
                    li.textContent = difference;
                    differencesList.appendChild(li);
                });
            }
            
            // Update evidence list
            const evidenceList = document.getElementById('evidence-list');
            if (evidenceList && result.supporting_evidence) {
                evidenceList.innerHTML = '';
                result.supporting_evidence.forEach(evidence => {
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>"${evidence.quote}"</strong> - <em>${evidence.source}</em>`;
                    evidenceList.appendChild(li);
                });
            }
            
            // Show the results
            analysisResults.classList.remove('hidden');
            
            // Update score chart
            updateScoreChart(result.authenticity_score);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during authenticity analysis. Please try again.');
    } finally {
        // Reset button state
        if (analyzeButton) {
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = 'Analyze Authenticity';
        }
    }
}

// Export the function
export default analyzeAuthenticity;