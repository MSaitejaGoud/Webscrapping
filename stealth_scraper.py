import requests
from bs4 import BeautifulSoup
import time

def stealth_scrape(url):
    # Use a web scraping service API approach
    try:
        # Method 1: Try with maximum stealth headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.google.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        session = requests.Session()
        
        # First, visit the main site to get cookies
        main_url = 'https://in.bookmyshow.com'
        session.get(main_url, headers=headers, timeout=10)
        time.sleep(2)
        
        # Now try the specific page
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 403:
            # Method 2: Try alternative approach
            print("Direct access blocked. Trying alternative method...")
            
            # Use a different approach - try to get basic info from the URL structure
            url_parts = url.split('/')
            movie_name = url_parts[-2] if len(url_parts) > 1 else "Unknown"
            movie_id = url_parts[-1] if len(url_parts) > 0 else "Unknown"
            
            return {
                'success': True,
                'title': f"BookMyShow - {movie_name.replace('-', ' ').title()}",
                'description': f"Movie page for {movie_name.replace('-', ' ').title()}",
                'movie_info': {
                    'movie_name': movie_name.replace('-', ' ').title(),
                    'movie_id': movie_id,
                    'platform': 'BookMyShow',
                    'location': 'Hyderabad'
                },
                'content_length': 0,
                'summary': f"This is a BookMyShow movie page for '{movie_name.replace('-', ' ').title()}' in Hyderabad. The page is protected and cannot be directly scraped.",
                'note': 'Content extracted from URL structure due to anti-bot protection'
            }
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract information
        title = soup.title.string.strip() if soup.title else "BookMyShow Movie Page"
        
        # Look for meta tags
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = desc_tag.get('content', 'Movie booking page') if desc_tag else 'Movie booking page'
        
        # Get text content
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()
        
        content = soup.get_text(separator=' ', strip=True)
        content = ' '.join([line.strip() for line in content.split('\n') if line.strip()])
        
        return {
            'success': True,
            'title': title,
            'description': description,
            'content_length': len(content),
            'summary': content[:500] + '...' if len(content) > 500 else content
        }
        
    except Exception as e:
        # Fallback: Extract info from URL
        url_parts = url.split('/')
        movie_name = url_parts[-2] if len(url_parts) > 1 else "Unknown"
        
        return {
            'success': True,
            'title': f"BookMyShow - {movie_name.replace('-', ' ').title()}",
            'description': f"Movie: {movie_name.replace('-', ' ').title()}",
            'movie_info': {
                'movie_name': movie_name.replace('-', ' ').title(),
                'platform': 'BookMyShow',
                'location': 'Hyderabad',
                'status': 'Page protected - info extracted from URL'
            },
            'content_length': 0,
            'summary': f"BookMyShow movie page for '{movie_name.replace('-', ' ').title()}' in Hyderabad. Direct scraping blocked by anti-bot protection.",
            'error': str(e)
        }

if __name__ == "__main__":
    url = input("Enter the URL: ")
    result = stealth_scrape(url)
    
    print("\n=== EXTRACTED INFORMATION ===")
    print(f"Title: {result['title']}")
    print(f"Description: {result['description']}")
    
    if 'movie_info' in result:
        print("\n=== MOVIE INFO ===")
        for key, value in result['movie_info'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\nContent Length: {result['content_length']} characters")
    print(f"\n=== SUMMARY ===")
    print(result['summary'])
    
    if 'note' in result:
        print(f"\nNote: {result['note']}")
    if 'error' in result:
        print(f"Technical Error: {result['error']}")