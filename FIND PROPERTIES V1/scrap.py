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
from query import generate_find_properties_url

my_query = "for sale villa in 6 bedrooms"
min_price= ""
max_price = "100,000"
bathrooms = "4"
print("------------------------------")
URL = generate_find_properties_url(my_query)
print(URL)
print("==============================")
#URL ="https://findproperties.ae/for-rent/properties/uae"
search_location = "abu dhabi"


st_time = time.time()



#-------------------USER AGENTS-------------------------
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
#------------------ CHROME OPTIONS ----------------------
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
    #options.add_argument("--headless")

    return options

#------------------ WEBSITE PAGE OPENING ----------------------
chrome_options = get_chrome_options()
# Initialize the Chrome driver with webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(URL)

wait = WebDriverWait(driver, 10)

# ------------------- REMOVE EXISTING LOCATION (IF ANY) --------------------------
# try:
#     # Wait and click on the CancelIcon (cross button) if present
#     cancel_icon = wait.until(
#         EC.element_to_be_clickable((By.XPATH, '//svg[@data-testid="CancelIcon"]'))
#     )
#     cancel_icon.click()
#     print("✅ Removed existing location (e.g., Dubai)")
# except Exception as e:
#     print(" No existing location found or could not remove:", e)
#     # Continue anyway — no error needed here

# ------------------- CLICK ON LOCATION INPUT --------------------------
try:
    location_input = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//input[@id="multiple-limit-tags"]'))
    )
    location_input.click()
    print("✅ Clicked on Location Input Field")
except Exception as e:
    print("❌ Could not click location input:", e)
    driver.quit()
    exit()

# ------------------- CLEAR AND TYPE NEW LOCATION --------------------------
try:
    location_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="multiple-limit-tags"]'))
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

# ------------------- CLICK ON FIRST SUGGESTION FROM DROPDOWN --------------------------
try:
    # Wait for the first suggestion in dropdown using XPATH
    first_suggestion = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//li[@class="MuiAutocomplete-option"][1]'))
    )
    first_suggestion.click()
    print("✅ Clicked on first suggestion from dropdown using XPATH")
except Exception as e:
    print("❌ Could not click first suggestion:", e)
    driver.quit()
    exit()
time.sleep(2)

#-----------------Applying Price Filter------------------------------------------------
#-------------------------MIN PRICE------------------------------
if min_price is not None:
    try:
        min_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="priceFrom"]'))
        )
        min_input.clear()
        min_input.send_keys(str(min_price))
        print(f"✅ Min price set to {min_price} AED")
    except Exception as e:
        print("❌ Could not set min price:", e)

#--------------------MAX PRICE----------------------------------------
if max_price is not None:
    try:
        max_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="priceTo"]'))
        )
        max_input.clear()
        max_input.send_keys(str(max_price))
        print(f"✅ Max price set to {max_price} AED")
    except Exception as e:
        print("❌ Could not set max price:", e)


#------------------BATHROOMS COUNT-------------

if bathrooms is not None:
    try:
        dropdown = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//select[@id="bathroom"]'))
        )
        dropdown.click()
        print("✅ Bathroom dropdown opened")

        option = wait.until(
            EC.element_to_be_clickable((By.XPATH, f'//select[@id="bathroom"]/option[@value="{bathrooms}"]'))
        )
        option.click()
        print(f"✅ Selected {bathrooms} bathrooms")

    except Exception as e:
        print("❌ Could not set bathroom filter:", e)
# --------------- Wait for the property list container to appear ----------------------------------
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "listing-list")]'))
    )
    print("✅ Listing containers loaded.")
    print('Loading Time:', time.time() - st_time)
except Exception as e:
    print("❌ Timeout: Listing containers not found:", str(e))
    print("Page source snippet:", driver.page_source[:1000])
    driver.quit()
    exit()

# ------------------------- Find all listing containers ----------------------------------
listings = driver.find_elements(By.XPATH, '//div[contains(@class, "listing-list")]')


# --- Optional: Print first few to confirm ---
# for i, listing in enumerate(listings[:5]):
#     print(f"  {i+1}. Listing ID: {listing.get_attribute('class')}")
data = []

for listing in listings:
    try:
        title = listing.find_element(By.XPATH, './/h2[@class="listing-title"]//a').text.strip()
        price_text = listing.find_element(By.XPATH, './/span[@class="listing-price"]').text.strip()
        location = listing.find_element(By.XPATH, './/div[contains(@class, "listing-title flex location")]//h3').text.strip()
        url = listing.find_element(By.XPATH, './/h2[@class="listing-title"]//a').get_attribute('href')

        # ✅ Bina filter ke sabhi listings ko add karo
        data.append({
            "Title": title,
            "Price": price_text,
            "Location": location,
            "URL": url
        })

    except Exception as e:
        print("Error extracting data:", e)
        continue
#-----------------DATA FRAME CREATION----------------------------
df = pd.DataFrame(data)
print(df.to_string(index=False))

#-----------------TERMINAL TESTING----------------------------
print("Entered Location:",search_location)

print('END-----------')
print('Total time:', time.time()-st_time)
driver.quit()
