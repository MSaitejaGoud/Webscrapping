
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import mimetypes
import os
import time
import random

app = FastAPI(title="URL Scraper API", version="1.0.0")

class URLRequest(BaseModel):
    url: HttpUrl

# --- /analyze endpoint using smart_fetch ---
@app.post("/analyze")
async def analyze_url(request: URLRequest):
    result = smart_fetch(str(request.url))
    if result['type'] == 'html':
        return JSONResponse({
            'type': 'html',
            'title': result['title'],
            'paragraphs': result['paragraphs']
        })
    elif result['type'] == 'json':
        return JSONResponse({
            'type': 'json',
            'data': result.get('data', result.get('error', {}))
        })
    elif result['type'] == 'binary':
        return JSONResponse({
            'type': 'binary',
            'message': result['message']
        })
    else:
        return JSONResponse({'type': 'unknown', 'result': result})
import mimetypes
import os
# --- SMART FETCH FUNCTION ---
def smart_fetch(url):
    resp = requests.get(url, stream=True)
    content_type = resp.headers.get('content-type', '').lower()
    resp.encoding = resp.apparent_encoding  # Fix garbled HTML

    if 'text/html' in content_type:
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else 'No title'
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')[:3]]
        return {'type': 'html', 'title': title, 'paragraphs': paragraphs}

    elif 'application/json' in content_type or resp.text.strip().startswith('{'):
        try:
            return {'type': 'json', 'data': resp.json()}
        except Exception:
            return {'type': 'json', 'error': 'Invalid JSON'}

    else:
        ext = mimetypes.guess_extension(content_type.split(';')[0]) or '.bin'
        filename = f"downloaded_file{ext}"
        with open(filename, 'wb') as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return {'type': 'binary', 'message': f'Saved to {filename}'}
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random

app = FastAPI(title="URL Scraper API", version="1.0.0")

class URLRequest(BaseModel):
    url: HttpUrl

def intelligent_scrape(url: str) -> dict:
    result = try_regular_scraping(url)
    
    if result['content_length'] < 100 or 'loading' in result.get('full_content', '').lower():
        selenium_result = try_selenium_scraping(url)
        if selenium_result and selenium_result['content_length'] > result['content_length']:
            return selenium_result
    return result

def try_regular_scraping(url: str) -> dict:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    
    session = requests.Session()
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    try:
        main_url = f"{parsed_url.scheme}://{domain}"
        try:
            session.get(main_url, headers=headers, timeout=5)
            time.sleep(random.uniform(1, 2))
        except:
            pass
        
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 403:
            return extract_from_url(url)
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string.strip() if soup.title else "No title found"
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = desc_tag.get('content', 'Not found') if desc_tag else 'Not found'
        
        structured_info = extract_structured_data(soup, url)
        
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()
        
        content = soup.get_text(separator=' ', strip=True)
        content = ' '.join([line.strip() for line in content.split('\n') if line.strip()])
        
        return {
            'success': True,
            'title': title,
            'description': description,
            'structured_info': structured_info,
            'content_length': len(content),
            'full_content': content,
            'method': 'Regular Scraping'
        }
        
    except Exception as e:
        return extract_from_url(url, str(e))

## Playwright scraping removed. All scraping now uses requests/BeautifulSoup or Selenium fallback.

def try_selenium_scraping(url: str) -> dict:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        try:
            driver = webdriver.Chrome(options=options)
        except:
            return None
        
        driver.get(url)
        time.sleep(5)
        
        html = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        title = soup.title.string.strip() if soup.title else "No title found"
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = desc_tag.get('content', 'Not found') if desc_tag else 'Not found'
        
        structured_info = extract_structured_data(soup, url)
        
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()
        
        content = soup.get_text(separator=' ', strip=True)
        content = ' '.join([line.strip() for line in content.split('\n') if line.strip()])
        
        return {
            'success': True,
            'title': title,
            'description': description,
            'structured_info': structured_info,
            'content_length': len(content),
            'full_content': content,
            'method': 'Selenium Scraping'
        }
        
    except ImportError:
        return None
    except Exception as e:
        return None

def extract_from_url(url: str, error: str = None) -> dict:
    parsed = urlparse(url)
    domain = parsed.netloc
    path_parts = [p for p in parsed.path.split('/') if p]
    
    info = {'domain': domain, 'path_parts': path_parts}
    
    if 'bookmyshow.com' in domain:
        if len(path_parts) >= 4:
            info.update({
                'type': 'Movie',
                'platform': 'BookMyShow',
                'location': path_parts[1] if len(path_parts) > 1 else 'Unknown',
                'movie_name': path_parts[2].replace('-', ' ').title() if len(path_parts) > 2 else 'Unknown',
                'movie_id': path_parts[3] if len(path_parts) > 3 else 'Unknown'
            })
    elif 'youtube.com' in domain or 'youtu.be' in domain:
        info.update({'type': 'Video', 'platform': 'YouTube'})
    elif 'amazon.com' in domain or 'amazon.in' in domain:
        info.update({'type': 'Product', 'platform': 'Amazon'})
    elif 'flipkart.com' in domain:
        info.update({'type': 'Product', 'platform': 'Flipkart'})
    elif any(news in domain for news in ['news', 'times', 'hindu', 'ndtv', 'cnn']):
        info.update({'type': 'News Article'})
    elif 'crex.com' in domain or any(sport in domain for sport in ['cricket', 'espn', 'cricbuzz']):
        info.update({'type': 'Cricket/Sports', 'platform': 'Sports Site'})
    elif 'poki.com' in domain:
        if len(path_parts) >= 3 and path_parts[1] == 'g':
            game_name = path_parts[2].replace('-', ' ').title()
            info.update({
                'type': 'Online Game',
                'platform': 'Poki',
                'game_name': game_name,
                'category': 'Browser Game'
            })
    
    title = f"{info.get('platform', domain.title())} - {info.get('movie_name', info.get('game_name', info.get('type', 'Page')))}"
    full_content = f"Content from {domain}. " + (f"Error: {error}" if error else "Direct access blocked.")
    
    return {
        'success': True,
        'title': title,
        'description': f"Page from {domain}",
        'structured_info': info,
        'content_length': 0,
        'full_content': full_content,
        'note': 'Info extracted from URL structure'
    }

def extract_structured_data(soup, url: str) -> dict:
    info = {}
    
    h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')[:3]]
    if h1_tags:
        info['headings'] = h1_tags
    
    rating_selectors = ['.rating', '.star-rating', '[data-rating]', '.imdb-rating']
    for selector in rating_selectors:
        rating = soup.select_one(selector)
        if rating:
            info['rating'] = rating.get_text().strip()
            break
    
    price_selectors = ['.price', '.cost', '[data-price]', '.amount']
    for selector in price_selectors:
        price = soup.select_one(selector)
        if price:
            info['price'] = price.get_text().strip()
            break
    
    return info

@app.post("/scrape", response_class=PlainTextResponse)
async def scrape_url(request: URLRequest):
    try:
        result = intelligent_scrape(str(request.url))
        return result['full_content']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "URL Scraper API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)