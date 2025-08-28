import google.generativeai as genai
from dotenv import load_dotenv
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# --------------------- GENERATE URL FUNCTION -----------------------------------------------
# def generate_bayut_url(user_query):
#     """
#     Generates a Bayut URL with correct handling of:
#     - Residential and commercial property types
#     - Multiple types → primary in path, others in ?categories=
#     - Uses Bayut’s priority order
#     """
#     # Commercial priority (lower = higher)
#     commercial_priority = {
#         "office": 1,
#         "warehouse": 2,
#         "showroom": 7,
#         "shop": 8,
#         "labour camp": 9,
#         "bulk unit": 10,
#         "factory": 12,
#         "mixed use land": 13,
#         "other": 14
#     }

#     # Commercial slug map
#     commercial_slug_map = {
#         "office": "offices",
#         "warehouse": "warehouses",
#         "showroom": "showrooms",
#         "shop": "shops",
#         "labour camp": "labour-camps",
#         "bulk unit": "bulk-units",
#         "factory": "factories",
#         "industrial land": "industrial-land",
#         "mixed use land": "mixed-use-land",
#         "other": "commercial"
#     }

#     # Residential priority
#     residential_priority = {
#         "apartment": 1,
#         "townhouse": 2,
#         "villa compound": 3,
#         "land": 4,
#         "building": 5,
#         "villa": 6,
#         "penthouse": 7,
#         "hotel apartment": 8,
#         "floor": 9
#     }

#     # Residential slug map
#     residential_slug_map = {
#         "apartment": "apartments",
#         "townhouse": "townhouses",
#         "villa compound": "villa-compounds",
#         "land": "residential-plots",
#         "building": "residential-building",
#         "villa": "villas",
#         "penthouse": "penthouses",
#         "hotel apartment": "hotel-apartments",
#         "floor": "residential-floors"
#     }

#     prompt = f"""
#     Analyze the query and extract:
#     Intent: rent or sale
#     Property Types: list all mentioned types (e.g., shop, showroom, apartment)
#     Location: city or emirate like Dubai, Ajman. If not mentioned, use 'uae'

#     Rules:
#     - If query has 'commercial', 'business', 'retail' → include 'other' in property types
#     - Treat 'villa', 'land', 'building', 'floor' as residential only
#     - Return types in order of mention
#     - Only include actual property types. Do not add 'residence', 'property', 'home', 'share' as types.

#     Respond in exactly this format:
#     Intent: rent
#     Property Types: shop, showroom
#     Location: ajman

#     Query: {user_query}
#     """

#     try:
#         response = model.generate_content(prompt)
#         text = response.text.strip().lower()

#         intent = "sale"
#         prop_types = []
#         location = "uae"

#         for line in text.splitlines():
#             if "intent:" in line:
#                 intent = line.split(":", 1)[1].strip()
#             elif "property types:" in line:
#                 raw = line.split(":", 1)[1].strip()
        
#                 raw_types = [pt.strip() for pt in raw.split(",") if pt.strip()]
            
#                 prop_types = [t for t in raw_types if t in commercial_priority or t in residential_priority]
#             elif "location:" in line:
#                 location = line.split(":", 1)[1].strip()

#         location_slug = location.replace(" ", "-")
#         base = "to-rent" if "rent" in intent else "for-sale"

    
#         if "commercial" in user_query.lower() or "business" in user_query.lower() or "retail" in user_query.lower():
#             return f"https://www.bayut.com/{base}/commercial/{location_slug}/"

#         # Commercial matches
#         commercial_matches = [t for t in prop_types if t in commercial_priority]
#         if commercial_matches:
#             sorted_commercial = sorted(commercial_matches, key=lambda x: commercial_priority[x])
#             primary_type = sorted_commercial[0]
#             primary_slug = commercial_slug_map.get(primary_type, "commercial")
#             extra_types = sorted_commercial[1:]
#             if extra_types:
#                 extra_slugs = [commercial_slug_map.get(t, "commercial") for t in extra_types]
#                 categories_param = "?categories=" + "%2C".join(extra_slugs)
#             else:
#                 categories_param = ""
#             return f"https://www.bayut.com/{base}/{primary_slug}/{location_slug}/{categories_param}"

       
#         residential_matches = [t for t in prop_types if t in residential_priority]
#         if residential_matches:
#             sorted_residential = sorted(residential_matches, key=lambda x: residential_priority[x])
#             primary_type = sorted_residential[0]
#             primary_slug = residential_slug_map.get(primary_type, primary_type.replace(" ", "-"))
#             extra_types = sorted_residential[1:]
#             if extra_types:
#                 extra_slugs = [residential_slug_map.get(t, t.replace(" ", "-")) for t in extra_types]
#                 categories_param = "?categories=" + "%2C".join(extra_slugs)
#             else:
#                 categories_param = ""
#             return f"https://www.bayut.com/{base}/{primary_slug}/{location_slug}/{categories_param}"

    
#         return f"https://www.bayut.com/{base}/property/{location_slug}/"

#     except Exception:
#         return "https://www.bayut.com/"




#------------PROMPT---------------
def generate_bayut_url(user_query):
    """
    Generates a Bayut URL with:
    - Fixed /uae/ location
    - Intent: rent or sale
    - Residential/commercial detection
    - Multiple types → primary in path, others in ?categories=
    - Uses Bayut’s priority order
    """
    # Commercial priority (lower = higher)
    commercial_priority = {
        "office": 1,
        "warehouse": 2,
        "showroom": 7,
        "shop": 8,
        "labour camp": 9,
        "bulk unit": 10,
        "factory": 12,
        "mixed use land": 13,
        "other": 14
    }

    # Commercial slug map
    commercial_slug_map = {
        "office": "offices",
        "warehouse": "warehouses",
        "showroom": "showrooms",
        "shop": "shops",
        "labour camp": "labour-camps",
        "bulk unit": "bulk-units",
        "factory": "factories",
        "industrial land": "industrial-land",
        "mixed use land": "mixed-use-land",
        "villa": "commercial-villas",
        "land": "commercial-plots",
        "building": "commercial-buildings",
        "floor": "commercial-floors",
        "other": "commercial"
    }

    # Residential priority
    residential_priority = {
        "apartment": 1,
        "townhouse": 2,
        "villa compound": 3,
        "land": 4,
        "building": 5,
        "villa": 6,
        "penthouse": 7,
        "hotel apartment": 8,
        "floor": 9
    }

    # Residential slug map
    residential_slug_map = {
        "apartment": "apartments",
        "townhouse": "townhouses",
        "villa compound": "villa-compounds",
        "land": "residential-plots",
        "building": "residential-building",
        "villa": "villas",
        "penthouse": "penthouses",
        "hotel apartment": "hotel-apartments",
        "floor": "residential-floors"
    }

    prompt = f"""
     **Situation**
     You are an expert URL generator for real estate queries on Bayut.com. Your role is to generate **exact, platform-compliant URLs** based on user search intent for properties in the UAE.

     **Task**
     Analyze the user query and generate a precise Bayut.com URL with:
         - Correct transaction type: `to-rent` or `for-sale`
         - Primary property type in the path
         - Additional types in `?categories=` (comma-encoded as %2C)
         - Default location: `/uae/`
         - Correct slug format (plural, hyphenated)

     **Objective**
     Generate a 100% accurate, production-ready URL that matches Bayut’s real-world structure and user intent.

     **Knowledge & Rules**

     1. **Transaction Type Detection**
         - Rent Intent: "rent", "rental", "rented", "lease", "leasing"
         - Sale Intent: "buy", "for sale", "purchase", "need", "looking to buy", "investment"
         - Default: `to-rent` if ambiguous

     2. **Location**
         - Always use `/uae/` — ignore any specific city (Dubai, Ajman, etc.)
         - Never include `dubai`, `sharjah`, etc. in URL

     3. **Property Type Priority (Residential)**
         - Use this order for sorting:
             1. apartment → apartments
             2. townhouse → townhouses
             3. villa compound → villa-compounds
             4. land → residential-plots
             5. building → residential-building
             6. villa → villas
             7. penthouse → penthouses
             8. hotel apartment → hotel-apartments
             9. floor → residential-floors

     4. **Commercial Detection**
         - If query contains: "commercial", "business", "retail", or commercial-specific types → treat as commercial
         - Commercial types:
             - "office" → offices
             - "warehouse" → warehouses
             - "shop" → shops
             - "labour camp" → labour-camps
             - "bulk unit" → bulk-units
             - "factory" → factories
             - "industrial land" → industrial-land
             - "mixed use land" → mixed-use-land
             - "showroom" → showrooms
             - "villa" + commercial context → commercial-villas
             - "land" + commercial context → commercial-plots
             - "floor" + commercial context → commercial-floors

     5. **Special Commercial URLs**
         - If "commercial villa" → `/commercial-villas/`
         - If "commercial plot" or "industrial land" → `/commercial-plots/`
         - If general "commercial property" → `/commercial/`

     6. **Multiple Types Handling**
         - Primary type: highest priority (based on order above)
         - Others: added to `?categories=` with `%2C` separator
         - Example: `?categories=villas%2Cresidential-floors`

     7. **Fallback Rules**
         - If no valid property type: use `/property/`
         - If no intent: default to `to-rent`
         - If "property" + rent → `/to-rent/property/uae/`
         - If "property" + sale → `/for-sale/property/uae/`

     8. **Output Format**
         - Only return the **full URL** — nothing else
         - No extra text, no explanation
         - Use correct slugs and encoding

     **Examples**
         1. "rent apartments and villas" → https://www.bayut.com/to-rent/apartments/uae/?categories=villas
         2. "buy land, floor and apartment" → https://www.bayut.com/for-sale/apartments/uae/?categories=residential-plots%2Cresidential-floors
         3. "commercial villas for rent" → https://www.bayut.com/to-rent/commercial-villas/uae/
         4. "lease shops and showrooms" → https://www.bayut.com/to-rent/shops/uae/?categories=showrooms
         5. "need a property for sale" → https://www.bayut.com/for-sale/property/uae/
         6. "looking for rental property" → https://www.bayut.com/to-rent/property/uae/
         7. "commercial plots in uae" → https://www.bayut.com/to-rent/commercial-plots/uae/
         8. "buy villa compound, penthouse and land" → https://www.bayut.com/for-sale/villa-compounds/uae/?categories=penthouses%2Cresidential-plots

     **Now process this query:**
     "{user_query}"
     """

    try:
        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        # Extract URL from response (in case model adds extra text)
        if "https://" in raw_output:
            start = raw_output.find("https://")
            url = raw_output[start:].split()[0].strip().strip('"').strip("'")
        else:
            url = raw_output

        # Validate and return clean URL
        if url.startswith("https://www.bayut.com/"):
            return url
        else:
            # Fallback logic in case Gemini fails
            intent = "for-sale" if any(word in user_query.lower() for word in ["buy", "sale", "purchase"]) else "to-rent"
            return f"https://www.bayut.com/{intent}/property/uae/"

    except Exception as e:
        return "https://www.bayut.com/to-rent/property/uae/"
# --------------------- TEST THE QUERY TO URLs ----------------------------------------------
user_query = "i want to buy apartment and villa in ajamn"
print("Query:", user_query)
url = generate_bayut_url(user_query)
print("Generated URL:", url)


#------------PROMPT---------------
