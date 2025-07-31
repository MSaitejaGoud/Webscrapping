from url_scraper import intelligent_scrape
import time

def analyze_multiple_urls():
    urls = []
    print("Enter URLs (press Enter twice when done):")
    
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        urls.append(url)
    
    if not urls:
        print("No URLs provided!")
        return
    
    print(f"\n=== ANALYZING {len(urls)} URLs ===\n")
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url}")
        print("-" * 80)
        
        result = intelligent_scrape(url)
        
        print(f"Title: {result['title']}")
        print(f"Description: {result['description']}")
        print(f"Content Length: {result['content_length']} characters")
        
        if result.get('structured_info'):
            key_info = []
            for key, value in result['structured_info'].items():
                if key in ['type', 'platform', 'match', 'movie_name']:
                    key_info.append(f"{key}: {value}")
            if key_info:
                print(f"Key Info: {', '.join(key_info)}")
        
        print(f"Summary: {result['summary'][:150]}...")
        if result.get('note'):
            print(f"Note: {result['note']}")
        
        print("\n" + "="*80 + "\n")
        
        # Small delay between requests
        if i < len(urls):
            time.sleep(1)

if __name__ == "__main__":
    analyze_multiple_urls()