import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_driver():
    try:
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logger.error(f"❌ Driver failed: {e}")
        return None

def extract_query_params(query):
    prompt = f"""
    Extract for Find Properties UAE:
    - location: 'dubai', 'sharjah', etc.
    - property_type: 'apartments', 'villas'
    - purpose: 'for-rent' or 'for-sale'

    Query: "{query}"

    Return JSON:
    {{"location": "dubai", "property_type": "apartments", "purpose": "for-rent"}}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text: text = text.split("```json")[1].split("```")[0]
        import json
        return json.loads(text)
    except:
        return {"location": "dubai", "property_type": "properties", "purpose": "for-rent"}

def build_urls(params):
    base = "https://findproperties.ae"
    loc = params["location"]
    ptype = params["property_type"]
    purpose = params["purpose"]
    return [
        f"{base}/{purpose}/{ptype}/{loc}",
        f"{base}/{purpose}/{loc}",
        f"{base}/search?location={loc}&purpose={purpose.replace('for-', '')}",
        f"{base}/{purpose}/properties"
    ]

def extract_properties(soup, source_url):
    results = []
    cards = soup.select("div.property-card, .listing, .card") or soup.find_all("div", class_=lambda x: x and "property" in str(x).lower())
    
    if not cards:
        text = soup.get_text()
        matches = re.findall(r'([^.\n]*AED[^.\n]*)', text, re.IGNORECASE)[:10]
        for m in matches:
            results.append({
                "title": "Property Listed",
                "price": re.search(r'AED[\s\d,]+', m).group() if re.search(r'AED[\s\d,]+', m) else "Price on request",
                "location": "UAE",
                "description": m[:80] + "...",
                "link": source_url,
                "source": "Find Properties"
            })
        return results

    for card in cards[:20]:
        try:
            title = card.find(['h2','h3']) or card.find(class_=lambda x: x and 'title' in str(x).lower())
            title = title.get_text(strip=True) if title else "Property Available"

            price = "Price on request"
            for pat in [r'AED[\s\d,]+', r'[\d,]+\s*AED']: 
                if re.search(pat, card.get_text(), re.IGNORECASE):
                    price = re.search(pat, card.get_text(), re.IGNORECASE).group(); break

            location = "UAE"
            for loc in ['Dubai', 'Sharjah', 'Abu Dhabi']: 
                if loc.lower() in card.get_text().lower(): 
                    location = loc; break

            link = card.find('a', href=True)
            link = link['href'] if link else source_url
            if link.startswith('/'): link = f"https://findproperties.ae{link}"

            results.append({
                "title": title,
                "price": price,
                "location": location,
                "description": card.get_text()[:100] + "...",
                "link": link,
                "source": "Find Properties"
            })
        except: continue
    return results

def crawl_find_properties(query):
    logger.info(f"🚀 Searching Find Properties: {query}")
    params = extract_query_params(query)
    driver = create_driver()
    if not driver: return []

    all_results = []
    for url in build_urls(params):
        try:
            driver.get(url)
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = extract_properties(soup, url)
            
            # ✅ Fix: Har property ki location ko query ki location se override karo agar nahi extract hui
            for prop in results:
                if not any(loc in prop["location"].lower() for loc in ['dubai', 'sharjah', 'abu dhabi', 'ajman', 'ras al khaimah']):
                    prop["location"] = params["location"].title()  # e.g., "abu dhabi" → "Abu Dhabi"

            all_results.extend(results)
            if all_results: break
        except: continue

    driver.quit()
    logger.info(f"✅ Found {len(all_results)} from Find Properties")
    return all_results[:60]

def main():
    query = input("Enter your property search query (e.g., 'apartments for rent in Dubai'): ").strip()
    if not query:
        query = "apartments for rent in Dubai"  
    print("\n🔍 Searching...\n")
    results = crawl_find_properties(query)
    
    if results:
        print(f"🎯 Found {len(results)} properties:\n")
        for i, prop in enumerate(results, 1):
            print(f"{i}. {prop['title']}")
            print(f"   💰 {prop['price']}")
            print(f"   📍 {prop['location']}")
            print(f"   📝 {prop['description']}")
            print(f"   🔗 {prop['link']}")
            print("-" * 60)
    else:
        print("❌ No properties found. Check your internet, site structure, or API key.")


if __name__ == "__main__":
    main()