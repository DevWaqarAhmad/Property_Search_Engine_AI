import re
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

def process_property_query(user_query):
    """
    Main function to process natural language property queries and return scraped results.
    
    Args:
        user_query (str): Natural language query like "I want to rent a 3BR apartment in JVC under 100k"
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'data': list of property dictionaries,
            'query_info': dict of extracted parameters
        }
    """
    try:
        # Step 1: Extract parameters from natural language query
        query_params = extract_query_parameters(user_query)
        
        if not query_params['success']:
            return {
                'success': False,
                'message': query_params['message'],
                'data': [],
                'query_info': {}
            }
        
        # Step 2: Scrape properties using extracted parameters
        scraping_result = scrape_bayut_properties(query_params['params'])
        
        return scraping_result
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error processing query: {str(e)}",
            'data': [],
            'query_info': {}
        }

def extract_query_parameters(query):
    """
    Extract search parameters from natural language query.
    
    Args:
        query (str): User's natural language query
        
    Returns:
        dict: Extracted parameters or error message
    """
    query_lower = query.lower()
    
    # Check if it's a property-related query
    property_keywords = ['rent', 'buy', 'apartment', 'villa', 'property', 'flat', 'house', 'studio']
    if not any(keyword in query_lower for keyword in property_keywords):
        return {
            'success': False,
            'message': "This doesn't appear to be a property-related query. Please ask about renting or buying properties.",
            'params': {}
        }
    
    params = {
        'purpose': 'rent',  # default
        'location': '',
        'property_type': 'Apartment',  # default
        'beds': '',
        'baths': '',
        'min_price': '',
        'max_price': ''
    }
    
    # Extract purpose (rent/buy)
    if any(word in query_lower for word in ['buy', 'buying', 'purchase']):
        params['purpose'] = 'buy'
    elif any(word in query_lower for word in ['rent', 'rental', 'renting']):
        params['purpose'] = 'rent'
    
    # Extract location with common Dubai areas
    dubai_areas = {
        'jvc': 'Jumeirah Village Circle',
        'jumeirah village circle': 'Jumeirah Village Circle',
        'marina': 'Dubai Marina',
        'dubai marina': 'Dubai Marina',
        'downtown': 'Downtown Dubai',
        'downtown dubai': 'Downtown Dubai',
        'jlt': 'Jumeirah Lake Towers',
        'jumeirah lake towers': 'Jumeirah Lake Towers',
        'business bay': 'Business Bay',
        'deira': 'Deira',
        'bur dubai': 'Bur Dubai',
        'jumeirah': 'Jumeirah',
        'al barsha': 'Al Barsha',
        'dubai hills': 'Dubai Hills Estate',
        'arabian ranches': 'Arabian Ranches',
        'dubai investment park': 'Dubai Investment Park',
        'dip': 'Dubai Investment Park',
        'motor city': 'Motor City',
        'sports city': 'Dubai Sports City',
        'silicon oasis': 'Dubai Silicon Oasis',
        'international city': 'International City',
        'discovery gardens': 'Discovery Gardens',
        'abu dhabi': 'Abu Dhabi',
        'sharjah': 'Sharjah',
        'ajman': 'Ajman'
    }
    
    for area_key, area_full in dubai_areas.items():
        if area_key in query_lower:
            params['location'] = area_full
            break
    
    if not params['location']:
        # Try to extract any location mentioned
        location_patterns = [
            r'in\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|under|over|with|for)',
            r'at\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|under|over|with|for)',
            r'near\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|under|over|with|for)'
        ]
        for pattern in location_patterns:
            match = re.search(pattern, query_lower)
            if match:
                params['location'] = match.group(1).strip().title()
                break
    
    # Extract property type
    property_types = {
        'apartment': 'Apartment',
        'flat': 'Apartment', 
        'studio': 'Apartment',
        'villa': 'Villa',
        'townhouse': 'Townhouse',
        'penthouse': 'Penthouse',
        'duplex': 'Apartment'
    }
    
    for prop_key, prop_value in property_types.items():
        if prop_key in query_lower:
            params['property_type'] = prop_value
            break
    
    # Extract bedrooms
    bedroom_patterns = [
        r'(\d+)\s*(?:br|bed|bedroom)',
        r'(\d+)\s*(?:bed|bedroom)',
        r'(studio)',
        r'(one|two|three|four|five)\s*(?:bed|bedroom)',
        r'(\d+)(?:\s*-|\s*to\s*|\s+)(?:bed|bedroom)'
    ]
    
    for pattern in bedroom_patterns:
        match = re.search(pattern, query_lower)
        if match:
            bed_text = match.group(1)
            if bed_text == 'studio':
                params['beds'] = 'Studio'
            elif bed_text in ['one', '1']:
                params['beds'] = '1'
            elif bed_text in ['two', '2']:
                params['beds'] = '2'
            elif bed_text in ['three', '3']:
                params['beds'] = '3'
            elif bed_text in ['four', '4']:
                params['beds'] = '4'
            elif bed_text in ['five', '5']:
                params['beds'] = '5'
            else:
                params['beds'] = bed_text
            break
    
    # Extract bathrooms
    bathroom_patterns = [r'(\d+)\s*(?:bath|bathroom)', r'(\d+)\s*(?:bath|bathroom)s?']
    for pattern in bathroom_patterns:
        match = re.search(pattern, query_lower)
        if match:
            params['baths'] = match.group(1)
            break
    
    # Extract price range
    price_patterns = [
        r'under\s+(\d+)(?:k|000)?',
        r'below\s+(\d+)(?:k|000)?',
        r'max(?:imum)?\s+(\d+)(?:k|000)?',
        r'up\s+to\s+(\d+)(?:k|000)?',
        r'(\d+)(?:k|000)?\s*(?:to|-)?\s*(\d+)(?:k|000)?',
        r'between\s+(\d+)(?:k|000)?\s*(?:and|to|-)\s*(\d+)(?:k|000)?'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, query_lower)
        if match:
            if 'under' in pattern or 'below' in pattern or 'max' in pattern or 'up to' in pattern:
                max_price = match.group(1)
                if 'k' in query_lower and len(max_price) <= 3:
                    params['max_price'] = str(int(max_price) * 1000)
                else:
                    params['max_price'] = max_price
            elif match.group(2):  # Range pattern
                min_price, max_price = match.group(1), match.group(2)
                if 'k' in query_lower:
                    params['min_price'] = str(int(min_price) * 1000) if len(min_price) <= 3 else min_price
                    params['max_price'] = str(int(max_price) * 1000) if len(max_price) <= 3 else max_price
                else:
                    params['min_price'] = min_price
                    params['max_price'] = max_price
            break
    
    # Set default location if none found
    if not params['location']:
        params['location'] = 'Dubai'
    
    return {
        'success': True,
        'message': f"Searching for {params['purpose']} properties in {params['location']}",
        'params': params
    }

def get_chrome_options():
    """Configure Chrome options for web scraping."""
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
    
    options = Options()
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'user-agent={user_agent}')
    
    # Anti-detection settings
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1400,800")
    options.add_argument("--headless")  # Run in background
    
    return options

def scrape_bayut_properties(params):
    """
    Scrape Bayut properties based on provided parameters.
    
    Args:
        params (dict): Search parameters extracted from user query
        
    Returns:
        dict: Scraping results with success status, message, and data
    """
    driver = None
    try:
        # Initialize Chrome driver
        chrome_options = get_chrome_options()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to Bayut
        base_url = "https://www.bayut.com/to-rent/property/dubai/" if params['purpose'] == 'rent' else "https://www.bayut.com/to-buy/property/dubai/"
        driver.get(base_url)
        
        wait = WebDriverWait(driver, 10)
        time.sleep(3)
        
        # Close popups/modals
        close_popups(driver, wait)
        
        # Apply filters based on parameters
        apply_filters(driver, wait, params)
        
        # Wait for results to load
        time.sleep(10)
        
        # Scrape property data
        property_data = scrape_property_listings(driver, params)
        
        if property_data:
            return {
                'success': True,
                'message': f"Found {len(property_data)} properties matching your criteria",
                'data': property_data,
                'query_info': params
            }
        else:
            return {
                'success': True,
                'message': "No properties found matching your criteria. Try adjusting your search parameters.",
                'data': [],
                'query_info': params
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error during scraping: {str(e)}",
            'data': [],
            'query_info': params
        }
    finally:
        if driver:
            driver.quit()

def close_popups(driver, wait):
    """Close any popups or modals that might appear."""
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, 
                '//div[contains(text(), "View Stories")]/following-sibling::div[contains(@class, "_37d9afbd")]'
            ))
        )
        close_btn.click()
        print("✅ Story banner closed")
    except:
        pass

    try:
        modal = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Agent stories onboarding dialog"]'))
        )
        driver.execute_script("document.body.click();")
        print("✅ Story modal dismissed")
    except:
        pass

def apply_filters(driver, wait, params):
    """Apply search filters based on extracted parameters."""
    
    # Purpose filter (Buy/Rent)
    if params['purpose'].lower() == 'buy':
        try:
            rent_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-haspopup='true' and .//span[text()='Rent']]"))
            )
            rent_button.click()
            time.sleep(1)
            
            buy_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Buy']"))
            )
            buy_option.click()
            print("✅ Selected 'Buy'")
        except Exception as e:
            print(f"❌ Failed to set purpose to Buy: {e}")
    
    # Location filter
    if params['location']:
        try:
            location_filter = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Location filter"]'))
            )
            location_filter.click()
            
            location_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Location filter"]//input'))
            )
            location_input.send_keys("\ue009a")  # Ctrl+A
            location_input.send_keys("\ue003")   # Delete
            location_input.clear()
            location_input.send_keys(params['location'])
            
            time.sleep(2)
            
            try:
                first_suggestion = driver.find_element(By.XPATH, '//span[@class="_98caf06c _26717a45"]')
                first_suggestion.click()
                print(f"✅ Selected location: {params['location']}")
            except:
                print(f"⚠️ Location suggestion not found, using typed location")
                
        except Exception as e:
            print(f"❌ Failed to set location: {e}")
    
    # Property type filter
    if params['property_type']:
        try:
            category_filter = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Category filter"]'))
            )
            category_filter.click()
            time.sleep(1)
            
            # Click Residential first
            residential = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//li[text()="Residential"]'))
            )
            ActionChains(driver).move_to_element(residential).click().perform()
            time.sleep(1)
            
            # Select specific property type
            specific_type = wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    f'//li[.//span[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{params["property_type"].lower()}")]]'
                ))
            )
            ActionChains(driver).move_to_element(specific_type).click().perform()
            print(f"✅ Selected property type: {params['property_type']}")
            
        except Exception as e:
            print(f"❌ Failed to set property type: {e}")
    
    # Beds & Baths filter
    if params['beds'] or params['baths']:
        try:
            beds_baths_filter = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Beds & Baths filter"]'))
            )
            beds_baths_filter.click()
            time.sleep(2)
            
            if params['beds']:
                try:
                    beds_option = wait.until(
                        EC.element_to_be_clickable((By.XPATH, 
                            f'//ul[@aria-label="Beds filter"]//li[contains(text(), "{params["beds"]}")]'
                        ))
                    )
                    ActionChains(driver).move_to_element(beds_option).click().perform()
                    print(f"✅ Selected {params['beds']} bedrooms")
                except Exception as e:
                    print(f"❌ Failed to select bedrooms: {e}")
            
            if params['baths']:
                try:
                    baths_option = wait.until(
                        EC.element_to_be_clickable((By.XPATH, 
                            f'//ul[@aria-label="Baths filter"]//li[contains(text(), "{params["baths"]}")]'
                        ))
                    )
                    ActionChains(driver).move_to_element(baths_option).click().perform()
                    print(f"✅ Selected {params['baths']} bathrooms")
                except Exception as e:
                    print(f"❌ Failed to select bathrooms: {e}")
                    
        except Exception as e:
            print(f"❌ Failed to open beds & baths filter: {e}")
    
    # Price filter
    if params['min_price'] or params['max_price']:
        try:
            price_filter = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//span[text()='Price (AED)']]"))
            )
            price_filter.click()
            time.sleep(1)
            
            if params['min_price']:
                try:
                    min_input = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//input[@id="activeNumericInput"]'))
                    )
                    min_input.clear()
                    min_input.send_keys(params['min_price'])
                    print(f"✅ Set min price: {params['min_price']}")
                except Exception as e:
                    print(f"❌ Failed to set min price: {e}")
            
            if params['max_price']:
                try:
                    max_input = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//input[@id="inactiveNumericInput"]'))
                    )
                    max_input.clear()
                    max_input.send_keys(params['max_price'])
                    print(f"✅ Set max price: {params['max_price']}")
                except Exception as e:
                    print(f"❌ Failed to set max price: {e}")
                    
        except Exception as e:
            print(f"❌ Failed to set price filter: {e}")

def scrape_property_listings(driver, params):
    """Extract property data from the current page."""
    data = []
    
    # Try multiple selectors to find property listings
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
        try:
            listings = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/property/"]')
            print(f"✅ Found {len(listings)} property links as fallback")
        except:
            print("❌ No property listings found")
            return []
    
    
    for idx, listing in enumerate(listings[:20]):
        try:
            property_data = {"PropertyNo": idx + 1}
            
            # Extract title
            title_selectors = [
                'h2[aria-label*="Title"]',
                'h2', 'h3',
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
                property_data["Name"] = "Property Listing"
            
            # Extract price
            price_selectors = [
                'span[aria-label*="Price"]',
                'span[data-testid="property-price"]',
                '.price'
            ]
            
            for selector in price_selectors:
                try:
                    price_element = listing.find_element(By.CSS_SELECTOR, selector)
                    property_data["Price"] = price_element.text.strip()
                    break
                except:
                    continue
            else:
                property_data["Price"] = "Price on Request"
            
            # Extract location
            location_selectors = [
                'div[data-testid="property-location"]',
                '.location',
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
                property_data["Location"] = params.get('location', 'Dubai')
            
            # Extract property URL
            try:
                if listing.tag_name.lower() == 'a':
                    property_data["Link"] = listing.get_attribute("href")
                else:
                    link_element = listing.find_element(By.CSS_SELECTOR, 'a')
                    property_data["Link"] = link_element.get_attribute("href")
            except:
                property_data["Link"] = "N/A"
            
            # Add search parameters
            property_data["Type"] = params.get('property_type', 'N/A')
            property_data["Beds"] = params.get('beds', 'N/A')
            property_data["Baths"] = params.get('baths', 'N/A')
            
            data.append(property_data)
            
        except Exception as e:
            print(f"⚠️ Failed to parse listing {idx + 1}: {str(e)}")
            continue
    
    return data

# Example usage function for chatbot integration
def chatbot_property_search(user_message):
    """
    Function to be called from chatbot.py
    
    Args:
        user_message (str): User's natural language query
        
    Returns:
        dict: Formatted response for chatbot
    """
    result = process_property_query(user_message)
    
    if result['success'] and result['data']:
        # Format response for chatbot
        response = f"\n🏠 {result['message']}\n"
        response += "="*50 + "\n"
        
        for idx, property_info in enumerate(result['data'][:20], 1):  # Show max 20 properties
            response += f"\n📍 Property {idx}:\n"
            response += f"   • Name: {property_info.get('Name', 'N/A')}\n"
            response += f"   • Price: {property_info.get('Price', 'N/A')}\n"
            response += f"   • Location: {property_info.get('Location', 'N/A')}\n"
            response += f"   • Type: {property_info.get('Type', 'N/A')}\n"
            if property_info.get('Beds') != 'N/A':
                response += f"   • Beds: {property_info.get('Beds', 'N/A')}\n"
            if property_info.get('Link') != 'N/A':
                response += f"   • Link: {property_info.get('Link', 'N/A')}\n"
            response += "-" * 30 + "\n"
        
        return response
    else:
        return f"❌ {result['message']}"