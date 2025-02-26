from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

def get_favicon_url(website_url):
    # Send a GET request to the website
    response = requests.get(website_url)
    
    if response.status_code != 200:
        return None
    
    # Parse the website's HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find the link to the favicon in the HTML <head> section
    link_tag = soup.find("link", rel=lambda rel: rel and 'icon' in rel.lower())
    
    if link_tag and 'href' in link_tag.attrs:
        # Resolve the favicon URL (it could be relative, so we use urljoin)
        favicon_url = urljoin(website_url, link_tag.attrs['href'])
        return favicon_url
    
    return None

@app.route('/')
def get_favicon():
    website_url = request.args.get('url')
    
    if not website_url:
        return jsonify({"error": "URL is missing"}), 400
    
    # If the URL doesn't start with "http://" or "https://", add "https://"
    if not website_url.startswith('http://') and not website_url.startswith('https://'):
        website_url = 'https://' + website_url

    # Remove 'https://' or 'http://' from the website URL for the JSON response
    website_url_stripped = website_url.replace('https://', '').replace('http://', '')
    
    favicon_url = get_favicon_url(website_url)
    
    if not favicon_url:
        return jsonify({"error": "Favicon not found"}), 404
    
    # JSON response:
    response_data = {
        "website": website_url_stripped,
        "favicon": favicon_url
    }
    
    # headers 
    response = jsonify(response_data)
    response.headers['Access-Control-Allow-Origin'] = '*'  # Allow cross-origin requests (CORS)
    response.headers['Content-Type'] = 'application/json'  # JSON
    
    return response

if __name__ == '__main__':
    app.run(debug=True)