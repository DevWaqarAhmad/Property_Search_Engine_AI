import google.generativeai as genai
from dotenv import load_dotenv
import json
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# --------------------- TEST THE QUERY TO url_v3 ----------------------------------------------
# def parse_query_with_gemini(user_query):
#     # --- Allowed parameters (Aligned with findproperties.ae) ---
#     ALLOWED_PARAMS = {
#         "purpose_property": ['for-rent', 'for-sale', 'for-sharing'],
#         "property_type": [
#             'apartments', 'villa', 'land', 'office', 'shops',
#             'building', 'warehouse', 'showroom', 'labour-camps',
#             'townhouse', 'hotel-apartments', 'penthouse', 'other-commercial'
#         ],
#         "bedrooms": ['studio', '1', '2', '3', '4', '5', '6', '7', '8+', '9', '10+'],
#     }

#     # --- Prompt to guide the LLM ---
#     SYSTEM_PROMPT = f"""
#     You are a real estate query parser. Extract structured data from user queries about property search.
#     Only output valid JSON with keys from the list below. Only use values from the allowed lists.
#     Do not invent new keys or values.

#     Allowed keys and values:
#     - purpose_property: {ALLOWED_PARAMS['purpose_property']}
#     - property_type: {ALLOWED_PARAMS['property_type']}
#     - bedrooms: {ALLOWED_PARAMS['bedrooms']} (use only these strings; 'studio' counts as bedroom type)

#     Rules:
#     - Only include keys if mentioned or clearly implied.
#     - purpose_property key is mandatory, default value is for-rent
#     - If user says 'rent', set purpose_property to 'for-rent'
#     - If user says 'sale', set to 'for-sale'
#     - If user says 'sharing', set to 'for-sharing'
#     - Output only a JSON object. No extra text.
#     """

#     try:
#         llm_response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUser Query: {user_query}")
#         raw_output = llm_response.text.strip()

#         def is_positive_number(val):
#             try:
#                 num = float(val)
#                 return num > 0
#             except (ValueError, TypeError):
#                 return False

#         # Clean output
#         if raw_output.startswith("```json"):
#             raw_output = raw_output[7:-3]

#         parsed_json = json.loads(raw_output)

#         cleaned = {}
#         for key, value in parsed_json.items():
#             if key in ALLOWED_PARAMS:
#                 if isinstance(value, str):
#                     value = [value]
#                 valid_values = [v for v in value if v in ALLOWED_PARAMS[key]]
#                 if valid_values:
#                     cleaned[key] = valid_values[0] if len(valid_values) == 1 else valid_values
#             elif key in ["min_price", "max_price", "area_sqft_min", "area_sqft_max"]:
#                 if isinstance(value, list):
#                     value = value[0]
#                 if is_positive_number(value):
#                     cleaned[key] = str(int(float(value)))
#             else:
#                 print(f"Warning: Ignoring unknown key '{key}'")

#         # Ensure purpose_property is valid
#         if "purpose_property" not in cleaned or cleaned["purpose_property"] not in ALLOWED_PARAMS["purpose_property"]:
#             cleaned["purpose_property"] = "for-rent"

#         return cleaned

#     except Exception as e:
#         print("Error parsing with Gemini:", str(e))
#         return {"purpose_property": "for-rent"}
def parse_query_with_gemini(user_query):
    # --- Allowed parameters ---
    ALLOWED_PARAMS = {
        "purpose_property": ['to-rent', 'for-sale'],
        "property_type": ['apartments', 'villa', 'land', 'office',
                                      'shops', 'buildings', 'warehouse', 'showroom', 'labour-camps',
                                      'townhouse', 'hotel-apartments', 'other-commercial', 'penthouse'
                                      ],
        "bedrooms": ['studio', '1', '2', '3', '4', '5', '6', '7', '8','9','10','11','12','13','14','15','16','17','18','19','20+'],
        "baths": ['studio', '1', '2', '3', '4', '5', '6', '7', '8','9','10','11','12','13','14','15','16','17','18','19','20+']
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
    - min_price: any positive number (in AED), optional
    - max_price: any positive number (in AED), optional
    - area_sqft_min: any positive number (square feet), optional
    - area_sqft_max: any positive number (square feet), optional
    - target_location: any area or location specified in the user query 

    Rules:
    - Only include keys if mentioned or clearly implied.
    - purpose_property key is mandatory, default value is to-rent
    - target_location will be a list if, more than one locations mentioned in the user query.
    - Output only a JSON object. No extra text.
    """

    try:
        llm_response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUser Query: {user_query}")
        raw_output = llm_response.text.strip()

        # print(raw_output)
        # return raw_output
        def is_positive_number(val):
            try:
                num = float(val)
                return num > 0
            except (ValueError, TypeError):
                return False

        # Clean output (remove markdown if present)
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3]  # Remove ```json and ```

        parsed_json = json.loads(raw_output)

        print('parsed_json:', parsed_json)

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
            elif key in ["min_price", "max_price", "area_sqft_min", "area_sqft_max"]:
                # Handle dynamic numeric fields
                if isinstance(value, list):
                    value = value[0]  # Take first if list
                if is_positive_number(value):
                    cleaned[key] = str(int(float(value)))  # Normalize to string integer
            elif key == "target_location":
                if isinstance(value, str) and value.strip():
                    cleaned[key] = value.strip()
                elif isinstance(value, list):
                    cleaned[key] = value[0]
                else:
                    cleaned[key] = str(value)
            else:
                print(f"Warning: Ignoring unknown key '{key}'")

        return cleaned
    except Exception as e:
        print("Error parsing with Gemini:", str(e))
        # return {}


def build_find_properties_url(params):
    """
    Creates a clean, URL using only purpose, bedrooms, and property type.
    Format: https://findproperties.ae/{purpose}/{bedroom}-{property}/uae
    """
    # Convert string to dict if needed
    if isinstance(params, str):
        try:
            params = json.loads(params)
        except Exception as e:
            print("Error parsing params string:", e)
            return None

    # Base URL (fixed extra space)
    base_url = "https://findproperties.ae/"

    # --- 1. Purpose (for-rent, for-sale) ---
    purpose = params.get("purpose_property", "to-rent")
    if isinstance(purpose, list):
        purpose = purpose[0]
    purpose_path = "for-rent" if purpose == "to-rent" else "for-sale"

    # --- 2. Bedrooms (studio, 1, 2, ..., 8+) ---
    bedroom_str = "any"
    if "bedrooms" in params:
        bed = params["bedrooms"]
        if isinstance(bed, list):
            bed = bed[0]
        bed = str(bed).strip()

        if bed == "studio":
            bedroom_str = "studio"
        elif bed in ["8+", "9", "10+"]:
            bedroom_str = "8-plus-bedroom"
        else:
            bedroom_str = f"{bed}-bedroom"

    # --- 3. Property Type ---
    property_type = "properties"
    if "property_type" in params:
        p_type = params["property_type"]
        if isinstance(p_type, list):
            p_type = p_type[0]
        p_type = str(p_type).lower().strip()

        # Clean mapping — only what's needed
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
            'other-commercial': 'other-commercial',
        }
        property_type = type_map.get(p_type, "properties")

    # --- Build Final Path ---
    if bedroom_str == "any":
        path_segment = property_type
    else:
        path_segment = f"{bedroom_str}-{property_type}"

    url_path = f"{purpose_path}/{path_segment}/uae"
    final_url = base_url + url_path

    return final_url


# --------------------- TEST THE QUERY TO url ----------------------------------------------

# test_query = "i want to buy a 4 bedrooms and 3 bathroom aprtment in dubai"
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