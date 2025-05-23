# NewsGuard AI - Your Shield Against Digital Deception

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

NewsGuard AI is an advanced news verification platform that uses artificial intelligence to analyze and verify the authenticity of news articles. In an era of rampant misinformation, this tool helps users distinguish fact from fiction by cross-referencing news content against trusted sources and providing detailed authenticity scores.

## Features

### 🔍 AI-Powered Analysis

- Advanced machine learning algorithms analyze news content for authenticity with high precision
- Extracts key headlines and points from articles for targeted verification

### 🌐 Cross-Reference Verification

- Automatically searches and compares news against trusted sources across the internet in real-time
- Uses Google Custom Search API to find relevant verification sources

### ⚡ Real-Time Results

- Get instant verification results with detailed credibility scores
- Comprehensive breakdown of factual accuracy, source consistency, detail accuracy, and context accuracy

### 🛡️ Authenticity Scoring

- Visual authenticity score with percentage rating
- Detailed key findings, differences, and supporting evidence from trusted sources

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: Ollama with Llama 3.2 model
- **APIs**: Google Custom Search API
- **Content Extraction**: Trafilatura, BeautifulSoup
- **Email**: Flask-Mail

## Installation

### Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.ai/) installed with the Llama 3.2 model
- Google Custom Search API key and Search Engine ID

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/VighneshDevHub/NewsGuard-AI.git
   cd NewsGuard-AI
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv env
   
   # On Windows
   .\env\Scripts\activate

   # On macOS/Linux
   source env/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure API keys:

   - Update the Google Custom Search API key and Search Engine ID in `app.py`
   - Configure email settings in `app.py` if you want to use the contact form

5. Run the application:

   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Usage

### Verifying News Articles

1. **Input**: Paste your news article or headline into the text area on the homepage
2. **Analysis**: Click "Analyze" to extract key points from the article
3. **Cross-Check**: Click "Cross Check" to search for and compare against trusted sources
4. **Authenticity Score**: On the results page, click "Analyze Authenticity" to get a detailed authenticity report

### Understanding Results

- **Authenticity Score**: Overall percentage indicating the article's credibility
- **Key Findings**: Important observations about the article's accuracy
- **Differences**: Notable inconsistencies or issues found
- **Supporting Evidence**: Quotes from trusted sources that verify or contradict the article
- **Score Breakdown**: Detailed scores for factual accuracy, source consistency, detail accuracy, and context accuracy

## How It Works

1. **URL Analysis**: The system processes the input news article
2. **AI Processing**: Advanced machine learning algorithms analyze the content
3. **Cross-Reference Check**: The system compares the article against trusted sources in real-time
4. **Score Generation**: A comprehensive credibility score is generated based on multiple factors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you have any questions or suggestions, please use the contact form on the website or open an issue on GitHub.

---

<p align="center">Built with ❤️ for truth in journalism</p>
