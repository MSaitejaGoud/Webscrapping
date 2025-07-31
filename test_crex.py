from url_scraper import intelligent_scrape

URL = "https://crex.com/scoreboard/QST/1NS/5th-Match/S/O/eng-vs-ind-5th-match-india-tour-of-england-2025/info"

result = intelligent_scrape(URL)

print("\n=== CREX CRICKET URL TEST ===")
print(f"Title: {result['title']}")
print(f"Description: {result['description']}")

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