from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
import re

# ========================== HARD CODED VARIABLE ================
URL = "https://www.properties.market/ae/to-rent/property/"

search_location = "dubai"
MERGE_URL = f"https://www.properties.market/ae/to-rent/property/{search_location}"

st_time = time.time()

# ------------------- USER AGENTS -------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    # ... (rest of user agents)
]

def get_chrome_options():
    options = Options()
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return options

# Initialize driver
chrome_options = get_chrome_options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Opening Properties.market...")
driver.get(MERGE_URL)

wait = WebDriverWait(driver, 10)

# Wait for property cards to load
try:
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "property-grid")))
except Exception as e:
    print("❌ Property cards not loaded:", e)

# Get page source after waiting
time.sleep(3)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Find all property cards
property_cards = soup.find_all('div', class_='col-md-4 property-grid grid-full web-view')
print(f"✅ Total properties found: {len(property_cards)}")

data = []

for idx, card in enumerate(property_cards, 1):
    try:
        # --- TITLE ---
        title_span = card.find('span', attrs={'title': True})
        title = title_span['title'] if title_span else "N/A"

        # --- PRICE ---
        price_span = card.find('span', class_='price')
        price_text = price_span.get_text(strip=True) if price_span else "N/A"
        currency_span = card.find('span', class_='currency')
        currency = currency_span.get_text(strip=True) if currency_span else "AED"
        price = f"{currency} {price_text}" if price_text != "N/A" else "N/A"

        # --- LOCATION ---
        location_elem = card.find('div', class_='property-location')
        location = location_elem.get_text(strip=True) if location_elem else "N/A"

        # --- BEDS, BATHS, AREA using regex (most reliable) ---
        text_content = card.get_text()
        
        # Extract bedrooms
        bed_match = re.search(r'(\d+)\s*Bed', text_content)
        beds = f"{bed_match.group(1)} Bed" if bed_match else "N/A"

        # Extract bathrooms
        bath_match = re.search(r'(\d+)\s*Bath', text_content)
        baths = f"{bath_match.group(1)} Bath" if bath_match else "N/A"

        # Extract area
        area_match = re.search(r'([\d,]+)\s*sqft', text_content)
        area = f"{area_match.group(1)} sqft" if area_match else "N/A"

        # --- URL ---
        link_elem = card.find('a', href=True)
        url = "https://www.properties.market" + link_elem['href'] if link_elem else "N/A"

        # Append data
        data.append({
            "Title": title,
            "Price": price,
            "Location": location,
            "Bedrooms": beds,
            "Bathrooms": baths,
            "Area": area,
            "URL": url
        })

    except Exception as e:
        print(f"⚠️ Error parsing card {idx}: {e}")
        continue

# Create DataFrame
df = pd.DataFrame(data, columns=['Title', 'Price', 'Location', 'Bedrooms', 'Bathrooms', 'Area', 'URL'])
print(df.to_string(index=False))

print("\n✅ Scraping completed!")
print(f"Total time: {time.time() - st_time:.2f}s")
driver.quit()