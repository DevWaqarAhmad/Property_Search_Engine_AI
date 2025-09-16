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
from selenium.webdriver.common.action_chains import ActionChains



# ===================================HARD CODED VARIABLES======================================
URL = "https://sharjah.dubizzle.com/en/property-for-rent/residential/"

# my_query = "3 bedroom apartment for rent"
# print("------------------------------")
# parsed_params = parse_query_with_gemini(my_query)
# URL = build_propertyfinder_url(parsed_params)
# print(URL)
# print("==============================")
search_location = "dubai"

#================================= USER AGENTS ====================================
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
#options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

print("Opening Dubizzle.......")
driver.get(URL)
#time.sleep(2)


#============================================= Step 1: Click location filter ===================
if not search_location:
    print("⚠️ Location value is empty, skipping...")
else:
    try:
        time.sleep(1)
        location_input = wait.until(EC.element_to_be_clickable((By.ID, "location-autocomplete")))
        location_input.click()
        print("✅ Clicked on Location Input Field")
    except Exception as e:
        print(f"❌ Could not click location input: {e}")
        print("🔄 Trying alternative selector...")
        try:
            # Try alternative selector
            location_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Enter location"]')))
            location_input.click()
            print("✅ Clicked on Location Input Field (Alternative)")
        except Exception as e2:
            print(f"❌ Alternative selector failed: {e2}")
            driver.quit()
            exit()

#===================================== Step 3: Enter location and select suggestion ================================
if not search_location:
    print("⚠️ Location value is empty, skipping...")
else:
    try:
        location_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@id="location-autocomplete"]')))
        location_input.click()
        location_input.clear()
        location_input.send_keys(search_location)
        print(f"✅ Typed '{search_location}' into location input")
        time.sleep(1)


        #====================================================
        # Step 3: Find the first suggestion that matches exactly or starts with search_location
        try:
            # Wait for listbox
            listbox = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="listbox"]'))
            )

            # Find first option that contains search_location (case-insensitive)
            suggestion = listbox.find_element(By.XPATH, f'.//div[@role="option" and contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{search_location.lower()}")][1]')
            
            # Scroll into view and click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", suggestion)
            time.sleep(0.3)
            suggestion.click()
            print(f"✅ Selected suggestion: {suggestion.text}")

        except Exception as e:
            print(f"❌ Could not find or click suggestion: {e}")
            # Fallback: Try arrow keys
            try:
                location_input.send_keys(Keys.ENTER)
                print("✅ Fallback: Pressed Enter to select suggestion")
            except:
                print("❌ Fallback failed too")
                pass

    except Exception as e:
        print(f"❌ Could not handle location input: {e}")
        driver.quit()
        exit()

# if not search_location:
#     print("⚠️ Skipping location")
# else:
#     try:
#         loc = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@id="location-autocomplete"]')))
#         loc.click()
#         loc.clear()
#         loc.send_keys(search_location)
#         print(f"✅ Typed '{search_location}'")

#         time.sleep(1)
#         suggestion = driver.find_element(By.XPATH, '//div[@role="listbox"]//div[@role="option"][1]')
#         driver.execute_script("arguments[0].scrollIntoView();", suggestion)
#         suggestion.click()
#         print("✅ Selected suggestion")
#     except:
#         loc.send_keys(Keys.ENTER)
#         print("✅ Fallback: Pressed Enter")





#============================== Step 3: Count total properties =================================================
try:
    time.sleep(2)
    
    # Smart selector - finds actual property cards
    selectors = [
        '//div[contains(@class, "property-lpv-card")]',
        '//div[contains(text(), "AED")]//ancestor::div[contains(@class, "MuiBox") or contains(@class, "card")][1]',
        '//a[contains(@href, "/property/")]//parent::div'
    ]
    
    cards = []
    for selector in selectors:
        cards = driver.find_elements(By.XPATH, selector)
        if cards: break
    
    # Count only displayed property cards with valid content
    count = len([c for c in cards if c.is_displayed() and 
                any(kw in c.text.lower() for kw in ['aed', 'bedroom']) and 
                len(c.text.strip()) > 50])
    
    print(f"✅ Found {count} properties on first page")
    
except Exception as e:
    print(f"❌ Could not count: {e}")




# ==================================== JSON PARSING PART (FINAL) =================================



#============================================== ENDING PROJECT HERE============================
print("🎉 Search completed successfully!")
print(f"Total time: {time.time() - start_time:.2f}")
time.sleep(5)
driver.quit()