/**
 * Update the score chart with an authenticity score
 * @param {number} score - Authenticity score (0-10)
 */
function updateScoreChart(score) {
    const canvas = document.getElementById('score-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Normalize score to 0-100%
    const normalizedScore = score / 10;
    
    // Choose color based on score
    let color;
    if (score < 3) {
        color = '#ff4d4d'; // Red for low scores
    } else if (score < 7) {
        color = '#ffad33'; // Orange for medium scores
    } else {
        color = '#4CAF50'; // Green for high scores
    }
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background circle
    ctx.beginPath();
    ctx.arc(100, 100, 80, 0, 2 * Math.PI);
    ctx.lineWidth = 15;
    ctx.strokeStyle = '#eaeaea';
    ctx.stroke();
    
    // Draw score arc
    ctx.beginPath();
    ctx.arc(100, 100, 80, -0.5 * Math.PI, (-0.5 + normalizedScore * 2) * Math.PI);
    ctx.lineWidth = 15;
    ctx.strokeStyle = color;
    ctx.stroke();
    
    // Add label
    ctx.font = 'bold 16px Arial';
    ctx.fillStyle = '#333';
    ctx.textAlign = 'center';
    ctx.fillText('Authenticity', 100, 180);
}

// Export the function
export default updateScoreChart; 