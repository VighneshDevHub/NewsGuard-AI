/**
 * Update the score chart with an authenticity score
 * @param {number} score - Authenticity score (0-100)
 */
function updateScoreChart(score) {
    const scorePath = document.getElementById('score-path');
    const scoreElement = document.getElementById('authenticity-score');
    
    if (!scorePath) {
        console.error('Score path element not found');
        return;
    }
    
    // Ensure score is a number between 0-100
    const validScore = Math.max(0, Math.min(100, Number(score) || 0));
    
    // Calculate the circumference
    const radius = 15.9155;
    const circumference = 2 * Math.PI * radius;
    
    // Calculate the dash offset based on the score percentage
    const dashOffset = circumference - (validScore / 100) * circumference;
    
    // Set the stroke-dasharray and stroke-dashoffset
    scorePath.style.strokeDasharray = circumference;
    scorePath.style.strokeDashoffset = dashOffset;
    
    // Choose color based on score
    let color;
    if (validScore < 30) {
        color = '#ef4444'; // Red for low scores
    } else if (validScore < 70) {
        color = '#f59e0b'; // Orange/yellow for medium scores
    } else {
        color = '#10b981'; // Green for high scores
    }
    
    // Update the path color
    scorePath.style.stroke = color;
    
    // Update score text color to match
    if (scoreElement) {
        scoreElement.style.color = color;
    }
}

// Export the function
export default updateScoreChart;