# from flask import Flask, request, jsonify, render_template
# import ollama
# import requests
# import json

# # Create the Flask app
# app = Flask(__name__)

# # Google Custom Search setup
# API_KEY = "AIzaSyB2nlYuSgnoKLBKC4aF2nfF2drE3ZWIMNk"  # Replace with your actual Google API Key
# CSE_ID = "15c198a8769a045ec"  # Replace with your Custom Search Engine ID

# # Function to perform Google Search
# def google_search(query):
#     url = f"https://www.googleapis.com/customsearch/v1"
#     params = {
#         "q": query,
#         "key": API_KEY,
#         "cx": CSE_ID,
#     }
    
#     # Send GET request to Google API
#     response = requests.get(url, params=params)
    
#     # Log the raw response from Google
#     print(f"Google search response for query '{query}':", response.json())

#     # If the response status code is not 200 (OK), raise an error
#     if response.status_code != 200:
#         raise Exception(f"Error with Google Search API: {response.status_code}")
    
#     # Return the search results
#     return response.json()

# # Function to extract key phrases using Ollama
# def extract_key_phrases_with_ollama(text):
#     prompt = f"""
#     I have this news article:\n\n{text}\n\n
#     Please provide a response in pure JSON format:
    
#     {{
#         "news_authenticity": {{
#             "authenticity_percentage": "Provide an authenticity percentage between 0 and 100",
#             "explanation": "Provide an explanation about the gap between the original news and the extracted news"
#         }},
#         "news_headline": [
#             "news_headline_1",
#             "news_headline_2",
#             "news_headline_3"
#         ]
#     }}
#     """
#     response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    
#     if 'message' in response and 'content' in response['message']:
#         return response['message']['content']
#     return None

# # Route to render the HTML
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Route to handle the POST request for Google search
# @app.route('/extract', methods=['POST'])
# def extract():
#     data = request.get_json()
#     news_text = data['news']

#     # Step 1: Extract key phrases using Ollama
#     key_phrases_response = extract_key_phrases_with_ollama(news_text)
    
#     if key_phrases_response is None:
#         return jsonify({"error": "Failed to extract key phrases."}), 500

#     # Log the raw response to check its structure
#     print("Ollama response (raw):", key_phrases_response)

#     # Step 2.1: Parse the key_phrases_response from JSON string to a Python dictionary
#     try:
#         key_phrases_response = json.loads(key_phrases_response)
#         print("Parsed Ollama response:", key_phrases_response)
#     except json.JSONDecodeError as e:
#         return jsonify({"error": f"Failed to decode JSON response from Ollama. Error: {e}"}), 500

#     # Parse the key phrases and headlines from the response
#     try:
#         headlines = key_phrases_response.get("news_headline", [])  # Access headlines, default to empty list if missing
#         print("Extracted Headlines:", headlines)
#     except KeyError as e:
#         return jsonify({"error": f"Invalid key phrases response format. Missing key: {e}"}), 500

#     # If fewer than 3 headlines, add placeholders
#     while len(headlines) < 3:
#         headlines.append("")

#     # Step 3: Perform Google search for each of the top 3 headlines
#     google_search_results = {}
#     for headline in headlines:
#         if headline:  # Skip empty headlines
#             search_results = google_search(headline)
            
#             # Log the raw Google search results to debug
#             print(f"Google search results for '{headline}':", search_results)

#             # Store the top 3 news articles from the Google search results
#             google_search_results[headline] = search_results.get('items', [])[:3]  # Limit to top 3 results

#     # Combine the results and return them as JSON
#     return jsonify({
#         "key_phrases": key_phrases_response,
#         "google_search_results": google_search_results
#     })

# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, request, jsonify, render_template
import ollama
import json
import re

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

    # Call Ollama's chat API
    response = ollama.chat(model="llama3.2", messages=[
        {"role": "user", "content": prompt},
    ])

    # Log the raw response for debugging purposes
    print(f"Raw response from Ollama API: {response}")

    # Get the response content
    response_content = response.get('message', {}).get('content', '')
    if not response_content:
        raise ValueError("No content in the response")

    # Attempt to extract the JSON block between triple backticks.
    # This regex looks for triple backticks (optionally followed by "json"),
    # then captures everything between the first { and the matching }.
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_content, re.DOTALL)
    if match:
        json_string = match.group(1)
    else:
        # Fallback: try to extract everything between the first '{' and the last '}'
        start = response_content.find("{")
        end = response_content.rfind("}")
        if start != -1 and end != -1:
            json_string = response_content[start:end+1]
        else:
            raise ValueError("Could not extract JSON content from the response")

    try:
        json_response = json.loads(json_string)
        return json_response
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        raise ValueError("Invalid JSON response from Ollama API")

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
        print(f"Extracted key phrases: {key_phrases}")  # Debug output
        return jsonify({"key_phrases": key_phrases})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
