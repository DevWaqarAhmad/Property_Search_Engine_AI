from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import random
import json
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# ===================================HARD CODED VARIABLES======================================
URL = "https://www.propertyfinder.ae/en/search?l=1&c=2&fu=0&rp=y&ob=mr"
search_location = "ajman"

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

start_time = time.time()

#==========================================CHROME SETUP=============================================

options = Options()
options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-notifications")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

print("Opening PropertyFinder...")
driver.get(URL)
time.sleep(2)

#============================================= Step 1: Click location filter ===================
try:
    location_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="autocomplete"]')))
    location_element.click()
    print("✅ Location filter opened")
    time.sleep(2)
except Exception as e:
    print(f"❌ Could not open location filter: {e}")
    driver.quit()
    exit()

#==================================Step 2: Remove Dubai chip===============================================

try:
    dubai_chip = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="autocomplete-tag"]')))
    dubai_chip.click()
    print("✅ Removed Dubai chip")
    time.sleep(1)
except Exception as e:
    print(f"❌ Could not remove Dubai: {e}")
    driver.quit()
    exit()

#===================================== Step 3: Enter location and select suggestion ================================
try:
    # Find and focus input field
    location_input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//input[@placeholder="City, community or building"]')
    ))
    location_input.click()
    location_input.clear()
    time.sleep(0.5)
    
    # Type location slowly
    for char in search_location:
        location_input.send_keys(char)
        time.sleep(0.1)
    
    print(f"✅ Typed: {search_location}")
    time.sleep(2)
    
    # Click first suggestion
    try:
        first_suggestion = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-testid="autocomplete-option"][1]')
        ))
        first_suggestion.click()
        print("✅ Selected first suggestion")
    except:
        # Fallback: keyboard navigation
        location_input.send_keys(Keys.ARROW_DOWN)
        location_input.send_keys(Keys.ENTER)
        print("✅ Used keyboard navigation")
    
    time.sleep(2)
    
except Exception as e:
    print(f"❌ Location selection failed: {e}")
    driver.quit()
    exit()

#=================================== NEW: REFRESH PAGE AFTER LOCATION SELECTION ===================================
print("🔄 Refreshing page after location selection...")
driver.refresh()
time.sleep(5)  # Wait for page to reload completely
print("✅ Page refreshed successfully")

#=================================Step 4: Click Find button=======================================

# try:
#     find_button = wait.until(EC.element_to_be_clickable(
#         (By.XPATH, '//button[@data-testid="filters-form-btn-find"]')
#     ))
#     find_button.click()
#     print("✅ Clicked FIND button")
#     time.sleep(3)
# except Exception as e:
#     print(f"❌ Could not click FIND: {e}")
#     driver.quit()
#     exit()



#============================== Step 5: Count total properties =================================================

try:
    print("Counting properties...")
    time.sleep(2)
    
    property_containers = driver.find_elements(By.XPATH, '//li[@role="listitem"]')
    total_count = len(property_containers)
    
    print(f"Total {total_count} properties in page")
    
except Exception as e:
    print(f"Could not count properties: {e}")

# ===================== SMART WAIT FOR DYNAMIC FILTER APPLY =====================
# try:
#     # Wait until number of property cards changes from initial count (or > 0)
#     WebDriverWait(driver, 15).until(
#         lambda d: len(d.find_elements(By.XPATH, '//li[@role="listitem"]')) > 0
#     )
#     print("✅ Filter applied — new properties loaded")
# except TimeoutException:
#     print("❌ Filter failed — no properties loaded after click")

#=======================================================MAJOR PART IS PARSING BY JSON============================================
# ===================== JSON PARSING PART (FINAL) =====================
time.sleep(8)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__', type='application/json')

if script:
    json_data = json.loads(script.string)
    try:
        props = json_data['props']['pageProps']['searchResult']['properties']
        data = []
        for p in props:
            data.append([
                p.get('title', ''),
                p.get('price', {}).get('value', '') if isinstance(p.get('price'), dict) else '',
                p.get('location', {}).get('full_name', ''),
                p.get('bedrooms', ''),
                p.get('bathrooms', ''),
                p.get('sizeInSqFt', '')  # <-- area in sqft
            ])
        df = pd.DataFrame(data, columns=['Title', 'Price', 'Location', 'Bedrooms', 'Bathrooms', 'Area'])
        print(df)
    except KeyError as e:
        print(f"❌ Key error: {e}")
else:
    print("❌ __NEXT_DATA__ not found")

#=============================ENDING PROJECT HERE============================
print("🎉 Search completed successfully!")
print(f"Total time: {time.time() - start_time:.2f}")
time.sleep(5)
driver.quit()
