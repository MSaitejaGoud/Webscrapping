import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random

def intelligent_scrape(url):
    # Try regular scraping first
    result = try_regular_scraping(url)
    
    # If content is too short or indicates JS loading, try browser automation
    if result['content_length'] < 100 or 'loading' in result.get('full_content', '').lower():
        print("Regular scraping failed, trying Playwright...")
        playwright_result = try_playwright_scraping(url)
        if playwright_result and playwright_result['content_length'] > result['content_length']:
            return playwright_result
            
        print("Playwright failed, trying Selenium...")
        selenium_result = try_selenium_scraping(url)
        if selenium_result and selenium_result['content_length'] > result['content_length']:
            return selenium_result
    
    return result

def try_regular_scraping(url):
    # Advanced headers for stealth
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
        # Visit main site first for cookies
        main_url = f"{parsed_url.scheme}://{domain}"
        try:
            session.get(main_url, headers=headers, timeout=5)
            time.sleep(random.uniform(1, 2))
        except:
            pass
        
        # Try to get the actual page
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 403:
            return extract_from_url(url)
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract information
        title = soup.title.string.strip() if soup.title else "No title found"
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = desc_tag.get('content', 'Not found') if desc_tag else 'Not found'
        
        # Extract structured data
        structured_info = extract_structured_data(soup, url)
        
        # Clean content
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
            'full_content': content,  # Return full content instead of summary
            'method': 'Regular Scraping'
        }
        
    except Exception as e:
        return extract_from_url(url, str(e))

def try_playwright_scraping(url):
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            page.goto(url, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            html = page.content()
            browser.close()
        
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
            'method': 'Playwright Scraping'
        }
        
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright")
        return None
    except Exception as e:
        print(f"Playwright scraping failed: {e}")
        return None

def try_selenium_scraping(url):
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
            print("Chrome driver not found, install ChromeDriver")
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
        print("Selenium not installed. Install with: pip install selenium")
        return None
    except Exception as e:
        print(f"Selenium scraping failed: {e}")
        return None

def extract_from_url(url, error=None):
    """Extract info from URL structure when direct scraping fails"""
    parsed = urlparse(url)
    domain = parsed.netloc
    path_parts = [p for p in parsed.path.split('/') if p]
    
    info = {'domain': domain, 'path_parts': path_parts}
    
    # Domain-specific extraction
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
        if 'scoreboard' in url:
            # Enhanced cricket match info extraction from Crex URL
            match_parts = [p for p in path_parts if 'vs' in p.lower()]
            if match_parts:
                teams = match_parts[0].replace('-', ' ').title()
                # Extract match details from path
                match_number = next((p for p in path_parts if 'match' in p.lower()), 'Unknown Match')
                series_info = 'India Tour of England 2025' if 'england' in url and 'india' in url else 'Cricket Series'
                
                # Determine format from URL structure
                format_type = 'TEST' if any(x in path_parts for x in ['QST', 'test']) else 'ODI/T20'
                
                info.update({
                    'type': 'Cricket Match',
                    'platform': 'Crex',
                    'match': teams,
                    'match_number': match_number.replace('-', ' ').title(),
                    'format': format_type,
                    'series': series_info,
                    'venue': 'International Cricket',
                    'url_structure': '/'.join(path_parts[:4])  # Match identifier
                })
            else:
                info.update({'type': 'Cricket Scoreboard', 'platform': 'Crex'})
    elif 'poki.com' in domain:
        # Add Poki game detection
        if len(path_parts) >= 3 and path_parts[1] == 'g':
            game_name = path_parts[2].replace('-', ' ').title()
            info.update({
                'type': 'Online Game',
                'platform': 'Poki',
                'game_name': game_name,
                'category': 'Browser Game'
            })
    
    title = f"{info.get('platform', domain.title())} - {info.get('movie_name', info.get('match', info.get('game_name', info.get('type', 'Page'))))}"
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

def extract_structured_data(soup, url):
    """Extract structured data based on site type"""
    info = {}
    
    # Try to find common elements
    h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')[:3]]
    if h1_tags:
        info['headings'] = h1_tags
    
    # Look for ratings
    rating_selectors = ['.rating', '.star-rating', '[data-rating]', '.imdb-rating']
    for selector in rating_selectors:
        rating = soup.select_one(selector)
        if rating:
            info['rating'] = rating.get_text().strip()
            break
    
    # Look for price (for e-commerce)
    price_selectors = ['.price', '.cost', '[data-price]', '.amount']
    for selector in price_selectors:
        price = soup.select_one(selector)
        if price:
            info['price'] = price.get_text().strip()
            break
    
    return info

# === MAIN EXECUTION ===
if __name__ == "__main__":
    URL = input("Enter the URL: ")
    result = intelligent_scrape(URL)
    
    print("\n=== EXTRACTED INFORMATION ===")
    print(f"Title: {result['title']}")
    print(f"Description: {result['description']}")
    print(f"Method Used: {result.get('method', 'Unknown')}")
    
    if result.get('structured_info'):
        print("\n=== STRUCTURED INFO ===")
        for key, value in result['structured_info'].items():
            if isinstance(value, list):
                print(f"{key.replace('_', ' ').title()}: {', '.join(value)}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\nContent Length: {result['content_length']} characters")
    print(f"\n=== FULL CONTENT ===")
    print(result['full_content'])
    
    if result.get('note'):
        print(f"\nNote: {result['note']}")