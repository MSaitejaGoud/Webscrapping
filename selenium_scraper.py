from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os

# === CONFIG ===
URL = input("Enter the URL: ")
CHROMEDRIVER_PATH = os.path.join(os.path.dirname(__file__), "drivers", "chromedriver.exe")

# === SETUP SELENIUM ===
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
service = Service(CHROMEDRIVER_PATH)

try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    time.sleep(3)
    html = driver.page_source
    driver.quit()
except Exception as e:
    print(f"Error with Selenium: {e}")
    exit(1)

# === PARSE WITH BEAUTIFULSOUP ===
soup = BeautifulSoup(html, 'html.parser')

# === CONTENT EXTRACTION ===
title = soup.title.string.strip() if soup.title else "No title found"
desc_tag = soup.find("meta", attrs={"name": "description"})

# Remove unwanted elements
for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
    element.decompose()

# Extract main content
content_selectors = ['article', '.content', '.post', '.entry', 'main', '.article-body']
main_content = None

for selector in content_selectors:
    main_content = soup.select_one(selector)
    if main_content:
        break

if not main_content:
    main_content = soup.find('body')

# Get text content
if main_content:
    text = main_content.get_text(separator=' ', strip=True)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    content = ' '.join(lines)
else:
    content = "Could not extract content"

# === SUMMARIZATION ===
def simple_summarize(text, max_sentences=3):
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    if len(sentences) <= max_sentences:
        return '. '.join(sentences) + '.'
    
    summary_sentences = [
        sentences[0],
        sentences[len(sentences)//2],
        sentences[-1]
    ]
    return '. '.join(summary_sentences) + '.'

print("\n=== EXTRACTED INFORMATION (Selenium) ===")
print(f"Title: {title}")
print(f"Description: {desc_tag['content'] if desc_tag else 'Not found'}")
print(f"\nContent Length: {len(content)} characters")
print(f"\n=== SUMMARY ===")
print(simple_summarize(content[:2000]))