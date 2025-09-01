import google.generativeai as genai
from dotenv import load_dotenv
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

#-----------------FUNCTION OF CREATE URLS--------------------------
def generate_find_properties_url(user_query):
    """
    Generates a Find Properties URL with:
    - Bedroom filter (if mentioned)
    - Property type
    - Intent: rent, sale, or sharing
    - Fixed location /uae/ by default
    Returns: raw URL string only
    """
    prompt = f"""
You are a precise URL generator for findproperties.ae. Analyze the user's query and return ONLY the correct search URL.

User Query: "{user_query}"

Rules:

1. First, detect the **number of bedrooms** if mentioned:
   - Look for: "1 bedroom", "2-bed", "3 bhk", "studio", "4 room", etc.
   - If found, format as: `{{number}}-bedroom-` (e.g., "3-bedroom-villa")
   - Special case: "studio" → use "studio-bedroom-"
   - If not mentioned, skip the bedroom prefix.

2. Detect the **property type** and map to:
   - apartment → "apartments"
   - villa → "villa"
   - land → "land"
   - office → "office"
   - shop → "shops"
   - building → "buildings"
   - warehouse → "warehouse"
   - showroom → "showroom"
   - labour camp → "labour-camps"
   - townhouse → "townhouse"
   - hotel apartment → "hotel-apartments"
   - other commercial → "other-commercial"
   - penthouse → "penthouse"
   If none, use "properties"

3. Detect the **intent**:
   - rent, rental, lease, on rent → "for-rent"
   - buy, sale, for sale, purchase, invest → "for-sale"
   - sharing, room, bed space, roommate → "for-sharing"
   If unsure, default to "for-rent"

4. Detect the **location**:
   - "/uae" be defualt "
   - "no need to create URL with user query like dubai abu dhabi etc"

5. Generate URL in this format:
   https://findproperties.ae/{{intent}}/{{bedroom_prefix}}{{slug}}/{{location}}
   - Only include `{{bedroom_prefix}}` if bedroom count or studio is specified.
   - Example: "4-bedroom-apartments", "7-bedroom-villa", "studio-bedroom-apartments"

Examples:
- "I want to rent a villa in Dubai" → https://findproperties.ae/for-rent/villa/uae
- "Looking to buy an apartment in Ajman" → https://findproperties.ae/for-sale/apartments/uae
- "Need a bed space in Sharjah" → https://findproperties.ae/for-sharing/properties/uae
- "I want to rent a 7 bedroom villa in Dubai" → https://findproperties.ae/for-rent/7-bedroom-villa/uae
- "Looking to buy a 4 bedroom apartment in Dubai" → https://findproperties.ae/for-sale/4-bedroom-apartments/uae
- "Need a 3-bedroom townhouse for rent in UAE" → https://findproperties.ae/for-rent/3-bedroom-townhouse/uae
- "I want to rent a 2 bhk apartment in Ajman" → https://findproperties.ae/for-rent/2-bedroom-apartments/uae
- "Studio apartment for rent in Sharjah" → https://findproperties.ae/for-rent/studio-bedroom-apartments/uae
- "Office space for rent in JVC with parking" → https://findproperties.ae/for-rent/office/uae
- "Shop for sale in Dubai Mall, retail space" → https://findproperties.ae/for-sale/shops/uae
- "Labour camp for rent in Abu Dhabi, need 100 beds" → https://findproperties.ae/for-rent/labour-camps/uae
- "Hotel apartment for short stay in Dubai" → https://findproperties.ae/for-rent/hotel-apartments/uae
- "I need a penthouse to buy in Dubai with 5 bedrooms" → https://findproperties.ae/for-sale/5-bedroom-penthouse/uae

Important:
- Return ONLY the raw URL
- No JSON, no explanation, no quotes, no markdown
- No extra text
- Always use lowercase
- Fixed Location /uae/ 
- If unsure, use: https://findproperties.ae/for-rent/properties/uae
"""

    try:
        response = model.generate_content(prompt)
        url = response.text.strip()
        return url.strip('"\'')  # Removes quotes and spaces
    except Exception as e:
        print("❌ Gemini API Error:", e)
        return "https://findproperties.ae/for-rent/properties/uae"


# Test queries
# test_queries = [
#     "I want to rent a villa in Dubai",
#     "Looking to buy an apartment in Ajman with payment plan",
#     "Need a bed space in Sharjah, mixed apartment",
#     "Invest in a luxury penthouse in Dubai Marina",
#     "Office space for rent in JVC with parking",
#     "Shop for sale in Dubai Mall, retail space",
#     "Labour camp for rent in Abu Dhabi, need 100 beds",
#     "Hotel apartment for short stay in Dubai",
#     "Looking to purchase a residential building in Ajman",
#     "Warehouse on lease in Dubai Industrial City"
# ]

# for query in test_queries:
#     url = generate_find_properties_url(query)
#     print(f"'{query}' → {url}")

#---------------TEST IN TERMINAL----------------------------------------

# user_query = "i need villa in dubai "
# print("Query:", user_query)
# url = generate_find_properties_url(user_query)
# print("Generated URL:", url)

#------------------------------------------------