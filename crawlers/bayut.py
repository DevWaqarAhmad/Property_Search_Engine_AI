import requests
import time
import os
import re
import json
import random
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

PROXY_CONFIGS = [
    {
        "name": "Rotating",
        "host": "rotating-residential.proxyseller.com",
        "port": 9000,
        "username": "5d0f603c340dc73f",
        "password": "olupxF9l"
    },
    {
        "name": "Premium",
        "host": "premium-residential.proxyseller.com",
        "port": 8080,
        "username": "5d0f603c340dc73f",
        "password": "olupxF9l"
    }
]


class BayutCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        self.proxy_working = self.test_all_proxies()  # Try all proxies

    def setup_headers(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        self.headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_proxy_dict(self, config):
        proxy_url = f"http://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
        return {'http': proxy_url, 'https': proxy_url}

    def test_proxy(self, config):
        try:
            proxies = self.get_proxy_dict(config)
            response = self.session.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                timeout=10,
                headers={"User-Agent": self.headers['User-Agent']}
            )
            if response.status_code == 200:
                print(f"✅ {config['name']} WORKING! 🆔 {response.json()['origin']}")
                return proxies
        except Exception as e:
            print(f"❌ {config['name']} FAILED: {str(e)[:50]}...")
        return None

    def test_all_proxies(self):
        print("🔄 Testing all proxies...")
        for config in PROXY_CONFIGS:
            proxies = self.test_proxy(config)
            if proxies:
                self.proxies = proxies
                return True
        print("⚠️  No proxy working. Using direct connection.")
        return False

    def extract_query_params(self, query):
        prompt = f"Extract JSON: location, property_type, bedrooms, max_price, purpose from '{query}'"
        try:
            response = gemini_model.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text: text = text.split("```json")[1].split("```")[0]
            params = json.loads(text)
            params["purpose"] = "to-rent" if params.get("purpose") == "rent" else "for-sale"
            return params
        except:
            return {"location": "dubai", "property_type": "apartment", "purpose": "to-rent"}

    def build_search_url(self, params):
        base_url = "https://www.bayut.com"
        location_map = {"marina": "dubai-marina", "jbr": "jumeirah-beach-residence-jbr", "downtown": "downtown-dubai"}
        location = location_map.get(params.get("location", "").lower(), params["location"].lower().replace(" ", "-"))
        url = f"{base_url}/{params['purpose']}/{params['property_type'].lower()}/{location}/"
        if params.get("bedrooms") or params.get("max_price"):
            query = []
            if params.get("bedrooms"): query.append(f"beds_min={params['bedrooms']}&beds_max={params['bedrooms']}")
            if params.get("max_price"): query.append(f"price_max={int(params['max_price'])}")
            url += "?" + "&".join(query)
        return url

    def scrape_properties(self, url):
        print(f"🔍 Fetching: {url}")
        time.sleep(random.uniform(3, 6))
        self.setup_headers()

        # Use proxy if available, else direct
        proxies = self.proxies if self.proxy_working else None

        try:
            response = self.session.get(url, headers=self.headers, proxies=proxies, timeout=30, verify=False)
            print(f"📡 Status: {response.status_code} | Via {'Proxy' if proxies else 'Direct'}")
            if response.status_code == 200:
                return self.parse_properties(response.text)
            elif response.status_code in [403, 429]:
                print("🚫 Blocked! Switching to direct.")
                return self.scrape_direct_fallback(url)
        except Exception as e:
            print(f"⚠️  Request failed: {e}")
            return self.scrape_direct_fallback(url)
        return []

    def scrape_direct_fallback(self, url):
        print("🔁 Falling back to direct connection...")
        try:
            time.sleep(5)
            response = self.session.get(url, headers=self.headers, timeout=30, verify=False)
            if response.status_code == 200:
                return self.parse_properties(response.text)
        except:
            pass
        return []

    def parse_properties(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        # Extract JSON-LD data
        script = soup.find("script", {"type": "application/ld+json"})
        json_data = {}
        if script:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get("url"):
                            json_data[item["url"]] = item
            except:
                pass

        # Find cards
        cards = soup.select('article[data-testid="property-card"], [class*="card"]')
        if not cards:
            print("🔧 Fallback: searching by keywords...")
            cards = soup.find_all(string=re.compile("AED|Bed|Bath", re.I))
            cards = [c.find_parent('article') or c.find_parent('div') for c in cards]
            cards = [c for c in cards if c]

        properties = []
        for card in cards[:10]:
            try:
                prop = self.extract_property(card, json_data)
                if prop and "Not found" not in prop["title"]:
                    properties.append(prop)
            except:
                continue
        return properties

    def extract_property(self, card, json_data):
        soup = BeautifulSoup(str(card), 'html.parser')
        link_tag = soup.find('a', href=True)
        link = link_tag['href'] if link_tag else "#"
        link = link if link.startswith("http") else "https://www.bayut.com" + link

        # Use JSON-LD if available
        if link in json_data:
            data = json_data[link]
            price_tag = soup.find(string=re.compile(r'AED', re.I))
            price = price_tag.parent.get_text(strip=True) if price_tag else "AED Price on Request"
            return {
                "title": data.get("name", "Not found"),
                "price": price,
                "location": data["address"].get("addressLocality", "UAE"),
                "bedrooms": data["numberOfRooms"]["value"] if isinstance(data["numberOfRooms"], dict) else "N/A",
                "bathrooms": data.get("numberOfBathroomsTotal", "N/A"),
                "area": data["floorSize"]["value"].replace(",", "") if isinstance(data["floorSize"], dict) else "N/A",
                "link": link,
                "image": data.get("image", "Not found"),
                "description": f"{data['numberOfRooms']['value']} Bed | {data.get('numberOfBathroomsTotal', 'N/A')} Bath | {data['floorSize']['value']} sqft"
            }

        # Fallback parsing
        title = self.safe_text(soup, 'h2, h3, a[href*="/property/"]')
        price = self.safe_text(soup, '[data-testid*="price"], *:contains("AED")') or "AED Price on Request"
        location = self.safe_text(soup, '*:contains("Dubai")|*:contains("JBR")') or "Dubai"
        text = soup.get_text()
        beds = re.search(r'(\d+)\s*bed', text, re.I)
        baths = re.search(r'(\d+)\s*bath', text, re.I)
        area = re.search(r'(\d{1,4}(?:,\d{3})*)\s*sq\.?\s*ft', text, re.I)

        return {
            "title": title,
            "price": price,
            "location": location,
            "bedrooms": beds.group(1) if beds else "N/A",
            "bathrooms": baths.group(1) if baths else "N/A",
            "area": area.group(1).replace(",", "") if area else "N/A",
            "link": link,
            "image": self.safe_attr(soup, 'img[data-src], img[src]', 'src') or "Not found",
            "description": f"{beds.group(1) if beds else 'N/A'} Bed | {baths.group(1) if baths else 'N/A'} Bath | {area.group(1).replace(',', '') if area else 'N/A'} sqft"
        }

    def safe_text(self, soup, selector):
        try:
            if selector.startswith('*:contains'):
                txt = selector.split('("')[1].split('")')[0]
                match = soup.find(string=re.compile(txt, re.I))
                return match.strip() if match else "Not found"
            el = soup.select_one(selector)
            return el.get_text(strip=True) if el else "Not found"
        except:
            return "Not found"

    def safe_attr(self, soup, selector, attr):
        try:
            el = soup.select_one(selector)
            return el.get(attr, '') if el else "Not found"
        except:
            return "Not found"

    def search_properties(self, query):
        print(f"\n🚀 SEARCHING: '{query}'")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        params = self.extract_query_params(query)
        url = self.build_search_url(params)
        print(f"🔗 URL: {url}")
        results = self.scrape_properties(url)
        self.pretty_print(results)
        return results

    def pretty_print(self, results):
        if not results:
            print("📭 No properties found.")
            return
        print(f"\n🎯 Found {len(results)} properties:\n")
        for i, p in enumerate(results, 1):
            print(f"📌 [{i}] {p['title']}")
            print(f"   💵 {p['price']} | 📍 {p['location']}")
            print(f"   🛏️  {p['description']}")
            print(f"   🔗 {p['link']}")
            if p['image'] != "Not found":
                print(f"   🖼️  Image: {p['image']}")
            print("   ─────────────────────────")

def bayut_property_search(query):
    try:
        crawler = BayutCrawler()
        return crawler.search_properties(query)
    except Exception as e:
        print(f"💥 Error: {e}")
        return []

# Test
if __name__ == "__main__":
    print("🏠 BAYUT CRAWLER v5.0 | PROXY + JSON-LD + FALLBACK")
    queries = ["rent apartments in abu dhabi"]
    for q in queries:
        bayut_property_search(q)
        time.sleep(7)