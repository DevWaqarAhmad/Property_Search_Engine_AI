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
    Generates a Bayut URL with strict logic:
    - If query is about 'property', 'residence', or any residential type → use residential logic
    - Only if 'commercial' is mentioned AND no residential keyword → use commercial
    """
    # Commercial priority
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

    # Keywords that force RESIDENTIAL handling
    residential_keywords = {
        "property", "properties", "residence", "residential",
        "apartment", "villa", "townhouse", "penthouse",
        "hotel apartment", "floor", "land", "building"
    }

    # Normalize query
    query_lower = user_query.lower().strip()

    # Check if query contains ANY residential keyword
    has_residential_keyword = any(word in query_lower for word in residential_keywords)

    # If user said "property", "residence", etc. → force residential
    if has_residential_keyword:
        # Use Gemini to extract types, intent, location
        prompt = f"""
        Analyze the query and extract:
        Intent: rent or sale
        Property Types: list all mentioned types (e.g., apartment, villa)
        Location: city or emirate like Dubai, Ajman. If not mentioned, use 'uae'

        Rules:
        - Treat all as residential
        - Return types in order of mention

        Respond in exactly this format:
        Intent: rent
        Property Types: apartment, villa
        Location: dubai

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
                    prop_types = [pt.strip() for pt in raw.split(",") if pt.strip()]
                elif "location:" in line:
                    location = line.split(":", 1)[1].strip()

            location_slug = location.replace(" ", "-")
            base = "to-rent" if "rent" in intent else "for-sale"

            # If no types, use /property/
            if not prop_types:
                return f"https://www.bayut.com/{base}/property/{location_slug}/"

            # Sort by priority
            matched = [t for t in prop_types if t in residential_priority]
            if not matched:
                return f"https://www.bayut.com/{base}/property/{location_slug}/"

            sorted_types = sorted(matched, key=lambda x: residential_priority[x])
            primary_type = sorted_types[0]
            primary_slug = residential_slug_map.get(primary_type, "property")

            # Extra types in categories
            extra_types = sorted_types[1:]
            if extra_types:
                extra_slugs = [residential_slug_map.get(t, "property") for t in extra_types]
                categories_param = "?categories=" + "%2C".join(extra_slugs)
            else:
                categories_param = ""

            return f"https://www.bayut.com/{base}/{primary_slug}/{location_slug}/{categories_param}"

        except Exception:
            return "https://www.bayut.com/"

    # Otherwise: no residential keyword → check for commercial
    elif "commercial" in query_lower:
        # Extract intent and location only
        prompt = f"""
        Analyze the query and extract:
        Intent: rent or sale
        Location: city or emirate like Dubai, Ajman. If not mentioned, use 'uae'

        Respond in exactly this format:
        Intent: rent
        Location: dubai

        Query: {user_query}
        """

        try:
            response = model.generate_content(prompt)
            text = response.text.strip().lower()

            intent = "sale"
            location = "uae"

            for line in text.splitlines():
                if "intent:" in line:
                    intent = line.split(":", 1)[1].strip()
                elif "location:" in line:
                    location = line.split(":", 1)[1].strip()

            location_slug = location.replace(" ", "-")
            base = "to-rent" if "rent" in intent else "for-sale"

            return f"https://www.bayut.com/{base}/commercial/{location_slug}/"

        except Exception:
            return "https://www.bayut.com/"

    # Fallback
    return "https://www.bayut.com/"
# --------------------- TEST THE QUERY TO URLs ----------------------------------------------
user_query = "share commerical properties in ajman"
print("Query:", user_query)
url = generate_bayut_url(user_query)
print("Generated URL:", url)