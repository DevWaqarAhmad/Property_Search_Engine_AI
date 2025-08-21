import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    """Create optimized Chrome driver for Property Finder"""
    try:
        logger.info("🔧 Creating Chrome driver for Property Finder...")
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ Chrome driver created!")
        return driver
    except Exception as e:
        logger.error(f"❌ Driver creation failed: {e}")
        return None

def extract_query_params(query):
    """Use Gemini to extract search parameters"""
    prompt = f"""
    Extract real estate parameters for Property Finder UAE:
    - location: (e.g., 'dubai-marina', 'downtown-dubai', 'sharjah')
    - property_type: ('apartment', 'villa', 'studio', 'penthouse', 'townhouse')
    - bedrooms: number (1,2,3,4,5)
    - max_price: AED amount
    - purpose: 'rent' or 'sale'

    Query: "{query}"

    Return only JSON:
    {{
        "location": "dubai",
        "property_type": "",
        "bedrooms": null,
        "max_price": null,
        "purpose": "rent"
    }}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        import json
        params = json.loads(text)
        if not params.get("purpose"):
            params["purpose"] = "rent" if any(w in query.lower() for w in ["rent", "rental"]) else "sale"
        if not params.get("location"):
            params["location"] = "dubai"
        return params
    except Exception as e:
        logger.error(f"❌ Gemini parsing failed: {e}")
        return {"location": "dubai", "property_type": "", "bedrooms": None, "max_price": None, "purpose": "rent"}

def build_property_finder_urls(params):
    """Build multiple URL patterns for Property Finder"""
    base = "https://www.propertyfinder.ae/en/search"
    purpose = params["purpose"]
    location = params["location"].replace(" ", "-").lower()
    bedrooms = params["bedrooms"]
    max_price = params["max_price"]
    prop_type = params["property_type"]

    purpose_param = "c=2" if purpose == "rent" else "c=1"
    location_param = f"l={location}"

    urls = [
        f"{base}?{purpose_param}&{location_param}",
        f"{base}?{purpose_param}&{location_param}&beds_min={bedrooms}" if bedrooms else None,
        f"{base}?{purpose_param}&{location_param}&price_max={max_price}" if max_price else None,
        f"{base}?{purpose_param}&{location_param}&t=apartment" if "apartment" in prop_type else None,
        f"{base}?{purpose_param}&{location_param}&t=villa" if "villa" in prop_type else None,
        "https://www.propertyfinder.ae/en/rent/apartments/dubai"  # Fallback
    ]
    return [url for url in urls if url]

def extract_properties_enhanced(soup, source_url):
    """Extract properties with multiple strategies"""
    results = []
    selectors = [
        'article[data-testid="property-card"]',
        'div[data-testid="property-card"]',
        '.property-card', '.listing-item', 'article.card'
    ]
    
    cards = []
    for sel in selectors:
        found = soup.select(sel)
        if found and len(found) > 1:
            cards = found
            break

    if not cards:
        text = soup.get_text()
        matches = re.findall(r'([^.\n]*AED[^.\n]*)', text, re.IGNORECASE)[:10]
        for i, m in enumerate(matches):
            results.append({
                "title": f"Property #{i+1}",
                "price": re.search(r'AED[\s\d,]+', m, re.IGNORECASE).group() if re.search(r'AED[\s\d,]+', m) else "Price on request",
                "location": "UAE",
                "description": m[:100] + "...",
                "link": source_url,
                "source": "Property Finder"
            })
        return results

    for card in cards[:20]: 
        try:
            card_text = card.get_text(" ", strip=True)
            title_elem = card.find(['h2', 'h3']) or card.find(class_=lambda x: x and 'title' in str(x).lower())
            title = title_elem.get_text(strip=True) if title_elem and len(title_elem.get_text(strip=True)) > 5 else "Property Available"

            price = "Price on request"
            for pat in [r'AED[\s\d,]+(?:\s*per\s*month)?', r'[\d,]+\s*AED']:
                match = re.search(pat, card_text, re.IGNORECASE)
                if match: price = match.group().strip(); break

            location = "UAE"
            for loc in ['Dubai', 'Sharjah', 'Abu Dhabi', 'Marina', 'Downtown', 'JBR']:
                if loc.lower() in card_text.lower():
                    location = loc; break

            link_elem = card.find('a', href=True)
            link = link_elem['href'] if link_elem else source_url
            if link.startswith('/'): link = f"https://www.propertyfinder.ae{link}"

            results.append({
                "title": title,
                "price": price,
                "location": location,
                "description": card_text[:120] + "...",
                "link": link,
                "source": "Property Finder"
            })
        except: continue

    return results

def crawl_property_finder(query):
    logger.info(f"🚀 Searching Property Finder for: {query}")
    params = extract_query_params(query)
    driver = create_driver()
    if not driver: return []

    all_results = []
    urls = build_property_finder_urls(params)

    for url in urls:
        try:
            driver.get(url)
            time.sleep(5)

            for page in range(3):
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                results = extract_properties_enhanced(soup, url)

                # ✅ Fix: Agar location "UAE" hai ya vague hai, to query se location set karo
                for prop in results:
                    if prop["location"] in ["UAE", "Dubai", "Sharjah", "Abu Dhabi"]:  # incomplete ya default
                        extracted_loc = params["location"].replace("-", " ").title()
                        if "dubai" in extracted_loc.lower():
                            prop["location"] = "Dubai"
                        elif "sharjah" in extracted_loc.lower():
                            prop["location"] = "Sharjah"
                        elif "abu dhabi" in extracted_loc.lower():
                            prop["location"] = "Abu Dhabi"
                        else:
                            prop["location"] = extracted_loc

                all_results.extend(results)

                try:
                    next_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Next']"))
                    )
                    next_btn.click()
                    time.sleep(3)
                except:
                    break

            if all_results: break
        except: continue

    driver.quit()
    logger.info(f"✅ Found {len(all_results)} raw results from Property Finder")
    return all_results[:60]


# def main():
#     query = input("Search property: ")
#     results = crawl_property_finder(query)
#     for r in results:
#         print(r["title"], r["price"], r["location"], r["link"])

# if __name__ == "__main__":
#     main()