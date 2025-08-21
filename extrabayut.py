import requests
import time
import os
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

def extract_query_params(query):
    """Use Gemini to extract search parameters"""
    prompt = f"""
    Extract: location (e.g., Dubai, Sharjah), property_type (apartment, villa, studio), bedrooms, max_price, purpose (rent/sale)
    Query: "{query}"
    Respond in JSON: {{ "location": "", "property_type": "", "bedrooms": null, "max_price": null, "purpose": "rent|sale" }}
    """
    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text: text = text.split("```json")[1].split("```")[0]
        elif "```" in text: text = text.split("```")[1].split("```")[0]

        import json
        params = json.loads(text)

        params["purpose"] = "to-rent" if params.get("purpose") == "rent" else "for-sale"
        p_type = params.get("property_type", "").lower()
        if "apartment" in p_type: params["property_type"] = "apartment"
        elif "villa" in p_type: params["property_type"] = "villa"
        else: params["property_type"] = "apartment"

        print("🧠 Gemini Params:", params)
        return params
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return {}

def build_url(params):
    """Build Bayut.com search URL"""
    base = "https://www.bayut.com"
    purpose = params.get("purpose", "to-rent")
    p_type = params.get("property_type", "apartment")
    location = params.get("location", "dubai").lower().replace(" ", "-")

    url = f"{base}/{purpose}/{p_type}/{location}/"

    query_parts = []
    if params.get("max_price"): query_parts.append(f"price_max={int(params['max_price'])}")
    if params.get("bedrooms"): query_parts.append(f"beds_min={params['bedrooms']}")

    if query_parts:
        url += "?" + "&".join(query_parts)

    return url

def scrape_with_scraperapi(url):
    """Scrape using ScraperAPI with .env key"""
    scraperapi_url = "https://api.scraperapi.com"
    payload = {
        "api_key": os.getenv("SCRAPERAPI_KEY"),
        "url": url,
        "render": "true",
        "country_code": "ae",
        "keep_headers": "true"
    }

    try:
        response = requests.get(scraperapi_url, params=payload, timeout=60)
        print(f"📡 ScraperAPI Status: {response.status_code}")

        if response.status_code != 200:
            print("❌ Failed to fetch page via ScraperAPI")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        cards = soup.find_all('article', attrs={'property-id': True})
        if not cards:
            cards = soup.find_all('div', {'data-testid': 'property-card'})

        print(f"✅ Found {len(cards)} property cards.")

        results = []
        for card in cards[:5]:
            try:
                title_elem = card.find('h2') or card.find('h3')
                title = title_elem.get_text(strip=True) if title_elem else "Not specified"

                price_elem = card.find(string=re.compile(r'AED|price', re.I))
                price = price_elem.strip() if price_elem else "Not listed"

                loc_elem = card.find('div', string=re.compile(r'Dubai|Sharjah|Abu Dhabi', re.I))
                location = loc_elem.get_text(strip=True) if loc_elem else "UAE"

                link_elem = card.find('a', href=True)
                href = link_elem['href'] if link_elem else "#"
                link = href if href.startswith("http") else f"https://www.bayut.com{href}"

                details = card.find_all(string=re.compile(r'^\d+\.?\d*$'))
                beds = details[0].strip() if len(details) > 0 else "N/A"
                baths = details[1].strip() if len(details) > 1 else "N/A"
                area = details[2].strip() if len(details) > 2 else "N/A"
                description = f"{beds} Beds | {baths} Baths | {area} sqft"

                results.append({
                    "title": title,
                    "price": price,
                    "location": location,
                    "description": description,
                    "link": link
                })
            except Exception as e:
                print(f"⚠️ Error parsing card: {e}")
                continue

        return results

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return []

def crawl_bayut(query):
    """Main function to scrape Bayut"""
    print("🚀 Starting Bayut scrape...")
    params = extract_query_params(query)
    if not params:
        print("❌ Could not extract query parameters.")
        return []

    url = build_url(params)
    print(f"🔗 Generated URL: {url}")

    results = scrape_with_scraperapi(url)

    if results:
        print(f"\n✅ Success! Found {len(results)} properties:")
        for i, prop in enumerate(results, 1):
            print(f"\n{i}. {prop['title']}")
            print(f"   💵 {prop['price']}")
            print(f"   📍 {prop['location']}")
            print(f"   📝 {prop['description']}")
            print(f"   🔗 {prop['link']}")
    else:
        print("❌ No properties found. Check API key or URL.")

    return results


if __name__ == "__main__":
    print("🧪 Testing Bayut Crawler with ScraperAPI...\n")

    test_queries = [
        "2 bedroom apartment in Dubai for rent under 100000 AED",
        "3 bed villa in Sharjah for sale",
        "studio in Al Nahda for rent"
    ]

    for i, q in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"🔍 TEST {i}: {q}")
        print("="*60)
        scrape_bayut(q)

    print("\n🎉 All tests completed!")