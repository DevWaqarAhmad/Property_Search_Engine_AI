import google.generativeai as genai
from dotenv import load_dotenv
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# --------------------- GENERATE URL FUNCTION -----------------------------------------------
def generate_bayut_url(user_query):
    """
    Generates a Bayut URL with correct handling of:
    - Residential and commercial property types
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
    Analyze the query and extract:
    Intent: rent or sale
    Property Types: list all mentioned types (e.g., shop, showroom, apartment)
    Location: city or emirate like Dubai, Ajman. If not mentioned, use 'uae'

    Rules:
    - If query has 'commercial', 'business', 'retail' → include 'other' in property types
    - Treat 'villa', 'land', 'building', 'floor' as residential only
    - Return types in order of mention
    - Only include actual property types. Do not add 'residence', 'property', 'home', 'share' as types.

    Respond in exactly this format:
    Intent: rent
    Property Types: shop, showroom
    Location: ajman

    Query: {user_query}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip().lower()

        intent = "sale"
        prop_types = []
        location = "uae"

        for line in text.splitlines():
            if "intent:" in line:
                intent = line.split(":", 1)[1].strip()
            elif "property types:" in line:
                raw = line.split(":", 1)[1].strip()
        
                raw_types = [pt.strip() for pt in raw.split(",") if pt.strip()]
            
                prop_types = [t for t in raw_types if t in commercial_priority or t in residential_priority]
            elif "location:" in line:
                location = line.split(":", 1)[1].strip()

        location_slug = location.replace(" ", "-")
        base = "to-rent" if "rent" in intent else "for-sale"

    
        if "commercial" in user_query.lower() or "business" in user_query.lower() or "retail" in user_query.lower():
            return f"https://www.bayut.com/{base}/commercial/{location_slug}/"

        # Commercial matches
        commercial_matches = [t for t in prop_types if t in commercial_priority]
        if commercial_matches:
            sorted_commercial = sorted(commercial_matches, key=lambda x: commercial_priority[x])
            primary_type = sorted_commercial[0]
            primary_slug = commercial_slug_map.get(primary_type, "commercial")
            extra_types = sorted_commercial[1:]
            if extra_types:
                extra_slugs = [commercial_slug_map.get(t, "commercial") for t in extra_types]
                categories_param = "?categories=" + "%2C".join(extra_slugs)
            else:
                categories_param = ""
            return f"https://www.bayut.com/{base}/{primary_slug}/{location_slug}/{categories_param}"

       
        residential_matches = [t for t in prop_types if t in residential_priority]
        if residential_matches:
            sorted_residential = sorted(residential_matches, key=lambda x: residential_priority[x])
            primary_type = sorted_residential[0]
            primary_slug = residential_slug_map.get(primary_type, primary_type.replace(" ", "-"))
            extra_types = sorted_residential[1:]
            if extra_types:
                extra_slugs = [residential_slug_map.get(t, t.replace(" ", "-")) for t in extra_types]
                categories_param = "?categories=" + "%2C".join(extra_slugs)
            else:
                categories_param = ""
            return f"https://www.bayut.com/{base}/{primary_slug}/{location_slug}/{categories_param}"

    
        return f"https://www.bayut.com/{base}/property/{location_slug}/"

    except Exception:
        return "https://www.bayut.com/"
# --------------------- TEST THE QUERY TO URLs ----------------------------------------------
user_query = "i want to buy apartment and villa in ajamn"
print("Query:", user_query)
url = generate_bayut_url(user_query)
print("Generated URL:", url)
