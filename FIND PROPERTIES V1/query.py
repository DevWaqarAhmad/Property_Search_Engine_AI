import google.generativeai as genai
from dotenv import load_dotenv
import json
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# --------------------- PARSE QUERY WITH GEMINI ----------------------------------------------
def parse_query_with_gemini(user_query):
    ALLOWED_PARAMS = {
        "purpose_property": ['for-rent', 'for-sale', 'for-sharing'],
        "property_type": [
            'apartments', 'villa', 'land', 'office', 'shops',
            'building', 'warehouse', 'showroom', 'labour-camps',
            'townhouse', 'hotel-apartments', 'penthouse', 'other-commercial'
        ],
        "bedrooms": ['studio', '1', '2', '3', '4', '5', '6', '7', '8+', '9', '10+'],
    }
    SYSTEM_PROMPT = f"""
    You are a real estate query parser. Extract structured data from user queries about property search.
    Only output valid JSON with keys from the list below. Only use values from the allowed lists.
    Do not invent new keys or values.

    Allowed keys and values:
    - purpose_property: {ALLOWED_PARAMS['purpose_property']}
    - property_type: {ALLOWED_PARAMS['property_type']}
    - bedrooms: {ALLOWED_PARAMS['bedrooms']} (use only these strings; 'studio' counts as bedroom type)

    Rules:
    - Only include keys if mentioned or clearly implied.
    - purpose_property key is mandatory, default value is for-rent
    - If user says 'rent', set purpose_property to 'for-rent'
    - If user says 'sale', set to 'for-sale'
    - If user says 'sharing', set to 'for-sharing'
    - Output only a JSON object. No extra text.
    """

    try:
        llm_response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUser Query: {user_query}")
        raw_output = llm_response.text.strip()

        def is_positive_number(val):
            try:
                num = float(val)
                return num > 0
            except (ValueError, TypeError):
                return False

        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3]

        parsed_json = json.loads(raw_output)

        cleaned = {}
        for key, value in parsed_json.items():
            if key in ALLOWED_PARAMS:
                if isinstance(value, str):
                    value = [value]
                valid_values = [v for v in value if v in ALLOWED_PARAMS[key]]
                if valid_values:
                    cleaned[key] = valid_values[0] if len(valid_values) == 1 else valid_values
            elif key in ["min_price", "max_price", "area_sqft_min", "area_sqft_max"]:
                if isinstance(value, list):
                    value = value[0]
                if is_positive_number(value):
                    cleaned[key] = str(int(float(value)))
            else:
                print(f"Warning: Ignoring unknown key '{key}'")

        if "purpose_property" not in cleaned or cleaned["purpose_property"] not in ALLOWED_PARAMS["purpose_property"]:
            cleaned["purpose_property"] = "for-rent"

        return cleaned

    except Exception as e:
        print("Error parsing with Gemini:", str(e))
        return {"purpose_property": "for-rent"}


#-------------------------------- BUILD FIND PROPERTIES URL -------------------------------
def build_find_properties_url(params):
    if isinstance(params, str):
        try:
            params = json.loads(params)
        except Exception as e:
            print("Error parsing params string:", e)
            return None
    base_url = "https://findproperties.ae/"

    # --- Purpose ---
    purpose = params.get("purpose_property", "for-rent")
    if isinstance(purpose, list):
        purpose = purpose[0]

    purpose_path = "for-rent"
    if purpose == "for-sale":
        purpose_path = "for-sale"
    elif purpose == "for-sharing":
        purpose_path = "for-sharing"

    # --- Bedrooms ---
    bedroom_str = "any"
    if "bedrooms" in params:
        bed = params["bedrooms"]
        if isinstance(bed, list):
            bed = bed[0]
        else:
            bed = str(bed)
        if bed == "studio":
            bedroom_str = "studio"
        elif bed == "8+":
            bedroom_str = "8-plus-bedroom"
        else:
            bedroom_str = f"{bed}-bedroom"

    # --- Property Type ---
    property_type_str = "properties"
    if "property_type" in params:
        p_type = params["property_type"]
        if isinstance(p_type, list):
            p_type = p_type[0]
        p_type = str(p_type).lower().strip()

        type_map = {
            'apartment': 'apartments',
            'apartments': 'apartments',
            'villa': 'villa',
            'villas': 'villa',
            'land': 'land',
            'office': 'office',
            'shop': 'shops',
            'shops': 'shops',
            'building': 'building',
            'warehouse': 'warehouse',
            'showroom': 'showroom',
            'labour-camp': 'labour-camps',
            'labour-camps': 'labour-camps',
            'labor camp': 'labour-camps',
            'townhouse': 'townhouse',
            'hotel-apartment': 'hotel-apartments',
            'penthouse': 'penthouse',
            'other commercial': 'other-commercial',
        }
        property_type_str = type_map.get(p_type, "properties")

    # Combine bedroom and property type
    if bedroom_str == "any":
        path_segment = property_type_str
    else:
        path_segment = f"{bedroom_str}-{property_type_str}"

    # Final URL
    url_path = f"{purpose_path}/{path_segment}/uae"
    final_url = base_url + url_path

    return final_url


# --------------------- TEST THE QUERY TO url_v3 ----------------------------------------------

# test_query = "i want a villa in sharjah with 4 bedrooms"
# paras = parse_query_with_gemini(test_query)
# print('------------Started---------------')
# print(paras)
# print('-----------------------------------spliter 1 --------------------------')
# my_url = build_find_properties_url(paras)
# print('-----------------------------------spliter 2 --------------------------')
# print(my_url)
#https://findproperties.ae/for-rent/4-bedroom-villa/uae


# test_queries = [
#     "I want a 3 bedroom apartment for rent in Dubai",
#     "Looking for a villa for sale in Abu Dhabi",
#     "Need a studio apartment for sharing in Sharjah",
#     "Find me a 4 bedroom villa for rent in UAE",
#     "I need a shop for rent in Dubai",
#     "Looking for a penthouse for sale in Dubai Marina",
#     "Want a warehouse for rent in industrial area",
#     "Find a 2 bedroom townhouse for rent",
#     "Looking for a labour camp for rent in Abu Dhabi",
#     "Need a hotel apartment for short stay in Dubai"
# ]

# for q in test_queries:
#     print("\nQuery:", q)
#     params = parse_query_with_gemini(q)
#     print("Parsed:", params)
#     url = build_find_properties_url(params)
#     print("URL:  ", url)
