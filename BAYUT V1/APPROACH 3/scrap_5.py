from re import search

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time
import random
from query import generate_bayut_url

my_query = "3 bedroom apartment for rent"
print("------------------------------")
URL = generate_bayut_url(my_query)
print(URL)
print("==============================")


# --- Configuration ---
#URL = "https://www.bayut.com/to-rent/property/dubai/"
search_location = "satwa"

# search_location = 'Jumeirah Village Circle'
# NUM_PROPERTIES = 500

st_time = time.time()

# # Setup Chrome options
# chrome_options = Options()
# # chrome_options.add_argument("--headless")  # Run in background (remove if you want to see browser)
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1920,1080")

# driver.get(URL)
# === User-Agent Rotation ===
USER_AGENTS = [

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6943.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6666.66 Safari/537.36 Edg/129.0.2792.77",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6600.123 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0.3 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/127.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6666.88 Safari/537.36 OPR/95.0.4638.41",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.77 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.123 Safari/537.36",
    "Mozilla/5.0 (X11; Arch Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6600.99 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.88 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/127.0.6533.88 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro Build/AP2A.240605.008) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.66 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6600.55 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; OnePlus 12 Build/OPP1.240520.003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6666.66 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-T875 Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36 Edg/127.0.2661.87",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6600.99 Safari/537.36 OPR/94.0.4606.85",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.88 Safari/537.36 Edg/127.0.2651.99",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.1",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.78 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.99 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 15623.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36",
    "Mozilla/5.0 (Windows NT 12.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.7000.50 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux Mint 21; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6605.80 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Xiaomi 13 Ultra Build/UP1A.231005.007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6666.72 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.7000.10 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; ARM; Surface Pro X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6602.40 Safari/537.36 Edg/128.0.2700.50",
    "Mozilla/5.0 (X11; FreeBSD amd64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6534.80 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; HUAWEI P50 Build/HUAWEIP50) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6488.90 Mobile Safari/537.36",
    "Mozilla/5.0 (PlayStation 5 3.20) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"
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
    # options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")

    return options

# Use with undetected-chromedriver
# driver = uc.Chrome(options=options)


chrome_options = get_chrome_options()
# Initialize the Chrome driver with webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(URL)



# Wait for page to load
wait = WebDriverWait(driver, 10)


# ---------------------------------------------------------------------------------------------------------
# Page clearing

# # Wait for page to load
time.sleep(2)

try:
    # Wait for the close button (X) inside the stories banner
    close_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "View Stories")]/following-sibling::div[contains(@class, "_37d9afbd")]'))
    )
    close_btn.click()
    print("✅ 'View Stories from TruBrokers' banner closed")
except Exception as e:
    print("❌ Story banner not found or already closed:", str(e))


try:
    # Wait for modal to appear
    modal = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Agent stories onboarding dialog"]'))
    )
    # Click on body or outside to close
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    print("✅ Story modal dismissed by clicking outside")
except:
    pass  # No modal


# ---------------------------------------------------------------------------------------------------------
# Filter the location

# --- Step 1: Find and click the Location Filter ---
try:
    location_filter = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Location filter"]'))
    )
    location_filter.click()
    print("✅ Clicked on Location Filter")
except Exception as e:
    print("❌ Could not click location filter:", e)
    driver.quit()
    exit()

# --- Step 2: Find the input field inside the filter ---
# After clicking, an input appears (usually in a dropdown)
try:
    # Wait for input to appear (it's likely the first input in the filter area)
    location_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Location filter"]//input'))
    )
    # Clear the input using Ctrl+A + Backspace (or Delete)
    location_input.send_keys("\ue009a")  # Ctrl+A to select all
    location_input.send_keys("\ue003")  # Delete (or use \ue00C for BACKSPACE)
    location_input.clear()
    location_input.send_keys(search_location)
    print(f"✅ Typed {search_location}")
except Exception as e:
    print("❌ Could not find input field:", e)
    driver.quit()
    exit()

# --- Step 3: Wait for dropdown suggestions ---
time.sleep(2)  # Let suggestions load (AJAX)

# --- Step 4: Click the correct suggestion ---
# Example: Click span with text "Jumeirah Village Circle"
# try:
#     suggestion = wait.until(
#         EC.element_to_be_clickable((By.XPATH, '//span[@class="_98caf06c _26717a45" and text()="Jumeirah Village Circle"]'))
#     )
#     suggestion.click()
#     print("✅ Selected 'Jumeirah Village Circle'")
# except Exception as e:
#     print("❌ Could not select suggestion:", e)
#     # Fallback: Try first suggestion
#     try:
#         first_suggestion = driver.find_element(By.XPATH, '//span[@class="_98caf06c _26717a45"]')
#         first_suggestion.click()
#         print("✅ Fallback: Clicked first suggestion")
#     except:
#         pass


try:
    first_suggestion = driver.find_element(By.XPATH, '//span[@class="_98caf06c _26717a45"]')
    first_suggestion.click()
    print("✅ Selected: Clicked first suggestion")
except Exception as e:
    print("❌ Could not select suggestion:", e)
    pass


# ---------------------------------------------------------------------------------------------------------
# Page parsing


# --- Wait for the property list container to appear ---
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//script[@type="application/ld+json"]'))
    )
    print("✅ Property list container loaded.")
    print('Loading Time:', time.time() - st_time)
except Exception as e:
    print("❌ Timeout: Container not found:", str(e))
    print("Page source snippet:", driver.page_source[:1000])
    driver.quit()
    exit()

# Give extra time for cards to render
#time.sleep(5)


# --- Find all JSON-LD scripts ---
scripts = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')

item_list_element = None

for script in scripts:
    try:
        text = script.get_attribute("innerHTML")
        data = json.loads(text)

        # Look for the Page-Level JSON with "ItemList" in @type and has "itemListElement"
        if (
            isinstance(data, dict) and
            isinstance(data.get("@type"), list) and
            "ItemList" in data["@type"] and
            "itemListElement" in data
        ):
            item_list_element = data["itemListElement"]
            break  # Found it

    except json.JSONDecodeError:
        continue

# print(json.dumps(item_list_element, indent=4))


data = []
for item in item_list_element:
    try:
        ent = item.get("mainEntity", {})

        # Skip if no entity
        if not ent:
            continue

        # Name
        name = ent.get("name", "N/A")

        # Link
        url = ent.get("url", "N/A")

        # Type: Extract from @type list
        types = ent.get("@type", [])
        prop_type = types[1]
        # if isinstance(types, str):
        #     types = [types]
        # prop_type = next((t for t in types if t in ["Apartment", "Villa", "House", "Townhouse"]), "Other")

        floorSize = ent.get("floorSize", {})
        size = floorSize.get("value", "N/A") if isinstance(floorSize, dict) else "N/A"

        # Price: Dig into offers → priceSpecification
        price = "N/A"
        offers = ent.get("offers", [])
        if isinstance(offers, list) and offers:
            price_spec = offers[0].get("priceSpecification", {})
            price = price_spec.get("price", "N/A")
        elif isinstance(offers, dict):
            price_spec = offers.get("priceSpecification", {})
            price = price_spec.get("price", "N/A")

        # Beds
        rooms = ent.get("numberOfRooms", {})
        beds = rooms.get("value", "N/A") if isinstance(rooms, dict) else "N/A"

        # Baths
        baths = ent.get("numberOfBathroomsTotal", "N/A")

        # Location
        address = ent.get("address", {})
        region = address.get("addressRegion", "N/A") if isinstance(address, dict) else "N/A"
        location = address.get("addressLocality", "N/A") if isinstance(address, dict) else "N/A"

        property_no = item.get("position", int)

        data.append({
            "PropertyNo": property_no,
            "Name": name,
            "Price": price,
            "Type": prop_type,
            "Beds": beds,
            "Baths": baths,
            "Region": region,
            "Location": location,
            "Size": size,
            "Link": url
        })
    except Exception as e:
        print("Error parsing item:", e)
        continue

df = pd.DataFrame(data)
print(df.to_string(index=False))
# ---------------------------------------------------------------------------------------------------------
print('END-----------')
print('Total time:', time.time()-st_time)
driver.quit()














