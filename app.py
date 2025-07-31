from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
import time
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@app.route('/analyze_url', methods=['POST'])
def analyze_url():
    driver = None
    try:
        data = request.get_json()
        url = data.get('url') if data else None
        
        logger.info(f"Request received for URL: {url}")
        
        if not url:
            logger.warning("Request missing URL")
            return jsonify({'error': 'URL is required'}), 400
        
        if not is_valid_url(url):
            logger.warning(f"Invalid URL format: {url}")
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Setup requests session with stealth headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        session = requests.Session()
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Visit main site first for cookies
        try:
            main_url = f"{parsed_url.scheme}://{domain}"
            session.get(main_url, headers=headers, timeout=5)
            time.sleep(random.uniform(1, 2))
        except:
            pass
        
        # Get the actual page
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # Check if we got JavaScript-heavy content (like MSN)
        if 'msn.com' in domain and (len(html) < 1000 or 'window._clientSettings' in html):
            # Extract from URL structure for MSN
            path_parts = [p for p in parsed_url.path.split('/') if p]
            article_title = "Unknown Article"
            if len(path_parts) >= 3:
                article_title = path_parts[2].replace('-', ' ').title()
            
            return jsonify({
                'title': f'MSN - {article_title}',
                'h1_tags': [article_title],
                'links': [],
                'content_preview': f'MSN article: {article_title}. JavaScript-heavy site detected.',
                'method': 'URL Structure Extraction',
                'note': 'MSN uses heavy JavaScript - content extracted from URL'
            }), 200
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract data
        title = soup.title.string.strip() if soup.title else "No title found"
        h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
        links = [{'text': a.get_text().strip(), 'href': urljoin(url, a.get('href', ''))} 
                for a in soup.find_all('a', href=True) if a.get_text().strip()]
        
        # Get content preview
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()
        content_text = soup.get_text(separator=' ', strip=True)
        content_preview = content_text[:300] + '...' if len(content_text) > 300 else content_text
        
        result = {
            'title': title,
            'h1_tags': h1_tags,
            'links': links[:10],
            'content_preview': content_preview,
            'method': 'Regular Scraping'
        }
        
        logger.info(f"Successfully scraped URL: {url} - Title: {title}")
        return jsonify(result), 200
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout accessing URL: {url if 'url' in locals() else 'unknown'}")
        return jsonify({'error': 'URL is unreachable or took too long to load'}), 408
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({'error': 'Failed to load webpage'}), 502
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)