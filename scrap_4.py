from re import search

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import json
import time
import random


# --- Configuration ---
URL = "https://www.bayut.com/to-rent/property/dubai/"
search_location = "Jumeirah Village Circle"
property_type = "Apartment"
beds = "2"
baths = "1"
min_price = "80000"
max_price = "150000"

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

def get_chrome_options():
    options = Options()
    # Randomly select a User-Agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'user-agent={user_agent}')

    # Essential for stealth
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
    # options.add_argument("--headless")

    return options

# Use with undetected-chromedriver
# driver = uc.Chrome(options=options)


chrome_options = get_chrome_options()
# Initialize the Chrome driver with webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def close_view_stories():
    """Close 'View Stories' banner or modal if it appears"""
    try:
        close_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, 
                '//div[contains(text(), "View Stories")]/following-sibling::div[contains(@class, "_37d9afbd")]'
            ))
        )
        close_btn.click()
        print("✅ 'View Stories from TruBrokers' banner closed")
    except:
        pass 

    try:
        
        modal = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Agent stories onboarding dialog"]'))
        )
        # Click outside the modal to dismiss it
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
        print("✅ Story modal dismissed by clicking outside")
    except:
        pass  

driver.get(URL)
close_view_stories()
# Wait for page to load
wait = WebDriverWait(driver, 10)


# ---------------------------------------------------------------------------------------------------------
# Page clearing

# # Wait for page to load
time.sleep(3)

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

# ------------------------------------RESIDENTIAL & COMMERCIAL---------------------------------------------------------------------
RESIDENTIAL_TYPES = ["Apartment", "Villa", "Townhouse", "Penthouse", "Hotel Apartment", "Land", "Villa Compound","Floor", "Building" ]
COMMERCIAL_TYPES = ["Office", "Shop", "Warehouse", "Labour Camp", "Bulk Unit", "Factory", "Industrial Area", "Mixed Used Land", "Showroom", "Other Commercial"]
#----------------------MAIN CATEGORY----------------------------------- 

try:
    category_filter = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Category filter"]'))
    )
    category_filter.click()
    print("✅ Clicked 'Category filter' button")
except Exception as e:
    print("❌ Could not click Category filter:", str(e))
    driver.quit()
    exit()

# --------------------Decide category and click specific type-------------------------------

try:
    category_filter = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Category filter"]'))
    )
    category_filter.click()
    print("✅ Clicked 'Category filter' button")
    time.sleep(1)  # Let dropdown load
except Exception as e:
    print("❌ Could not click 'Category filter':", str(e))
    driver.quit()
    exit()
if property_type in RESIDENTIAL_TYPES:
    try:
        residential = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//li[text()="Residential"]'))
        )
        ActionChains(driver).move_to_element(residential).click().perform()
        print("✅ Clicked 'Residential'")
        time.sleep(1)
    except Exception as e:
        print("❌ Could not click 'Residential':", str(e))
        driver.quit()
        exit()
    try:
        specific_type = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                f'//li[.//span[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{property_type.lower()}")]]'
            ))
        )
        ActionChains(driver).move_to_element(specific_type).click().perform()
        print(f"✅ Selected '{property_type}'")
    except Exception as e:
        print(f"❌ Could not select '{property_type}':", str(e))
        driver.quit()
        exit()

elif property_type in COMMERCIAL_TYPES:
    try:
        commercial = wait.until(EC.element_to_be_clickable((By.XPATH, '//li[text()="Commercial"]')))
        commercial.click()
        print("✅ Clicked 'Commercial'")
    except Exception as e:
        print("❌ Could not click Commercial:", str(e))
        driver.quit()
        exit()

    try:
        specific_type = wait.until(
            EC.element_to_be_clickable((By.XPATH,
                f'//li[.//span[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{property_type.lower()}")]]'
            ))
        )
        specific_type.click()
        print(f"✅ Clicked '{property_type}'")
    except Exception as e:
        print(f"❌ Could not click '{property_type}':", str(e))
        driver.quit()
        exit()
else:
    print(f"❌ Unknown property type: {property_type}")
    driver.quit()
    exit()

    
#--------------------------BEDS & BATHS FILTER -----------------------------------
try:
    beds_baths_filter = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Beds & Baths filter"]'))
    )
    beds_baths_filter.click()
    print("✅ Clicked 'Beds & Baths' filter")
except Exception as e:
    print("❌ Could not click 'Beds & Baths' filter:", str(e))
    driver.quit()
    exit()

time.sleep(2)

# --- Select Beds ------------------------
try:
    # Only match Beds (under Beds filter)
    beds_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, 
            f'//ul[@aria-label="Beds filter"]//li[contains(text(), "{beds}")]'
        ))
    )
    
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", beds_option)
    time.sleep(0.5)
    
    ActionChains(driver).move_to_element(beds_option).click(beds_option).perform()
    print(f"✅ Selected '{beds}' bedrooms")
    
except Exception as e:
    print(f"❌ Could not select '{beds}' bedrooms:", str(e))
    driver.quit()
    exit()

# --- Select Baths ----------------------
try:
    # Only match Baths (under Baths filter)
    baths_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, 
            f'//ul[@aria-label="Baths filter"]//li[contains(text(), "{baths}")]'
        ))
    )
    
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", baths_option)
    time.sleep(0.5)
    
    ActionChains(driver).move_to_element(baths_option).click(baths_option).perform()
    print(f"✅ Selected '{baths}' bathrooms")
    
except Exception as e:
    print(f"❌ Could not select '{baths}' bathrooms:", str(e))
    driver.quit()
    exit()

# Price Range Filter -----------------------------------
try:
    price_filter = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and .//span[text()="Price (AED)"]]'))
    )
    price_filter.click()
    print("✅ Clicked 'Price (AED)' filter")
    time.sleep(1)  # Let inputs load
except Exception as e:
    print("❌ Could not click 'Price (AED)' filter:", str(e))
    driver.quit()
    exit()

# ------------- Enter Min Price ----------------------------------
try:
    min_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="activeNumericInput"]'))
    )
    min_input.clear()
    min_input.send_keys(min_price)
    print(f"✅ Entered Min Price: {min_price}")
except Exception as e:
    print(f"❌ Could not enter Min Price: {str(e)}")
    driver.quit()
    exit()

# ---------------- Enter Max Price ------------------
try:
    max_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="inactiveNumericInput"]'))
    )
    max_input.clear()
    max_input.send_keys(max_price)
    print(f"✅ Entered Max Price: {max_price}")
except Exception as e:
    print(f"❌ Could not enter Max Price: {str(e)}")
    driver.quit()
    exit()


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
time.sleep(5)





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
        if isinstance(types, list):
            for t in types:
                if t in ["Apartment", "Villa", "House", "Townhouse", "HotelApartment", "Building", "Office", "Shop", "Warehouse"]:
                    prop_type = t
                    break
                else:
                    prop_type = "Other"
            else: 
                    prop_type = "Other"
        
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
        beds = rooms.get("value", "N/A") if isinstance(rooms, dict) else str(rooms)

        # Baths
        baths = ent.get("numberOfBathroomsTotal", "N/A")

        # Location
        address = ent.get("address", {})
        region = address.get("addressRegion", "N/A") if isinstance(address, dict) else "N/A"
        location = address.get("addressLocality", "N/A") if isinstance(address, dict) else "N/A"

        property_no = item.get("position", "N/A")

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
