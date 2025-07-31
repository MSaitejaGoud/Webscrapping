import requests
from bs4 import BeautifulSoup
import time
import random

def advanced_scrape(url):
    # Multiple user agents to rotate
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    session = requests.Session()
    
    try:
        # Add delay to appear more human-like
        time.sleep(random.uniform(1, 3))
        
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.title.string.strip() if soup.title else "No title found"
        
        # Extract meta description
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = desc_tag.get('content', 'Not found') if desc_tag else 'Not found'
        
        # Extract movie-specific info for BookMyShow
        movie_info = {}
        
        # Try to find movie title
        movie_title_selectors = [
            'h1[data-testid="movie-title"]',
            '.movie-title',
            'h1.title',
            '.event-title h1',
            'h1'
        ]
        
        for selector in movie_title_selectors:
            movie_title = soup.select_one(selector)
            if movie_title:
                movie_info['movie_title'] = movie_title.get_text().strip()
                break
        
        # Try to find rating
        rating_selectors = [
            '.rating-value',
            '.imdb-rating',
            '[data-testid="rating"]',
            '.star-rating'
        ]
        
        for selector in rating_selectors:
            rating = soup.select_one(selector)
            if rating:
                movie_info['rating'] = rating.get_text().strip()
                break
        
        # Try to find genre
        genre_selectors = [
            '.genre',
            '[data-testid="genre"]',
            '.movie-genre'
        ]
        
        for selector in genre_selectors:
            genre = soup.select_one(selector)
            if genre:
                movie_info['genre'] = genre.get_text().strip()
                break
        
        # Get all text content
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()
        
        content = soup.get_text(separator=' ', strip=True)
        content = ' '.join([line.strip() for line in content.split('\n') if line.strip()])
        
        return {
            'success': True,
            'title': title,
            'description': description,
            'movie_info': movie_info,
            'content_length': len(content),
            'summary': content[:500] + '...' if len(content) > 500 else content
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Parsing failed: {str(e)}'
        }

if __name__ == "__main__":
    url = input("Enter the URL: ")
    result = advanced_scrape(url)
    
    if result['success']:
        print("\n=== EXTRACTED INFORMATION ===")
        print(f"Title: {result['title']}")
        print(f"Description: {result['description']}")
        
        if result['movie_info']:
            print("\n=== MOVIE INFO ===")
            for key, value in result['movie_info'].items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print(f"\nContent Length: {result['content_length']} characters")
        print(f"\n=== SUMMARY ===")
        print(result['summary'])
    else:
        print(f"Error: {result['error']}")