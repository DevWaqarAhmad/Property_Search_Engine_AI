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
#from query import generate_find_properties_url


URL ="https://findproperties.ae/for-rent/properties/uae"
search_location = "dubai"


st_time = time.time()



#-------------------FAKE BROWSERS DATA-------------------------
USER_AGENTS = [

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6943.99 Safari/537.36"
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
    # Clear any existing text (optional: use clear() or send_keys with backspace)
    location_input.clear()
    location_input.send_keys(search_location)
    print(f"✅ Typed: {search_location}")
except Exception as e:
    print("❌ Could not type location:", e)
    driver.quit()
    exit()

# ------------------- CLICK ON FIRST SUGGESTION FROM DROPDOWN --------------------------
try:
    # Wait for first suggestion in dropdown (common classes like MuiAutocomplete-option)
    first_suggestion = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.MuiAutocomplete-option'))
    )
    first_suggestion.click()
    print("✅ Clicked on first suggestion from dropdown")
except Exception as e:
    print("❌ Could not click first suggestion:", e)
    driver.quit()
    exit()
time.sleep(2)



#-----------------TERMINAL TESTING----------------------------
print('END-----------')
print('Total time:', time.time()-st_time)
driver.quit()
