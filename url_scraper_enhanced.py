import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random

def intelligent_scrape(url):
    # Try regular scraping first
    result = try_regular_scraping(url)
    
    # If content is too short or indicates JS loading, try Selenium
    if result['content_length'] < 100 or 'loading' in result.get('summary', '').lower():
        print("Regular scraping failed, trying Selenium...")
        selenium_result = try_selenium_scraping(url)
        if selenium_result and selenium_result['content_length'] > result['content_length']:
            return selenium_result
    
    return result

def try_regular_scraping(url):
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
            'summary': simple_summarize(content[:2000]),
            'method': 'Regular Scraping'
        }
        
    except Exception as e:
        return extract_from_url(url, str(e))

def try_selenium_scraping(url):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=options)
        except:
            print("Chrome driver not found, install ChromeDriver")
            return None
        
        driver.get(url)
        time.sleep(5)  # Wait for JS to load
        
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
            'summary': simple_summarize(content[:2000]),
            'method': 'Selenium Scraping'
        }
        
    except ImportError:
        print("Selenium not installed. Install with: pip install selenium")
        return None
    except Exception as e:
        print(f"Selenium scraping failed: {e}")
        return None

def extract_from_url(url, error=None):
    parsed = urlparse(url)
    domain = parsed.netloc
    path_parts = [p for p in parsed.path.split('/') if p]
    
    info = {'domain': domain, 'path_parts': path_parts}
    
    if 'community.boomi.com' in domain:
        if 'topic' in path_parts:
            topic_name = path_parts[-1].replace('-', ' ').title() if path_parts else 'Community Topic'
            info.update({
                'type': 'Community Forum',
                'platform': 'Boomi Community',
                'topic': topic_name,
                'category': 'Integration Platform Discussion'
            })
    
    title = f"{info.get('platform', domain.title())} - {info.get('topic', 'Page')}"
    summary = f"Content from {domain}. " + (f"Error: {error}" if error else "Direct access blocked.")
    
    return {
        'success': True,
        'title': title,
        'description': f"Page from {domain}",
        'structured_info': info,
        'content_length': 0,
        'summary': summary,
        'method': 'URL Structure Analysis',
        'note': 'Info extracted from URL structure'
    }

def extract_structured_data(soup, url):
    info = {}
    h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')[:3]]
    if h1_tags:
        info['headings'] = h1_tags
    return info

def simple_summarize(text, max_sentences=3):
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    if len(sentences) <= max_sentences:
        return '. '.join(sentences) + '.' if sentences else text[:200] + '...'
    
    summary_sentences = [sentences[0], sentences[len(sentences)//2], sentences[-1]]
    return '. '.join(summary_sentences) + '.'

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
    print(f"\n=== SUMMARY ===")
    print(result['summary'])
    
    if result.get('note'):
        print(f"\nNote: {result['note']}")