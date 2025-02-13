from flask import Flask, request, jsonify, render_template
import ollama

app = Flask(__name__)

# Function to extract key phrases using Ollama's model
def extract_key_phrases_with_ollama(text):
    prompt = f"""
    I have this news article:\n\n{text}\n\n
    Please provide a response in pure JSON format:
    
    {{
        "news_authenticity": {{
            "authenticity_percentage": "Provide an authenticity percentage between 0 and 100",
            "explanation": "Provide an explanation about the gap between the original news and the extracted news"
        }},
        "news_headline": [
            "news_headline_1",
            "news_headline_2",
            "news_headline_3"
        ]
    }}
    """

    # Use Ollama's chat API
    response = ollama.chat(model="llama3.2", messages=[
        {"role": "user", "content": prompt},
    ])

    # Extract the response content
    return response['message']['content']

# Route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle key phrase extraction
@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    news_article = data.get('news', '')

    if not news_article:
        return jsonify({"error": "No news article provided"}), 400

    try:
        # Extract key phrases
        key_phrases = extract_key_phrases_with_ollama(news_article)
        return jsonify({"key_phrases": key_phrases})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)