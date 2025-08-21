import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import selenium_stealth 

def setup_driver():
    """Setup Chrome driver with stealth and anti-detection"""
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    #options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});")

    selenium_stealth.stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver

def random_delay(min_seconds=1, max_seconds=5):
    """Add random human-like delay"""
    time.sleep(random.uniform(min_seconds, max_seconds))


def extract_full_price(element):
    """Extract full price like 'AED 1,950,000'"""
    try:
        price_selectors = [
            '.property-price',
            '[data-testid="price"]',
            '.amount',
            '.currency',
            'div[aria-label*="price"]',
            'span[aria-label*="price"]'
        ]

        for selector in price_selectors:
            try:
                container = element.find_element(By.CSS_SELECTOR, selector)
                children = container.find_elements(By.XPATH, ".//*")
                full_text = " ".join([ch.text.strip() for ch in children if ch.text.strip()])
                if 'AED' in full_text:
                    match = re.search(r'AED\s*[\d,]+(?:\.\d{2})?', full_text, re.IGNORECASE)
                    if match:
                        return match.group(0).strip()
            except:
                continue

        match = re.search(r'AED\s*[\d,]+(?:\.\d{2})?', element.text, re.IGNORECASE)
        return match.group(0).strip() if match else "N/A"
    except:
        return "N/A"

def extract_title(element):
    """Extract title from link or heading"""
    try:
        link = element.find_element(By.XPATH, './/a[contains(@href, "/property/details")]')
        return (link.get_attribute('title') or link.text).strip()
    except:
        pass
    try:
        heading = element.find_element(By.XPATH, './/h2 | .//h3 | .//h4')
        return heading.text.strip()
    except:
        pass
    return "N/A"


def extract_location(element):
    """Extract location"""
    location_selectors = [
        '.location',
        '.address',
        '.title-line-2',
        '[aria-label*="Location"]',
        '.property-location',
        'xpath:.//span[contains(translate(text(), "LOCATION", "location"), "location")]'
    ]
    for selector in location_selectors:
        try:
            elem = element.find_element(By.XPATH, selector[6:]) if selector.startswith('xpath:') \
                else element.find_element(By.CSS_SELECTOR, selector)
            text = elem.text.strip()
            if text and len(text) > 2:
                return text
        except:
            continue
    return "N/A"


def extract_details(element):
    """Extract bed, bath, sqft"""
    text = element.text.lower()
    parts = []
    if m := re.search(r'(\d+)\s*bed', text): parts.append(f"{m.group(1)} bed")
    if m := re.search(r'(\d+)\s*bath', text): parts.append(f"{m.group(1)} bath")
    if m := re.search(r'([\d,]+)\s*sq\.?\s*ft', text): parts.append(f"{m.group(1)} sqft")
    return " | ".join(parts) if parts else "N/A"


def extract_url(element):
    """Extract full property URL"""
    try:
        link = element.find_element(By.XPATH, './/a[contains(@href, "/property/details")]')
        href = link.get_attribute('href')
        if href:
            return href if href.startswith('http') else 'https://www.bayut.com' + href
    except:
        pass
    return "N/A"


def scrape_bayut_properties(url, max_properties=10):
    """Scrape top property listings from any Bayut URL"""
    driver = setup_driver()
    properties = []

    try:
        print("🚀 Loading Bayut page...")
        driver.get(url.strip())

        print(f"📌 Page Title: {driver.title}")
        print(f"📍 Current URL: {driver.current_url}")

        if "access denied" in driver.title.lower() or "captcha" in driver.page_source.lower():
            print("🛑 Access denied or CAPTCHA detected.")
            return properties

        wait = WebDriverWait(driver, 30)

        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            'article, [data-testid="listing-card"], .listingCard, [data-qa="SEARCH_RESULT_ITEM"], div[data-index]'
        )))
        print(" Listings detected — loading content...")
 
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_delay(2, 5)

        listing_selectors = [
            'article[data-testid="listing-card"]',
            'div[aria-label="Listing"]',
            '.listingCard',
            'div[data-qa="SEARCH_RESULT_ITEM"]',
            'div[data-dec-qa="SearchResult"]',
            'div[data-index]:not([data-index=""])',
            'article.grid',
            'article',
            '.card, .property-item, .unit-card'
        ]

        elements = []
        for selector in listing_selectors:
            try:
                print(f"🔍 Trying selector: {selector}")
                elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                if len(elements) >= 5:
                    print(f"✅ Found {len(elements)} listings with: {selector}")
                    break
            except TimeoutException:
                continue

        if not elements:
            print("❌ No property listings found.")
            return properties

        print("\n" + "=" * 60)
        #print("📊 TOP 5 PROPERTY LISTINGS")
        print("=" * 60)

        processed = 0
        for elem in elements:
            if processed >= max_properties:
                break
            if len(elem.text.strip()) < 20:
                continue

            try:
                title = extract_title(elem)
                price = extract_full_price(elem)
                location = extract_location(elem)
                details = extract_details(elem)
                url_link = extract_url(elem)

                if price == "N/A" and title == "N/A":
                    continue

                property_data = {
                    'title': title if title != "N/A" else f"Property {processed + 1}",
                    'price': price,
                    'location': location,
                    'details': details,
                    'url': url_link
                }

                properties.append(property_data)
                processed += 1

                print(f"\n PROPERTY {processed}")
                print(f"────────────────────────────────────────────────────")
                print(f"Title    : {property_data['title']}")
                print(f"Price    : {property_data['price']}")
                print(f"Location : {property_data['location']}")
                print(f"Details  : {property_data['details']}")
                print(f"URL      : {property_data['url']}")

            except Exception as e:
                print(f"⚠️ Error processing listing: {e}")
                continue

    except Exception as e:
        print(f"💥 Critical error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

    return properties

if __name__ == "__main__":
    url = "https://www.bayut.com/for-sale/villas/dubai/"

    print("Bayut Property Scraper")
    print("=" * 60)
    print(f"Target: {url}")
    print("=" * 60)

    try:
        properties = scrape_bayut_properties(url, max_properties=10)
        if not properties:
            print("\n❌ No properties were scraped. Possible causes:")
            print("   • Website structure changed")
            print("   • Bot detection / CAPTCHA")
            print("   • Slow network or timeout")

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    except Exception as e:
        print(f"\n🚨 Unexpected error: {e}")











# import time
# import random
# import re
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# import selenium_stealth

# def setup_driver():
#     """Setup Chrome driver with stealth and anti-detection"""
#     options = Options()
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--disable-web-security')
#     options.add_argument('--allow-running-insecure-content')
#     options.add_argument('--disable-features=VizDisplayCompositor')
#     options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
#     # Remove '--headless' if you want to see the browser (for debugging)
#     # options.add_argument('--headless')

#     driver = webdriver.Chrome(options=options)

#     # Remove automation flags
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
#     driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});")
#     driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});")

#     selenium_stealth.stealth(driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
#     )

#     return driver

# def random_delay(min_seconds=2, max_seconds=4):
#     """Add random human-like delay"""
#     time.sleep(random.uniform(min_seconds, max_seconds))

# def extract_full_price(element):
#     """Extract full price like 'AED 1,950,000'"""
#     try:
#         price_selectors = [
#             '.property-price',
#             '[data-testid="price"]',
#             '.amount',
#             '.currency',
#             'div[aria-label*="price"]',
#             'span[aria-label*="price"]'
#         ]

#         for selector in price_selectors:
#             try:
#                 container = element.find_element(By.CSS_SELECTOR, selector)
#                 children = container.find_elements(By.XPATH, ".//*")
#                 full_text = " ".join([ch.text.strip() for ch in children if ch.text.strip()])
#                 if 'AED' in full_text:
#                     match = re.search(r'AED\s*[\d,]+(?:\.\d{2})?', full_text, re.IGNORECASE)
#                     if match:
#                         return match.group(0).strip()
#             except:
#                 continue

#         match = re.search(r'AED\s*[\d,]+(?:\.\d{2})?', element.text, re.IGNORECASE)
#         return match.group(0).strip() if match else "N/A"
#     except:
#         return "N/A"

# def extract_title(element):
#     """Extract title from link or heading"""
#     try:
#         link = element.find_element(By.XPATH, './/a[contains(@href, "/property/details")]')
#         return (link.get_attribute('title') or link.text).strip()
#     except:
#         pass
#     try:
#         heading = element.find_element(By.XPATH, './/h2 | .//h3 | .//h4')
#         return heading.text.strip()
#     except:
#         pass
#     return "N/A"

# def extract_location(element):
#     """Extract location"""
#     location_selectors = [
#         '.location',
#         '.address',
#         '.title-line-2',
#         '[aria-label*="Location"]',
#         '.property-location',
#         'xpath:.//span[contains(translate(text(), "LOCATION", "location"), "location")]'
#     ]
#     for selector in location_selectors:
#         try:
#             elem = element.find_element(By.XPATH, selector[6:]) if selector.startswith('xpath:') \
#                 else element.find_element(By.CSS_SELECTOR, selector)
#             text = elem.text.strip()
#             if text and len(text) > 2:
#                 return text
#         except:
#             continue
#     return "N/A"

# def extract_details(element):
#     """Extract bed, bath, sqft"""
#     text = element.text.lower()
#     parts = []
#     if m := re.search(r'(\d+)\s*bed', text): parts.append(f"{m.group(1)} bed")
#     if m := re.search(r'(\d+)\s*bath', text): parts.append(f"{m.group(1)} bath")
#     if m := re.search(r'([\d,]+)\s*sq\.?\s*ft', text): parts.append(f"{m.group(1)} sqft")
#     return " | ".join(parts) if parts else "N/A"

# def extract_url(element):
#     """Extract full property URL"""
#     try:
#         link = element.find_element(By.XPATH, './/a[contains(@href, "/property/details")]')
#         href = link.get_attribute('href')
#         if href:
#             return href if href.startswith('http') else 'https://www.bayut.com' + href
#     except:
#         pass
#     return "N/A"

# def scrape_bayut_properties(url, max_properties=10):
#     """Scrape top property listings from Bayut with full scroll support"""
#     driver = setup_driver()
#     properties = []
#     seen_urls = set()  # Avoid duplicates

#     try:
#         print("🚀 Loading Bayut page...")
#         driver.get(url.strip())

#         print(f"📌 Page Title: {driver.title}")
#         print(f"📍 Current URL: {driver.current_url}")

#         if "access denied" in driver.title.lower() or "captcha" in driver.page_source.lower():
#             print("🛑 Access denied or CAPTCHA detected.")
#             return properties

#         wait = WebDriverWait(driver, 30)

#         # Wait for first listing
#         wait.until(EC.presence_of_element_located((
#             By.CSS_SELECTOR, 'article[data-testid="listing-card"], [data-qa="SEARCH_RESULT_ITEM"], .listingCard'
#         )))

#         print("✅ Listings found — scrolling to load more...")

#         # Scroll and collect until we have 10
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         while len(properties) < max_properties:
#             # Scroll down
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             random_delay(4, 6)

#             # Find all listings
#             elements = driver.find_elements(
#                 By.CSS_SELECTOR,
#                 'article[data-testid="listing-card"], '
#                 '[data-qa="SEARCH_RESULT_ITEM"], '
#                 '.listingCard, '
#                 'div[data-index]:not([data-index=""]), '
#                 'article.grid'
#             )

#             print(f"🔍 Found {len(elements)} total listings on page...")

#             for elem in elements:
#                 try:
#                     url_link = extract_url(elem)
#                     if not url_link or url_link == "N/A" or url_link in seen_urls:
#                         continue

#                     title = extract_title(elem)
#                     price = extract_full_price(elem)
#                     location = extract_location(elem)
#                     details = extract_details(elem)

#                     if price == "N/A" and title == "N/A":
#                         continue

#                     seen_urls.add(url_link)
#                     property_data = {
#                         'title': title if title != "N/A" else f"Property {len(properties)+1}",
#                         'price': price,
#                         'location': location,
#                         'details': details,
#                         'url': url_link
#                     }

#                     properties.append(property_data)

#                     print(f"\n PROPERTY {len(properties)}")
#                     print(f"────────────────────────────────────────────────────")
#                     print(f"Title    : {property_data['title']}")
#                     print(f"Price    : {property_data['price']}")
#                     print(f"Location : {property_data['location']}")
#                     print(f"Details  : {property_data['details']}")
#                     print(f"URL      : {property_data['url']}")

#                     if len(properties) >= max_properties:
#                         break

#                 except Exception as e:
#                     continue  # Skip failed ones

#             # Check if we reached end of page
#             new_height = driver.execute_script("return document.body.scrollHeight")
#             if new_height == last_height:
#                 print("✅ No more new listings. End of page reached.")
#                 break
#             last_height = new_height

#         print("\n" + "=" * 80)
#         print(f"✅ Successfully scraped {len(properties)} properties.")
#         print("=" * 80)

#     except Exception as e:
#         print(f"💥 Critical error: {e}")
#     finally:
#         try:
#             driver.quit()
#         except:
#             pass

#     return properties

# if __name__ == "__main__":
#     url = "https://www.bayut.com/for-sale/villas/dubai/"

#     print("🏡 Bayut Villa Scraper")
#     print("=" * 80)
#     print(f"Target URL: {url}")
#     print("=" * 80)

#     try:
#         # ✅ This line ensures 10 results
#         properties = scrape_bayut_properties(url, max_properties=10)

#         if not properties:
#             print("\n❌ No properties were scraped. Possible causes:")
#             print("   • Website structure changed")
#             print("   • Bot detection / CAPTCHA")
#             print("   • Slow network or timeout")

#     except KeyboardInterrupt:
#         print("\n🛑 Stopped by user.")
#     except Exception as e:
#         print(f"\n🚨 Unexpected error: {e}")
