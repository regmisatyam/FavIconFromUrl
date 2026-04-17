from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

def get_favicon_url(website_url):
    response = requests.get(website_url)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # BS4 checks if the string is IN the rel list — no lambda needed
    rel_priorities = [
        'apple-touch-icon',
        'apple-touch-icon-precomposed',
        'icon',
        'shortcut icon',
    ]
    
    for rel_value in rel_priorities:
        link_tag = soup.find("link", rel=rel_value)
        if link_tag and 'href' in link_tag.attrs:
            return urljoin(website_url, link_tag.attrs['href'])
    
    # Final fallback: try /favicon.ico directly
    parsed = urlparse(website_url)
    fallback = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    try:
        r = requests.head(fallback, timeout=3)
        if r.status_code == 200:
            return fallback
    except requests.RequestException:
        pass
    
    return None

@app.route('/')
def get_favicon():
    website_url = request.args.get('url')
    
    if not website_url:
        return jsonify({"error": "URL is missing"}), 400
    
    if not website_url.startswith('http://') and not website_url.startswith('https://'):
        website_url = 'https://' + website_url

    website_url_stripped = website_url.replace('https://', '').replace('http://', '')
    
    favicon_url = get_favicon_url(website_url)
    
    if not favicon_url:
        return jsonify({"error": "Favicon not found"}), 404
    
    response_data = {
        "website": website_url_stripped,
        "favicon": favicon_url
    }
    
    response = jsonify(response_data)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
