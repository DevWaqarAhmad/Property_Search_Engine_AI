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
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import re




#========================= HARD CODED VARIABLE ================
URL = "https://propsearch.ae/dubai-properties-to-rent/by-location"


# my_query = "i want a rent apartment in dubai with 3 bedrooms and 3 baths from 60,000AED to 100,000"
# print("------------------------------")
# parsed_params = parse_query_with_gemini(my_query)
# URL = build_find_properties_url(parsed_params)
# print(URL)
# print("==============================")

search_location = "business bay"

#URL ="https://findproperties.ae/for-rent/properties/uae"



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
    options.add_argument("--window-size=1920,1080")
    #options.add_argument("--headless")

    return options

#------------------ WEBSITE PAGE OPENING ----------------------
chrome_options = get_chrome_options()
# Initialize the Chrome driver with webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
print("Opening Propsearch.ae....")
driver.get(URL)

wait = WebDriverWait(driver, 10)


# ------------------------ CLICK ON LOCATION FILTER --------------------------


# location_filter = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "zena-complete-button-text")]'))
# )
# location_filter.click()
# print("✅ Clicked on Location Filter")


# ------------------- ENTER LOCATION FILTER --------------------------------

# ------------------------ CLICK ON LOCATION FILTER --------------------------
# try:
#     location_filter = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Location")]'))
#     )
#     driver.execute_script("arguments[0].click();", location_filter)
#     print("✅ Clicked on Location Filter")
# except Exception as e:
#     print("❌ Could not click Location Filter:", e)


# ------------------- ENTER LOCATION FILTER --------------------------------

try:

    # ---------- CLICK ON LOCATION FILTER ----------
    clicked = False
    selectors_to_try = [
        '//div[contains(@class, "zena-complete-button-text")]',
        #'//div[contains(@class, "zena-complete-button")]',
        #'//div[contains(@class, "zena-search-dropdown")]',
        #'//button[contains(.,"Location")]',
        #'//div[contains(text(),"Location") or contains(text(),"location")]'
    ]
    for sel in selectors_to_try:
        try:
            el = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, sel)))
            driver.execute_script("arguments[0].click();", el)
            print("✅ Clicked filter via:", sel)
            clicked = True
            break
        except Exception as e:
            pass


    # if not clicked:
    #     print("❌ Could not click filter using primary selectors. Trying broader clickable area...")
    #     # fall back: click the first zena-dropdown-like element
    #     try:
    #         el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
    #             (By.CSS_SELECTOR, 'div.zena-dropdown, div.zena-complete-input-wrapper')))
    #         driver.execute_script("arguments[0].click();", el)
    #         print("✅ Clicked fallback element")
    #         clicked = True
    #     except Exception as e:
    #         print("❌ Final fallback failed:", e)

    # if not clicked:
    #     raise Exception("Unable to open location popup — filter click failed.")

    # # give popup time to animate open
    # time.sleep(0.8)

    # ----------  Locate the input by class (stable) ----------
    input_xpath_candidates = [
        #'//input[contains(@class, "zena-complete")]',
        #'//input[contains(@class, "zena-complete bg-gray-100")]',
        '//input[@placeholder[contains(.,"Dubai")]]',
        #'//input[@type="text" and (contains(@class,"zena") or contains(@class,"complete"))]'
    ]
    location_input = None
    for xp in input_xpath_candidates:
        try:
            location_input = WebDriverWait(driver, 6).until(EC.visibility_of_element_located((By.XPATH, xp)))
            print("✅ Found input using:", xp)
            break
        except Exception:
            pass

    if location_input is None:
        raise Exception("Input field not found by any XPath candidate.")

    # scroll into view & focus
    driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", location_input)
    time.sleep(0.3)

    # ----------  Try JS injection first (most reliable for controlled React inputs) ----------
    try:
        driver.execute_script("""
            const el = arguments[0];
            const val = arguments[1];
            el.value = val;
            // dispatch multiple events so React/vue/others pick it up
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            el.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true}));
            el.dispatchEvent(new KeyboardEvent('keyup', {bubbles:true}));
        """, location_input, search_location)
        print("✅ JS injection performed")
        time.sleep(0.8)
    except Exception as e:
        print("⚠️ JS injection failed, will try ActionChains. Error:", e)

    # ---------- Wait for suggestions - try to click first suggestion ----------
    try:
        # sometimes suggestions wrapper appears inside .acom-suggestions
        first_selector = '.acom-suggestions div'
        first_suggestion = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR, first_selector)))
        driver.execute_script("arguments[0].click();", first_suggestion)
        print("✅ Clicked first suggestion")
    except Exception as e:
        # if suggestion didn't appear, try human-like typing via ActionChains and then Arrow+Enter
        print("ℹ️ Suggestions not clickable yet; trying ActionChains typing + ENTER...")

        # try:
        #     try:
        #         location_input.clear()
        #     except Exception:
        #         pass
        #     actions = ActionChains(driver)
        #     for ch in search_location:
        #         actions.send_keys(ch)
        #     actions.perform()
        #     time.sleep(0.6)
        #     # press ARROW DOWN then ENTER to select first suggestion
        #     location_input.send_keys(Keys.ARROW_DOWN)
        #     time.sleep(0.3)
        #     location_input.send_keys(Keys.ENTER)
        #     print("✅ Typed via ActionChains and pressed ENTER")
        # except Exception as e2:
        #     print("❌ ActionChains typing failed:", e2)
        #     # last resort: send raw keys
        #     try:
        #         location_input.send_keys(search_location + Keys.RETURN)
        #         print("✅ Sent keys + RETURN as last resort")
        #     except Exception as e3:
        #         print("❌ All typing fallback methods failed:", e3)
        #         raise

    # optional: wait for page to react to selection (e.g., filter applied)
    #time.sleep(1.2)


except Exception as exc:
    print("❌ Overall error:", exc)
finally:
    # do not quit immediately if you want to inspect; change to driver.quit() later
    print("Script finished (you can close driver manually).")
    # driver.quit()

# -------------------- PROPERTY CARDS FOUND -------------

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

card_container = soup.find('div', class_='zena-search-results-container')
if card_container:
    property_cards = card_container.find_all('div', class_='mx-auto bg-white rounded-lg border border-gray-200 p-0.5 lg:p-0 mb-4 lg:mb-8 max-w-[550px] lg:max-w-none')
    total_properties = len(property_cards)
    print(f'TOTEL PROPERTIES ARE: ', total_properties)
else:
    print(0)


# ----------------------------------- REFRESH THE PAGE ------------------------------------------

# print("🔄 Refreshing page before parsing...")
# driver.refresh()
# time.sleep(5)  # Wait for page to reload completely
# print("✅ Page refreshed successfully")

# ------------------------------------ BS4 PARSING MODULE ------------------------------------

time.sleep(5)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
card_container = soup.find('div', class_='zena-search-results-container')

data = []

if card_container:
    property_cards = card_container.find_all('div', class_='mx-auto bg-white rounded-lg border border-gray-200 p-0.5 lg:p-0 mb-4 lg:mb-8 max-w-[550px] lg:max-w-none')
    
    for card in property_cards:
        try:
            # Extract Title from specific div
            title_div = card.find('div', class_='mb-1')
            if title_div:
                title = title_div.get_text(strip=True)
            else:
                # Fallback: try to find title in link text
                title_link = card.find('a', class_='block text-sm mb-4')
                title = title_link.get_text(strip=True) if title_link else 'N/A'
            
            # Extract URL from main property link
            url_link = card.find('a', href=True)
            if url_link and url_link.get('href'):
                href = url_link['href']
                url = 'https://propsearch.ae' + href if href.startswith('/') else href
            else:
                url = 'N/A'
            
            # Extract Price
            price_span = card.find('span', class_='price-val')
            if price_span:
                price = price_span.get('data-orig', price_span.get_text(strip=True))
            else:
                price = 'N/A'
            
            # Extract Location (correct class selector)
            location_div = card.find('div', class_='text-xs text-gray-600')
            location = location_div.get_text(strip=True) if location_div else 'N/A'
            
            # Extract Beds/Baths/Area from property details section
            # Look for sections with property details
            details_section = card.find('div', class_='select-none flex items-center gap-4 text-13 mb-4')
            
            bedrooms = 'N/A'
            bathrooms = 'N/A' 
            area = 'N/A'
            
            if details_section:
                details_text = details_section.get_text()
                # Parse bed/bath info from text
                if 'Bed' in details_text:
                    bed_match = re.search(r'(\d+)\s*Bed', details_text)
                    bedrooms = bed_match.group(1) if bed_match else 'N/A'
                
                if 'Bath' in details_text:
                    bath_match = re.search(r'(\d+)\s*Bath', details_text)
                    bathrooms = bath_match.group(1) if bath_match else 'N/A'
                    
                # Extract area if available
                area_match = re.search(r'(\d+(?:,\d+)*)\s*sq', details_text)
                area = area_match.group(1) if area_match else 'N/A'
            
            # Alternative method for extracting details from different sections
            if bedrooms == 'N/A' or bathrooms == 'N/A':
                all_text = card.get_text()
                
                # Look for bed info
                bed_patterns = [r'(\d+)\s*bed', r'(\d+)\s*BR', r'(\d+)\s*Bedroom']
                for pattern in bed_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        bedrooms = match.group(1)
                        break
                
                # Look for bath info  
                bath_patterns = [r'(\d+)\s*bath', r'(\d+)\s*BR', r'(\d+)\s*Bathroom']
                for pattern in bath_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        bathrooms = match.group(1)
                        break
            
            if price != 'N/A':
                price = re.sub(r'[^\d,]', '', str(price))
            
            data.append([
                title,
                price,
                location, 
                bedrooms,
                bathrooms,
                area,
                url
            ])
            
        except Exception as e:
            print(f"Error parsing card: {e}")
            continue

else:
    print("❌ Container not found!")


#-----------------DATA FRAME CREATION----------------------------
df = pd.DataFrame(data, columns=['Title', 'Price', 'Location', 'Bedrooms', 'Bathrooms', 'Area', 'URL'])
print(df.to_string(index=False))

#-----------------TERMINAL TESTING----------------------------
print("Entered Location:",search_location)
print('END-----------')
print('Total time:', time.time()-st_time)
time.sleep(10)
driver.quit()