from flask import Flask, request, jsonify, render_template, redirect
import ollama
import requests
import json
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse
from datetime import datetime
from flask_mail import Mail, Message


# Create the Flask app
app = Flask(__name__)

# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'salunkhesantosh787@gmail.com'  # Your email here
app.config['MAIL_PASSWORD'] = 'ohjq iqcn zrpt xpco'  # Your email password here

# Initialize the Mail instance
mail = Mail(app)



# Google Custom Search setup
API_KEY = "AIzaSyB2nlYuSgnoKLBKC4aF2nfF2drE3ZWIMNk"
CSE_ID = "15c198a8769a045ec"

def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": API_KEY,
        "cx": CSE_ID,
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Error with Google Search API: {response.status_code}")
    
    # Extract only the URLs from the search results
    search_results = response.json()
    urls = []
    if 'items' in search_results:
        urls = [item['link'] for item in search_results['items']]
    
    return urls

def extract_key_phrases_with_ollama(text):
    prompt = f"""
        Please extract 3 concise headlines from the following news article. 
        Make sure the headlines are clear and concise, focusing on the main facts and events,places,people,organizations,etc.
    I have this news article:\n\n{text}\n\n
    Please provide a response in pure JSON format():
    {{
        "news_headline": [
            "news_headline_1",
            "news_headline_2",
            "news_headline_3"
        ]
    }}
    """
    
    response = ollama.chat(model='llama3.2', messages=[{"role": "user", "content": prompt}])
    
    if 'message' in response and 'content' in response['message']:
        try:
            # Extract JSON from the response content
            content = response['message']['content']
            # Find the JSON object in the response
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                json_str = content[start:end+1]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            raise
    return None

@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json()
        news_text = data.get('news')
        
        if not news_text:
            return jsonify({'error': 'No news text provided'}), 400

        # Extract key phrases using Ollama
        result = extract_key_phrases_with_ollama(news_text)
        
        if not result or 'news_headline' not in result:
            return jsonify({'error': 'Failed to extract headlines'}), 500

        return jsonify({'key_phrases': result})

    except Exception as e:
        print(f"Error in extract endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        news_text = data.get('news')
        
        if not news_text:
            return jsonify({'error': 'No news text provided'}), 400

        # Perform Google search
        search_results = google_search(news_text)
        
        return jsonify({
            'google_search_results': search_results
        })

    except Exception as e:
        print(f"Error in search endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add this function to extract content and metadata from URLs
def extract_article_content(url):
    try:
        # Download content
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            return None

        # Extract main content
        content = trafilatura.extract(downloaded)
        
        # Get metadata using BeautifulSoup as backup
        soup = BeautifulSoup(downloaded, 'html.parser')
        title = soup.title.string if soup.title else ''
        
        # Parse the URL to get the source
        source = urlparse(url).netloc.replace('www.', '')
        
        # Find image (first image in article or og:image)
        image_url = None
        og_image = soup.find('meta', property='og:image')
        if og_image:
            image_url = og_image.get('content')
        
        return {
            'url': url,
            'title': title,
            'content': content,  # Full content for display
            'description': content[:300] + '...' if content else '',
            'source': source,
            'image_url': image_url
        }
    except Exception as e:
        print(f"Error extracting content from {url}: {str(e)}")
        return None

# Add new route for displaying extracted content
@app.route('/extracted_content', methods=['POST'])
def show_extracted_content():
    try:
        data = request.get_json()
        original_news = data.get('news')
        urls = data.get('urls', [])

        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400

        # Extract content from each URL
        extracted_articles = []
        for url in urls[:3]:  # Limit to top 3 URLs
            article_content = extract_article_content(url)
            if article_content:
                extracted_articles.append(article_content)

        return render_template('extracted_content.html',
                             original_news=original_news,
                             extracted_articles=extracted_articles,
                             active_page='home')

    except Exception as e:
        print(f"Error in extracted_content endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['POST'])
def show_results():
    try:
        data = request.get_json()
        original_news = data.get('news')
        headlines = data.get('headlines', [])
        
        if not headlines:
            return jsonify({'error': 'No headlines provided'}), 400

        search_results = []
        
        # Process each headline
        for headline in headlines:
            # Search for URLs
            urls = google_search(headline)
            
            # Extract content from URLs
            articles = []
            for url in urls[:3]:  # Limit to top 3 URLs per headline
                article_content = extract_article_content(url)
                if article_content:
                    articles.append(article_content)
            
            # Add to results if we found articles
            if articles:
                search_results.append({
                    'headline': headline,
                    'articles': articles
                })

        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return render_template('search_results.html',
                             original_news=original_news,
                             search_results=search_results,
                             current_time=current_time,
                             active_page='home')

    except Exception as e:
        print(f"Error in results endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add this new function after your existing functions
def analyze_authenticity(original_news, verified_articles):
    # Prepare the content for comparison
    verified_contents = [article['content'] for article in verified_articles if article['content']]
    
    if not verified_contents:
        return {
            "authenticity_score": 0,
            "key_findings": ["No verified sources available for comparison"],
            "differences": ["Unable to verify due to lack of reference content"],
            "supporting_evidence": [{"quote": "No verified sources found", "source": "System"}],
            "score_breakdown": {
                "factual_accuracy": 0,
                "source_consistency": 0,
                "detail_accuracy": 0,
                "context_accuracy": 0
            }
        }

    # Simplified prompt with clear instructions
    prompt = f"""
    Compare this news article against trusted sources and analyze its authenticity.
    
    Original News Article:
    {original_news}

    Trusted Sources:
    {' '.join(verified_contents[:3])}

    Analyze the factual accuracy, source consistency, detail accuracy, and context accuracy.
    
    Respond with a JSON object containing:
    1. An overall authenticity score (0-100)
    2. 2-3 key findings about the article's accuracy
    3. 2-3 notable differences or issues found
    4. 2-3 supporting quotes from trusted sources
    5. A breakdown of scores for factual accuracy (0-40), source consistency (0-30), 
       detail accuracy (0-20), and context accuracy (0-10)
    """

    try:
        # Call the LLM with the simplified prompt
        response = ollama.chat(model='llama3.2', messages=[
            {
                "role": "system",
                "content": "You are a fact-checker,news analyst, and authenticity expert. Respond only with clean JSON in this format: {\"authenticity_score\": number, \"key_findings\": [string], \"differences\": [string], \"supporting_evidence\": [{\"quote\": string, \"source\": string}], \"score_breakdown\": {\"factual_accuracy\": number, \"source_consistency\": number, \"detail_accuracy\": number, \"context_accuracy\": number}}"
            },
            {
                "role": "user",
                "content": prompt
            }
        ])

        # Extract content from response
        if not response or 'message' not in response or 'content' not in response['message']:
            return create_error_response("Invalid response from LLM")

        content = response['message']['content'].strip()
        
        # Extract JSON from the response
        try:
            # Find JSON object in the response
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                json_str = content[start:end+1]
                result = json.loads(json_str)
                
                # Create a standardized response with defaults for missing fields
                analysis = {
                    "authenticity_score": 0,
                    "key_findings": [],
                    "differences": [],
                    "supporting_evidence": [],
                    "score_breakdown": {
                        "factual_accuracy": 0,
                        "source_consistency": 0,
                        "detail_accuracy": 0,
                        "context_accuracy": 0
                    }
                }
                
                # Extract and validate authenticity score
                try:
                    score = int(result.get('authenticity_score', 0))
                    analysis["authenticity_score"] = max(0, min(100, score))
                except (ValueError, TypeError):
                    pass
                
                # Extract key findings (up to 3)
                findings = result.get('key_findings', [])
                if isinstance(findings, list):
                    analysis["key_findings"] = [str(f) for f in findings[:3]]
                
                # Extract differences (up to 3)
                differences = result.get('differences', [])
                if isinstance(differences, list):
                    analysis["differences"] = [str(d) for d in differences[:3]]
                
                # Extract supporting evidence (up to 3)
                evidence = result.get('supporting_evidence', [])
                if isinstance(evidence, list):
                    for item in evidence[:3]:
                        if isinstance(item, dict):
                            analysis["supporting_evidence"].append({
                                "quote": str(item.get('quote', '')),
                                "source": str(item.get('source', 'Unknown'))
                            })
                
                # Extract score breakdown
                breakdown = result.get('score_breakdown', {})
                if isinstance(breakdown, dict):
                    try:
                        analysis["score_breakdown"] = {
                            "factual_accuracy": max(0, min(40, int(breakdown.get('factual_accuracy', 0)))),
                            "source_consistency": max(0, min(30, int(breakdown.get('source_consistency', 0)))),
                            "detail_accuracy": max(0, min(20, int(breakdown.get('detail_accuracy', 0)))),
                            "context_accuracy": max(0, min(10, int(breakdown.get('context_accuracy', 0))))
                        }
                    except (ValueError, TypeError):
                        pass
                
                return analysis
            else:
                return create_error_response("Could not find JSON in LLM response")
                
        except json.JSONDecodeError:
            return create_error_response("Failed to parse LLM response")

    except Exception as e:
        print(f"Error in analyze_authenticity: {str(e)}")
        return create_error_response(f"Analysis failed: {str(e)}")

def create_error_response(error_message):
    return {
        "authenticity_score": 0,
        "key_findings": [error_message],
        "differences": ["Analysis failed"],
        "supporting_evidence": [{"quote": "Error processing request", "source": "System"}],
        "score_breakdown": {
            "factual_accuracy": 0,
            "source_consistency": 0,
            "detail_accuracy": 0,
            "context_accuracy": 0
        }
    }

@app.route('/analyze_authenticity', methods=['POST'])
def get_authenticity_analysis():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No JSON data received")

        original_news = data.get('original_news')
        verified_articles = data.get('verified_articles', [])
        
        if not original_news:
            raise ValueError("No original news content provided")
            
        analysis_result = analyze_authenticity(original_news, verified_articles)
        return jsonify(analysis_result)
        
    except Exception as e:
        print(f"Error in get_authenticity_analysis: {str(e)}")
        return jsonify({
            "authenticity_score": 0,
            "key_findings": ["Error during analysis"],
            "differences": ["Analysis failed"],
            "supporting_evidence": [{"quote": "Unable to process", "source": "System"}],
            "score_breakdown": {
                "factual_accuracy": 0,
                "source_consistency": 0,
                "detail_accuracy": 0,
                "context_accuracy": 0
            }
        }), 200  # Return 200 instead of 500 to handle error gracefully

@app.route('/about')
def about():
    try:
        return render_template('about.html', active_page='about')
    except Exception as e:
        print(f"Error rendering about page: {str(e)}")
        return redirect('/')

@app.route('/how-it-works')
def how_it_works():
    try:
        return render_template('how-it-works.html', active_page='how-it-works')
    except Exception as e:
        print(f"Error rendering how-it-works page: {str(e)}")
        return redirect('/')

@app.route('/contact')
def contact():
    try:
        return render_template('contact.html', active_page='contact')
    except Exception as e:
        print(f"Error rendering contact page: {str(e)}")
        return redirect('/')

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    print(request.json)  # Debugging: Check if JSON data is received

    try:
        # Extract data from the JSON payload
        name = request.json.get('name')
        email = request.json.get('email')
        subject = request.json.get('subject')
        message = request.json.get('message')

        if not name or not email or not message:
            return jsonify({'error': 'Please fill out all fields'}), 400

        # Create the email message
        body = f"Name: {name}\nEmail: {email}\n\nSubject:{subject}\n\nMessage: {message}"

        msg = Message(subject=subject,
                      sender='salunkhesantosh787@gmail.com',
                      recipients=['vighneshsalunkhe13@gmail.com'])
        msg.body = body
        mail.send(msg)

        return jsonify({'message': 'Form submitted successfully! We will get back to you shortly.'}), 200

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({'error': 'Failed to submit form'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

