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
print('Start Program -------------------------------------')
URL = "https://www.bayut.com/to-rent/property/dubai/"
PURPOSE = "Rent"
search_location = "Jumeirah Village Circle"
property_type = "Apartment"
beds = "3"
baths = "1"
min_price = "60000"
max_price = "150000"

st_time = time.time()

# === User-Agent Rotation ===
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
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
    return options

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
        driver.execute_script("document.body.click();")
        #body = driver.find_element(By.TAG_NAME, "body")
        #body.click()
        print("✅ Story modal dismissed by clicking outside")
    except:
        pass  

# Initialize Chrome driver
chrome_options = get_chrome_options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get(URL)
close_view_stories()
wait = WebDriverWait(driver, 10)

# Page clearing and setup
time.sleep(3)

try:
    close_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "View Stories")]/following-sibling::div[contains(@class, "_37d9afbd")]'))
    )
    close_btn.click()
    print("✅ 'View Stories from TruBrokers' banner closed")
except Exception as e:
    print("❌ Story banner not found or already closed:", str(e))

try:
    modal = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Agent stories onboarding dialog"]'))
    )

    #body = driver.find_element(By.TAG_NAME, "body")
    #body.click()
    driver.execute_script("document.body.click();")
    print("✅ Story modal dismissed by clicking outside")
except:
    pass

# Purpose filter
try:
    if PURPOSE.lower() == "buy":
        rent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-haspopup='true' and .//span[text()='Rent']]"))
        )
        rent_button.click()
        print("✅ Clicked 'Rent' button to open dropdown")
        time.sleep(1)
        
        buy_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Buy']"))
        )
        buy_option.click()
        print("✅ Selected 'Buy'")
    elif PURPOSE.lower() == "rent":
        print("✅ Purpose is already set to 'Rent' — no action needed")
    else:
        print(f"❌ Invalid purpose: {PURPOSE}")
        driver.quit()
        exit()
except Exception as e:
    print("❌ Failed to set Purpose:", str(e))

# Location filter
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

try:
    location_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Location filter"]//input'))
    )
    location_input.send_keys("\ue009a")  # Ctrl+A
    location_input.send_keys("\ue003")   # Delete
    location_input.clear()
    location_input.send_keys(search_location)
    print(f"✅ Typed {search_location}")
except Exception as e:
    print("❌ Could not find input field:", e)
    driver.quit()
    exit()

time.sleep(2)  # Let suggestions load

try:
    first_suggestion = driver.find_element(By.XPATH, '//span[@class="_98caf06c _26717a45"]')
    first_suggestion.click()
    print("✅ Selected: Clicked first suggestion")
except Exception as e:
    print("❌ Could not select suggestion:", e)

# Property type filter
RESIDENTIAL_TYPES = ["Apartment", "Villa", "Townhouse", "Penthouse", "Hotel Apartment", "Land", "Villa Compound", "Floor", "Building"]
COMMERCIAL_TYPES = ["Office", "Shop", "Warehouse", "Labour Camp", "Bulk Unit", "Factory", "Industrial Area", "Mixed Used Land", "Showroom", "Other Commercial"]

if property_type.strip():
    try:
        category_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Category filter"]'))
        )
        category_filter.click()
        print("✅ Clicked 'Category filter' button")
        time.sleep(1)
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

# Beds & Baths filter
if beds.strip() or baths.strip():
    try:
        beds_baths_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Beds & Baths filter"]'))
        )
        beds_baths_filter.click()
        print("✅ Clicked 'Beds & Baths' filter")
        time.sleep(2)
    except Exception as e:
        print("❌ Could not click 'Beds & Baths' filter:", str(e))
        driver.quit()
        exit()

    if beds.strip():
        try:
            beds_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, 
                    f'//ul[@aria-label="Beds filter"]//li[contains(text(), "{beds}")]'
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", beds_option)
            time.sleep(0.5)
            ActionChains(driver).move_to_element(beds_option).click().perform()
            print(f"✅ Selected '{beds}' bedrooms")
        except Exception as e:
            print(f"❌ Could not select '{beds}' bedrooms:", str(e))

    if baths.strip():
        try:
            baths_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, 
                    f'//ul[@aria-label="Baths filter"]//li[contains(text(), "{baths}")]'
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", baths_option)
            time.sleep(0.5)
            ActionChains(driver).move_to_element(baths_option).click().perform()
            print(f"✅ Selected '{baths}' bathrooms")
        except Exception as e:
            print(f"❌ Could not select '{baths}' bathrooms:", str(e))

# Price filter (if needed)
if min_price.strip() or max_price.strip():
    try:
        price_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//span[text()='Price (AED)']]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", price_filter)
        time.sleep(0.5)
        price_filter.click()
        print("✅ Clicked 'Price (AED)' filter")
        time.sleep(1)

        if min_price.strip():
            try:
                min_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@id="activeNumericInput"]'))
                )
                min_input.clear()
                min_input.send_keys(min_price)
                print(f"✅ Entered Min Price: {min_price}")
            except Exception as e:
                print(f"❌ Could not enter Min Price: {str(e)}")

        if max_price.strip():
            try:
                max_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@id="inactiveNumericInput"]'))
                )
                max_input.clear()
                max_input.send_keys(max_price)
                print(f"✅ Entered Max Price: {max_price}")
            except Exception as e:
                print(f"❌ Could not enter Max Price: {str(e)}")
    except Exception as e:
        print("❌ Could not click 'Price (AED)' filter:", str(e))

# Wait for page to load after filters
print("⏳ Waiting for filtered results to load...")
time.sleep(10)  # Increased wait time

# Enhanced scraping logic
def scrape_property_data():
    data = []
    
    # Try multiple approaches to find property listings
    possible_selectors = [
        'article[data-testid]',
        'article',
        'div[data-testid*="property"]',
        'div[aria-label*="property"]',
        '.property-card',
        '[data-testid="property-card"]'
    ]
    
    listings = []
    for selector in possible_selectors:
        try:
            listings = driver.find_elements(By.CSS_SELECTOR, selector)
            if listings:
                print(f"✅ Found {len(listings)} listings with selector: {selector}")
                break
        except:
            continue
    
    if not listings:
        # Fallback: Try to find any links that look like property listings
        try:
            listings = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/property/"]')
            print(f"✅ Found {len(listings)} property links as fallback")
        except:
            print("❌ No property listings found with any selector")
            return []
    
    # Process found listings
    for idx, listing in enumerate(listings[:20]):  # Limit to first 20
        try:
            property_data = {"PropertyNo": idx + 1}
            
            # Try to get title/name
            title_selectors = [
                'h2[aria-label*="Title"]',
                'h2',
                'h3',
                '[data-testid="property-title"]',
                '.title'
            ]
            
            for selector in title_selectors:
                try:
                    title_element = listing.find_element(By.CSS_SELECTOR, selector)
                    property_data["Name"] = title_element.text.strip()
                    break
                except:
                    continue
            else:
                property_data["Name"] = "N/A"
            
            # Try to get price
            price_selectors = [
                'span[aria-label*="Price"]',
                'span[data-testid="property-price"]',
                '.price',
                'span:contains("AED")'
            ]
            
            for selector in price_selectors:
                try:
                    price_element = listing.find_element(By.CSS_SELECTOR, selector)
                    property_data["Price"] = price_element.text.strip()
                    break
                except:
                    continue
            else:
                property_data["Price"] = "N/A"
            
            # Try to get location
            location_selectors = [
                'div[data-testid="property-location"]',
                '.location',
                'h3',
                '[aria-label*="location"]'
            ]
            
            for selector in location_selectors:
                try:
                    location_element = listing.find_element(By.CSS_SELECTOR, selector)
                    property_data["Location"] = location_element.text.strip()
                    break
                except:
                    continue
            else:
                property_data["Location"] = search_location
            
            # Try to get URL
            try:
                if listing.tag_name.lower() == 'a':
                    property_data["Link"] = listing.get_attribute("href")
                else:
                    link_element = listing.find_element(By.CSS_SELECTOR, 'a')
                    property_data["Link"] = link_element.get_attribute("href")
            except:
                property_data["Link"] = "N/A"
            
            # Add configured values
            property_data["Type"] = property_type
            property_data["Beds"] = beds if beds else "N/A"
            property_data["Baths"] = baths if baths else "N/A"
            
            data.append(property_data)
            
        except Exception as e:
            print(f"⚠️ Failed to parse listing {idx + 1}: {str(e)}")
            continue
    
    return data

# Try scraping
print("🔍 Attempting to scrape property data...")
scraped_data = scrape_property_data()

if scraped_data:
    df = pd.DataFrame(scraped_data)
    print("\n" + "="*50)
    print("SCRAPED PROPERTY DATA:")
    print("="*50)
    print(df.to_string(index=False))
    print(f"\n✅ Successfully scraped {len(scraped_data)} properties")
else:
    print("❌ No property data could be scraped")
    print("💡 Current URL:", driver.current_url)
    
    # Debug: Print page source snippet to see what's actually loaded
    page_source = driver.page_source
    if "no results" in page_source.lower() or "0 results" in page_source.lower():
        print("🔍 Page indicates no results found - try different filter criteria")
    else:
        print("🔍 Page seems loaded but properties not detected - DOM structure may have changed")

print('='*50)
print(f'Total execution time: {time.time() - st_time:.2f} seconds')
driver.quit()