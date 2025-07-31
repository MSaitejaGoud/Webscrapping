import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random

def test_msn_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        print(f"Testing URL: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No title found"
            
            # Extract article content
            article_selectors = ['article', '.article-body', '.content', 'main', '[data-module="ArticleBody"]']
            content = ""
            
            for selector in article_selectors:
                article = soup.select_one(selector)
                if article:
                    content = article.get_text(separator=' ', strip=True)
                    break
            
            if not content:
                # Fallback to body content
                for element in soup(["script", "style", "nav", "header", "footer"]):
                    element.decompose()
                content = soup.get_text(separator=' ', strip=True)
            
            print("SUCCESS!")
            print(f"Title: {title}")
            print(f"Content Length: {len(content)} characters")
            print(f"First 500 chars: {content[:500]}...")
            
            return {
                'success': True,
                'title': title,
                'content': content,
                'content_length': len(content)
            }
        else:
            print(f"Failed with status code: {response.status_code}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    url = input("Enter MSN URL: ")
    result = test_msn_url(url)
    
    if result['success']:
        print("\n" + "="*50)
        print("ARTICLE EXTRACTED SUCCESSFULLY")
        print("="*50)
        print(f"Title: {result['title']}")
        print(f"Content Length: {result['content_length']} characters")
        print("\nFirst 1000 characters:")
        print("-" * 30)
        print(result['content'][:1000])
    else:
        print(f"\nFailed to extract: {result['error']}")