from url_scraper import intelligent_scrape

URL = "https://www.getyourguide.com/-l1148/?cmp=bing&cmp=bing&ad_id=77859371633610&adgroup_id=1245747322221011&bid_match_type=be&campaign_id=710107007&device=c&feed_item_id=&keyword=rajasthan&loc_interest_ms=1672&loc_physical_ms=144064&match_type=e&msclkid=747777ebab991f10da341f6243cd15f8&network=o&partner_id=CD951&target_id=kwd-77859605625959&utm_adgroup=lc%3D1148%3Arajasthan%7Cfn%3Df3%7Cci%3D937%3Athings%20to%20do&utm_campaign=dc%3D55%3Ain%7Clc%3D1148%3Arajasthan%7Cct%3Dcore%7Cln%3D29%3Aen%7Ctc%3Dall&utm_keyword=rajasthan&utm_medium=paid_search&utm_query=rajasthan&utm_source=bing"

result = intelligent_scrape(URL)

print("\n=== EXTRACTED INFORMATION ===")
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