import google.generativeai as genai
from dotenv import load_dotenv
import json
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



# --------------------- TEST THE QUERY TO url_v2 ----------------------------------------------


def generate_bayut_url_v2(user_query):
    """
    Generates a Bayut URL with correct handling of:
    - Residential and commercial property types
    - Multiple types → primary in path, others in ?categories=
    - Uses Bayut’s priority order
    """
    # Commercial priority (lower = higher)

    purpose_property = ['to-rent', 'for-sale']
    residential_reproperty_type = ['apartments', 'townhouses', 'villa-compound', 'residential-plots', 'residential-building', 'villas', 'penthouse', 'hotel-apartments', 'residential-floors']

    commercial_property_type = ['warehouses', 'commercial-villas', 'commercial-plots', 'commercial-buildings', 'industrial-land', 'showrooms', 'shops', 'labour-camps', 'bulk-units', 'commercial-floors', 'factories', 'mixed-use-land', 'commerical-properties']

    bedrooms = ['studio', '1', '2', '3', '4', '5', '6', '7', '8+']
    baths = ['1', '2', '3', '4', '5', '6+']
    min_price = ['20000', '30000', '40000', '50000']
    max_price = ['50000', '60000', '85000', '110000']
    area_sqft_min = ['800', '1000', '1500', '2000']
    area_sqft_max = ['800', '1000', '1500', '2000']

    exapmple_url = "https://www.bayut.com/to-rent/studio,1-bedroom-apartments/uae/?categories=townhouses%2Cvillas&price_min=20000&price_max=50000"


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
        "penthouse": "penthouse",
        "hotel apartment": "hotel-apartments",
        "floor": "residential-floors"
    }

    prompt = f"""
            **Situation**
        You are an expert URL generator for real estate queries, specifically focused on the Bayut.com platform. The system requires generating precise, contextually-appropriate URLs based on user search intents for UAE real estate listings.
        
        **Task**
        Generate a precise, well-structured URL for real estate property searches on Bayut.com based on user input, considering property type, transaction type, and default location.
        
        **Objective**
        Create accurate, user-friendly real estate search URLs that match the exact intent of the user's query while maintaining platform-specific URL structures.
        
        **Knowledge**
        Available data sets:
        - commercial_priority: {commercial_priority}
        - commercial_slug_map: {commercial_slug_map}
        - residential_priority: {residential_priority}
        - residential_slug_map: {residential_slug_map}
        
        Critical rules:
        - Strictly use commercial_priority, commercial_slug_map, residential_priority, residential_slug_map for usl priorities and mapping exact keyword in url
        - Don't consider user specified location in the url
        - Always assume UAE as the default location
        - Default to residential property if no specific property type is mentioned
        - Default to rent property if no specific property type is mentioned
        - Prioritize matching user intent with most relevant property category
        - Handle various query types including rent, buy, property types
        
        **Examples**
        1. Query: "i want residential apartment for rent in satwa"
           Response: "https://www.bayut.com/to-rent/apartments/uae/"
        
        2. Query: "i want commercial villa or office for rent in al qouz or international city dubai"
           Response: "https://www.bayut.com/to-rent/offices/uae/?categories=commercial-villas"
        
        3. Query: "looking for villa or apartment to buy"
           Response: "https://www.bayut.com/for-sale/villas/uae/"
        
        Your response must be precise, matching the exact property type, transaction type, and maintaining the standard Bayut.com URL structure. If the query is ambiguous, default to the most likely residential property search. Prioritize clarity and specificity in URL generation.
        
        user_query: {user_query}
    """

    try:
        llm_response = model.generate_content(prompt)
        text = llm_response.text
        # print(text)
        return text



    except Exception as e:
        print(e)
        return "https://www.bayut.com/"


# --------------------- TEST THE QUERY TO url_v2 ----------------------------------------------


# --------------------- TEST THE QUERY TO url_v3 ----------------------------------------------

def parse_query_with_gemini(user_query):
    # --- Allowed parameters ---
    ALLOWED_PARAMS = {
        "purpose_property": ['to-rent', 'for-sale'],
        "property_type": ['apartments', 'townhouses', 'villa-compound', 'residential-plots',
                                      'residential-building', 'villas', 'penthouse', 'hotel-apartments', 'residential-floors',
                                      'warehouses', 'commercial-villas', 'commercial-plots', 'commercial-buildings',
                                      'industrial-land', 'showrooms', 'shops', 'labour-camps', 'bulk-units',
                                      'commercial-floors', 'factories', 'mixed-use-land', 'commerical-properties'
                                      ],
        "bedrooms": ['studio', '1', '2', '3', '4', '5', '6', '7', '8+'],
        "baths": ['1', '2', '3', '4', '5', '6+'],
        "min_price": ['20000', '30000', '40000', '50000'],
        "max_price": ['50000', '60000', '85000', '110000'],
        "area_sqft_min": ['800', '1000', '1500', '2000'],
        "area_sqft_max": ['800', '1000', '1500', '2000']
    }

    # --- Prompt to guide the LLM ---
    SYSTEM_PROMPT = f"""
    You are a real estate query parser. Extract structured data from user queries about property search.
    Only output valid JSON with keys from the list below. Only use values from the allowed lists.
    Do not invent new keys or values.

    Allowed keys and values:
    - purpose_property: {ALLOWED_PARAMS['purpose_property']}
    - property_type: {ALLOWED_PARAMS['property_type']}
    - bedrooms: {ALLOWED_PARAMS['bedrooms']} (use only these strings; 'studio' counts as bedroom type)
    - baths: {ALLOWED_PARAMS['baths']}
    - min_price: {ALLOWED_PARAMS['min_price']}
    - max_price: {ALLOWED_PARAMS['max_price']}
    - area_sqft_min: {ALLOWED_PARAMS['area_sqft_min']}
    - area_sqft_max: {ALLOWED_PARAMS['area_sqft_max']}

    Rules:
    - Only include keys if mentioned or clearly implied.
    - purpose_property key is mandatory, default value is to-rent
    - If property type is residential (e.g., apartment, villa), use 'residential_property_type'.
    - If commercial (e.g., shop, warehouse), use 'commercial_property_type'.
    - Output only a JSON object. No extra text.
    """

    try:
        llm_response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUser Query: {user_query}")
        raw_output = llm_response.text.strip()

        # print(raw_output)
        # return raw_output

        # Clean output (remove markdown if present)
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3]  # Remove ```json and ```

        parsed_json = json.loads(raw_output)

        # print(parsed_json)

        # Validate values are in allowed lists
        cleaned = {}
        for key, value in parsed_json.items():
            if key in ALLOWED_PARAMS:
                if isinstance(value, str):
                    value = [value]  # Convert to list for uniformity
                # Filter only allowed values
                valid_values = [v for v in value if v in ALLOWED_PARAMS[key]]
                if valid_values:
                    cleaned[key] = valid_values[0] if len(valid_values) == 1 else valid_values
            else:
                print(f"Warning: Ignoring unknown key '{key}'")

        return cleaned
    except Exception as e:
        print("Error parsing with Gemini:", str(e))
        # return {}


def build_bayut_url(params):
    # Base URL: purpose + placeholder for location

    print('build_bayut_url fucntion called ------------')
    purpose = params.get("purpose_property", ["to-rent"]) if "purpose_property" in params else "to-rent"
    base_url = f"https://www.bayut.com/{purpose}/"

    # --- Build path components ---
    path_parts = []

    # Bedrooms
    if "bedrooms" in params:
        bed = params["bedrooms"]
        if isinstance(bed, list):
            bed = ",".join(bed)
        else:
            bed = str(bed)
        path_parts.append(f"{bed}-bedroom")

    print('path_parts: ', path_parts)

    prop_type = None
    if "property_type" in params:
        prop_type = params["property_type"]
        if isinstance(prop_type, list):
            path_parts.append(f"-{prop_type[0]}")
        else:
            path_parts.append(f"{prop_type}")

    print('path_parts: ', path_parts)
    # Join path parts
    path_str = "".join(path_parts) + "/uae/"

    print(f"{base_url}{path_str}")

    # --- Query parameters ---
    query_params = {}
    if "baths" in params:
        query_params["facing"] = params["baths"]
    if "min_price" in params:
        query_params["price_min"] = params["min_price"]
    if "max_price" in params:
        query_params["price_max"] = params["max_price"]
    if "area_sqft_min" in params:
        query_params["area_min"] = params["area_sqft_min"]
    if "area_sqft_max" in params:
        query_params["area_max"] = params["area_sqft_max"]

    print(f"query_params: {query_params}")

    # # Handle categories (for property type in query)
    # if "property_type" in params:
    #     cat_list = []
    #     val = params["property_type"]
    #     cat_list.extend(val if isinstance(val, list) else [val])
    #     query_params["categories"] = "%2C".join(cat_list)  # URL encoded comma
    #
    # # Encode query string
    # query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
    #
    # # Final URL: insert location later, so we leave a marker or placeholder
    # constructed_url = base_url + path_str
    # if query_string:
    #     constructed_url += "?" + query_string
    #
    # return constructed_url


# --------------------- TEST THE QUERY TO url_v3 ----------------------------------------------



test_query = "I am looking for apartment or villa or townhouses for rent and price between 20k to 30k and should have 2 bed and 1/2 baths and 800 square foot"
# test_query = "I want a apartment for rent in jvc dubai in price range 8k and 900 suqure foot"
paras = parse_query_with_gemini(test_query)
print(paras)
print('-----------------------------------spliter 1 --------------------------')
my_url = build_bayut_url(paras)
print('-----------------------------------spliter 2 --------------------------')
print(my_url)


# https://www.bayut.com/to-rent/1,2,3,4-bedroom-townhouses/uae/?categories=villa-compound&price_min=20000&price_max=50000&baths_in=1%2C2%2C3

