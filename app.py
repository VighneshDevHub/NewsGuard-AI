from flask import Flask, request, jsonify, render_template, redirect, url_for
import ollama
import requests
import json
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse
from datetime import datetime
from flask_mail import Mail, Message
from flask_login import LoginManager, current_user, login_required
from config import Config
from models import db, User, UserHistory, SavedArticle, VerificationResult, SearchQuery
from auth import auth as auth_blueprint

# Create the Flask app
app = Flask(__name__)

# Load configuration from Config class
app.config.from_object(Config)

# Initialize Flask-Mail
mail = Mail(app)

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')

# Google Custom Search setup
API_KEY = Config.GOOGLE_API_KEY
CSE_ID = Config.GOOGLE_CSE_ID

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
        You are a professional news analyst.
        Please extract 3 concise headlines from the following news article. 
        Make sure that each headlines are clear and concise, focusing on the main facts and events,places,people,organizations,date-time,etc.
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
            'content': content,  
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
        
        # Create search query record in database
        search_query = SearchQuery(query_text=original_news)
        search_query.set_headlines(headlines)
        
        # Associate with user if logged in
        if current_user.is_authenticated:
            search_query.user_id = current_user.id
        
        db.session.add(search_query)
        db.session.commit()
        
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
        
        # Update search query with results
        search_query.set_search_results({headline: [a['url'] for a in result['articles']] 
                                        for result in search_results 
                                        for headline in [result['headline']]})
        db.session.commit()
        
        # Add to user history if logged in
        if current_user.is_authenticated:
            history_entry = UserHistory(
                user_id=current_user.id,
                action_type='search_performed',
                action_details=f'Search with {len(headlines)} headlines',
                article_title=f'Search #{search_query.id}'
            )
            db.session.add(history_entry)
            db.session.commit()

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
    You are professional fact-checker and news analyst.
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
        
        # Store verification result in database if user is logged in
        if current_user.is_authenticated:
            # Create verification result record
            verification = VerificationResult(
                user_id=current_user.id,
                original_text=original_news,
                authenticity_score=analysis_result['authenticity_score']
            )
            
            # Set JSON fields
            verification.set_key_findings(analysis_result['key_findings'])
            verification.set_differences(analysis_result['differences'])
            verification.set_supporting_evidence(analysis_result['supporting_evidence'])
            verification.set_score_breakdown(analysis_result['score_breakdown'])
            
            # Add to database
            db.session.add(verification)
            
            # Add to user history
            history_entry = UserHistory(
                user_id=current_user.id,
                action_type='article_verified',
                action_details=f'Article verified with score: {analysis_result["authenticity_score"]}%',
                article_title='Verification #' + str(verification.id)
            )
            db.session.add(history_entry)
            db.session.commit()
        
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

@app.route('/faq')
def faq():
    try:
        return render_template('faq.html', active_page='faq')
    except Exception as e:
        print(f"Error rendering FAQ page: {str(e)}")
        return redirect('/')

@app.route('/documentation')
def documentation():
    try:
        return render_template('documentation.html', active_page='documentation')
    except Exception as e:
        print(f"Error rendering documentation page: {str(e)}")
        return redirect('/')

@app.route('/save_article', methods=['POST'])
@login_required
def save_article():
    try:
        data = request.get_json()
        article_url = data.get('article_url')
        article_title = data.get('article_title')
        article_content = data.get('article_content')
        article_source = data.get('article_source')
        image_url = data.get('image_url')
        
        if not article_url or not article_title:
            return jsonify({'error': 'URL and title are required'}), 400
            
        # Check if article is already saved
        existing = SavedArticle.query.filter_by(user_id=current_user.id, article_url=article_url).first()
        if existing:
            return jsonify({'message': 'Article already saved', 'saved': True}), 200
        
        # Create new saved article
        saved_article = SavedArticle(
            user_id=current_user.id,
            article_url=article_url,
            article_title=article_title,
            article_content=article_content,
            article_source=article_source,
            image_url=image_url
        )
        
        # Add to database
        db.session.add(saved_article)
        
        # Add to user history
        history_entry = UserHistory(
            user_id=current_user.id,
            action_type='article_saved',
            action_details=f'Saved article: {article_title[:50]}...',
            article_url=article_url,
            article_title=article_title
        )
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify({'message': 'Article saved successfully', 'saved': True}), 200
        
    except Exception as e:
        print(f"Error saving article: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api-access')
def api_access():
    try:
        return render_template('api-access.html', active_page='api-access')
    except Exception as e:
        print(f"Error rendering API access page: {str(e)}")
        return redirect('/')

@app.route('/case-studies')
def case_studies():
    try:
        return render_template('case-studies.html', active_page='case-studies')
    except Exception as e:
        print(f"Error rendering case studies page: {str(e)}")
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
