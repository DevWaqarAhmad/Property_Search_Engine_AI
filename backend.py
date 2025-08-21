import concurrent.futures
import time
import re
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
import os
from crawlers.property_finder import crawl_property_finder
from crawlers.find_properties import crawl_find_properties

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def is_property_query(query: str) -> bool:
    """
    Detect if the query is related to property search
    """
    query = query.lower().strip()
    
    property_keywords = [
        'rent', 'sale', 'buy', 'lease', 'apartment', 'villa', 'studio',
        'penthouse', 'townhouse', 'room', 'bedroom', 'bathroom', 'flat',
        'duplex', 'house', 'property', 'real estate', 'housing', 'accommodation',
        'dubai', 'sharjah', 'abu dhabi', 'ajman', 'ras al khaimah',
        'marina', 'downtown', 'jbr', 'business bay', 'difc'
    ]
    
    return any(keyword in query for keyword in property_keywords)

def call_gemini_api(query: str) -> str:
    """
    Call Gemini API for general conversation
    """
    try:
        response = model.generate_content(
            f"You are a helpful assistant for a UAE property finder app. "
            f"Answer naturally in 1-2 sentences. Query: {query}"
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"❌ Gemini API error: {e}")
        return "Sorry, I couldn't process your request right now."

def validate_query(query: str) -> bool:
    """Validate search query"""
    if not query or len(query.strip()) < 3:
        return False
    if len(query) > 200:
        return False
    harmful_patterns = ['<script', 'javascript:', 'select ', 'union ', 'insert ', 'delete ']
    if any(pattern in query.lower() for pattern in harmful_patterns):
        return False
    return True

def clean_price(price_text: str) -> str:
    if not price_text:
        return "Price on request"
    clean = re.sub(r'\s+', ' ', price_text.strip())
    if 'aed' in clean.lower() and not clean.upper().startswith('AED'):
        clean = re.sub(r'aed', 'AED', clean, flags=re.IGNORECASE)
    return clean

def normalize_location(location: str) -> str:
    if not location:
        return "UAE"
    location_map = {
        'dxb': 'Dubai', 'auh': 'Abu Dhabi', 'shj': 'Sharjah', 'ajm': 'Ajman'
    }
    location_lower = location.lower()
    for abbrev, full_name in location_map.items():
        if abbrev in location_lower:
            return full_name
    return location.title()

def remove_duplicates(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not results:
        return results
    unique_results = []
    seen_combinations = set()
    
    for prop in results:
        title = prop.get('title', '').lower().strip()
        price = prop.get('price', '').lower().strip()
        location = prop.get('location', '').lower().strip()
        price_numbers = re.findall(r'\d+', price)
        price_signature = ''.join(price_numbers)
        signature = f"{title[:30]}_{price_signature}_{location[:20]}"
        
        if signature not in seen_combinations:
            seen_combinations.add(signature)
            cleaned_prop = {
                'title': prop.get('title', 'Property Available'),
                'price': clean_price(prop.get('price', '')),
                'location': normalize_location(prop.get('location', '')),
                'description': prop.get('description', ''),
                'link': prop.get('link', '#'),
                'source': prop.get('source', 'Unknown')
            }
            unique_results.append(cleaned_prop)
    
    return unique_results

def crawl_single_site(site_name: str, crawler_func, query: str) -> List[Dict[str, Any]]:
    try:
        logger.info(f"🔍 Starting {site_name} crawler...")
        start_time = time.time()
        results = crawler_func(query)
        end_time = time.time()
        duration = end_time - start_time
        
        if results:
            logger.info(f"✅ {site_name}: Found {len(results)} properties in {duration:.1f}s")
            return results
        else:
            logger.warning(f"⚠️ {site_name}: No results found in {duration:.1f}s")
            return []
    except Exception as e:
        logger.error(f"❌ {site_name} crawler failed: {e}")
        return []

def search_all_properties(query: str) -> List[Dict[str, Any]]:
    """
    Main function: Returns either scraped results OR Gemini response
    based on query type
    """
    logger.info(f"🚀 Processing query: '{query}'")
    
    if not validate_query(query):
        logger.error("❌ Invalid query")
        return []
    
    if not is_property_query(query):
        logger.info("💬 Non-property query detected → Using Gemini AI")
        try:
            ai_response = call_gemini_api(query)
            return [{
                'title': "AI Assistant Response",
                'price': "—",
                'location': "UAE",
                'description': ai_response,
                'link': "#",
                'source': "AI Assistant"
            }]
        except Exception as e:
            logger.error(f"❌ Gemini failed: {e}")
            return [{
                'title': "AI Assistant",
                'price': "—",
                'location': "UAE",
                'description': "I can help you find properties in UAE. Try searching for '2 bedroom apartment in Dubai Marina'.",
                'link': "#",
                'source': "AI Assistant"
            }]
    
    logger.info("🏠 Property query detected → Starting web scraping")
    start_time = time.time()
    all_results = []
    
    crawlers = [
        ("Property Finder", crawl_property_finder),
        ("Find Properties", crawl_find_properties)
    ]
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_crawler = {
                executor.submit(crawl_single_site, name, func, query): name 
                for name, func in crawlers
            }
            for future in concurrent.futures.as_completed(future_to_crawler, timeout=90):
                crawler_name = future_to_crawler[future]
                try:
                    results = future.result()
                    if results:
                        all_results.extend(results)
                        logger.info(f"✅ {crawler_name}: Added {len(results)} properties")
                except Exception as e:
                    logger.error(f"❌ {crawler_name} failed: {e}")
    except Exception as e:
        logger.error(f"❌ Parallel execution failed: {e}")
        for name, func in crawlers:
            results = crawl_single_site(name, func, query)
            if results:
                all_results.extend(results)
    
    if all_results:
        unique_results = remove_duplicates(all_results)
        def sort_key(prop):
            has_price = 'aed' in prop['price'].lower() or any(char.isdigit() for char in prop['price'])
            return (not has_price, prop['title'].lower())
        sorted_results = sorted(unique_results, key=sort_key)
        
        end_time = time.time()
        logger.info(f"🎉 Found {len(sorted_results)} unique properties in {end_time - start_time:.1f}s")
        return sorted_results
    else:
        logger.warning("⚠️ No properties found")
        return []