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
    - Fixed /uae/ location
    - Intent: rent, sale, or sharing
    Returns: raw URL string only
    """
    prompt = f"""
You are a precise URL generator for findproperties.ae. Analyze the user's query and return ONLY the correct search URL.

User Query: "{user_query}"

Rules:

1. Detect the **property type** and map to:
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

2. Detect the **intent**:
   - rent, rental, lease, on rent → "for-rent"
   - buy, sale, purchase, invest → "for-sale"
   - sharing, room, bed space, roommate → "for-sharing"
   If unsure, default to "for-rent"

3. Generate URL in this format:
   https://findproperties.ae/{{intent}}/{{slug}}/uae

Examples:
- "I want to rent a villa in Dubai" → https://findproperties.ae/for-rent/villa/uae
- "Looking to buy an apartment in Ajman" → https://findproperties.ae/for-sale/apartments/uae
- "Need a bed space in Sharjah" → https://findproperties.ae/for-sharing/properties/uae

Important:
- Return ONLY the raw URL
- No JSON, no explanation, no quotes, no markdown
- No extra text
- Always end with "/uae"
- If unsure, use: https://findproperties.ae/for-rent/properties/uae
"""

    try:
        response = model.generate_content(prompt)
        url = response.text.strip()
        # Clean up any surrounding quotes or spaces
        return url.strip('"\'')

    except Exception as e:
        print("❌ Gemini API Error:", e)
        return "https://findproperties.ae/for-rent/properties/uae"


# Test queries
test_queries = [
    "I want to rent a villa in Dubai",
    "Looking to buy an apartment in Ajman with payment plan",
    "Need a bed space in Sharjah, mixed apartment",
    "Invest in a luxury penthouse in Dubai Marina",
    "Office space for rent in JVC with parking",
    "Shop for sale in Dubai Mall, retail space",
    "Labour camp for rent in Abu Dhabi, need 100 beds",
    "Hotel apartment for short stay in Dubai",
    "Looking to purchase a residential building in Ajman",
    "Warehouse on lease in Dubai Industrial City"
]

for query in test_queries:
    url = generate_find_properties_url(query)
    print(f"'{query}' → {url}")

#---------------TEST IN TERMINAL----------------------------------------

# user_query = "Find me a shop for rent in Dubai above 20,000 AED monthly"
# print("Query:", user_query)
# url = generate_find_properties_url(user_query)
# print("Generated URL:", url)
