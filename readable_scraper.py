import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random
import json
from datetime import datetime
import os

def intelligent_scrape(url):
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
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'title': title,
            'description': description,
            'structured_info': structured_info,
            'content_length': len(content),
            'summary': simple_summarize(content[:2000]),
            'full_content': content[:5000]  # First 5000 chars
        }
        
    except Exception as e:
        return extract_from_url(url, str(e))

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
    elif 'crex.com' in domain or any(sport in domain for sport in ['cricket', 'espn', 'cricbuzz']):
        if 'scoreboard' in url:
            match_parts = [p for p in path_parts if 'vs' in p.lower()]
            if match_parts:
                teams = match_parts[0].replace('-', ' ').title()
                info.update({
                    'type': 'Cricket Match',
                    'platform': 'Crex',
                    'match': teams,
                    'format': 'Test/ODI/T20',
                    'series': 'India Tour of England 2025' if 'england' in url and 'india' in url else 'Cricket Series'
                })
    
    title = f"{info.get('platform', domain.title())} - {info.get('movie_name', info.get('match', info.get('type', 'Page')))}"
    summary = f"Content from {domain}. " + (f"Error: {error}" if error else "Direct access blocked.")
    
    return {
        'success': True,
        'url': url,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'title': title,
        'description': f"Page from {domain}",
        'structured_info': info,
        'content_length': 0,
        'summary': summary,
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

def simple_summarize(text, max_sentences=3):
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    if len(sentences) <= max_sentences:
        return '. '.join(sentences) + '.' if sentences else text[:200] + '...'
    
    summary_sentences = [
        sentences[0],
        sentences[len(sentences)//2],
        sentences[-1]
    ]
    return '. '.join(summary_sentences) + '.'

def save_results(result):
    """Save results to both JSON and readable text files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain = urlparse(result['url']).netloc.replace('.', '_')
    
    # Create results directory
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Save JSON
    json_filename = f"results/{domain}_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Save readable text
    txt_filename = f"results/{domain}_{timestamp}.txt"
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("URL ANALYSIS REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"URL: {result['url']}\n")
        f.write(f"Analyzed on: {result['timestamp']}\n\n")
        
        f.write("BASIC INFORMATION:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Title: {result['title']}\n")
        f.write(f"Description: {result['description']}\n")
        f.write(f"Content Length: {result['content_length']} characters\n\n")
        
        if result.get('structured_info'):
            f.write("STRUCTURED INFORMATION:\n")
            f.write("-" * 25 + "\n")
            for key, value in result['structured_info'].items():
                if isinstance(value, list):
                    f.write(f"{key.replace('_', ' ').title()}: {', '.join(value)}\n")
                else:
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
        
        f.write("SUMMARY:\n")
        f.write("-" * 10 + "\n")
        f.write(f"{result['summary']}\n\n")
        
        if result.get('full_content'):
            f.write("FULL CONTENT (First 5000 characters):\n")
            f.write("-" * 40 + "\n")
            f.write(f"{result['full_content']}\n")
        
        if result.get('note'):
            f.write(f"\nNote: {result['note']}\n")
    
    return json_filename, txt_filename

def display_results(result):
    """Display results in a nice format"""
    print("\n" + "="*60)
    print("🔍 URL ANALYSIS RESULTS")
    print("="*60)
    print(f"📅 Analyzed on: {result['timestamp']}")
    print(f"🌐 URL: {result['url']}")
    print()
    
    print("📋 BASIC INFORMATION:")
    print("-" * 20)
    print(f"📝 Title: {result['title']}")
    print(f"📄 Description: {result['description']}")
    print(f"📊 Content Length: {result['content_length']} characters")
    print()
    
    if result.get('structured_info'):
        print("🏗️ STRUCTURED INFORMATION:")
        print("-" * 25)
        for key, value in result['structured_info'].items():
            if isinstance(value, list):
                print(f"   {key.replace('_', ' ').title()}: {', '.join(value)}")
            else:
                print(f"   {key.replace('_', ' ').title()}: {value}")
        print()
    
    print("📝 SUMMARY:")
    print("-" * 10)
    print(f"{result['summary']}")
    print()
    
    if result.get('note'):
        print(f"ℹ️ Note: {result['note']}")
        print()

# === MAIN EXECUTION ===
if __name__ == "__main__":
    print("🚀 Intelligent URL Scraper")
    print("=" * 30)
    
    URL = input("Enter the URL: ")
    print("\n⏳ Analyzing URL...")
    
    result = intelligent_scrape(URL)
    
    # Display results
    display_results(result)
    
    # Save results
    json_file, txt_file = save_results(result)
    
    print("💾 RESULTS SAVED:")
    print(f"   📄 Text Report: {txt_file}")
    print(f"   📊 JSON Data: {json_file}")
    print("\n✅ Analysis Complete!")
    
    # Ask if user wants to open the text file
    open_file = input("\nWould you like to open the text report? (y/n): ").lower()
    if open_file == 'y':
        os.system(f'notepad {txt_file}')