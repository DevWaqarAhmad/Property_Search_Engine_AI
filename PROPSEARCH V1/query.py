import google.generativeai as genai
from dotenv import load_dotenv
import json
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")



# ------------------------ QUERY TO PARAMS PARSED -----------------------

def parse_query_with_gemini(user_query):
    # --- Allowed parameters ---
    ALLOWED_PARAMS = {
        "purpose_property": ['to-rent', 'for-sale'],
        "property_type": ['apartments', 'villas', 'land', 'office',
                                      'shops', 'buildings', 'warehouse', 'bungalows', 'labour-camps',
                                      'townhouses', 'hotel-apartments', 'other-commercial', 'penthouses'
                                      ],
        "bedrooms": ['studio', '1', '2', '3', '4', '5', '6+'],
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


# ----------------------------- PARAMS TO URL ---------------------------

def build_prop_search_url(params):
    """
    Build URL from parsed params.
    Supports:
      - purpose_property (rent/sale)
      - property_type (mapped to residential_types)
      - price filter (min_price, max_price)
      - beds filter (single/multiple)
    """

    # Mapping property types to residential_types IDs
    PROPERTY_TYPE_MAP = {
        "villas": 1,
        "apartments": 2,
        "townhouses": 4,
        "hotel-apartments": 5,
        "bungalows": 6,
        "penthouses": 3
    }

    purpose = params.get("purpose_property", "to-rent")

    # Set base URL based on purpose
    if purpose == "for-sale":
        base_url = "https://propsearch.ae/dubai-properties-for-sale/by-location"
    else:
        base_url = "https://propsearch.ae/dubai-properties-to-rent/by-location"

    query_parts = []

    # Property type filter
    property_types = params.get("property_type")
    if property_types:
        if isinstance(property_types, str):
            property_types = [property_types]
        ids = [str(PROPERTY_TYPE_MAP.get(pt)) for pt in property_types if pt in PROPERTY_TYPE_MAP]
        if ids:
            residential_param = "%2C".join(ids)
            query_parts.append(f"residential_types={residential_param}")

    # Beds filter
    beds = params.get("beds") or params.get("bedrooms")
    if beds:
        if isinstance(beds, list):   # multiple beds
            beds_param = "%2C".join(map(str, beds))
        else:  # single bed
            beds_param = str(beds)
        query_parts.append(f"beds={beds_param}")

    # Price filter
    min_price = params.get("min_price")
    max_price = params.get("max_price")

    price_key = "price" if purpose == "for-sale" else "price_l"

    if min_price and max_price:
        query_parts.append(f"{price_key}={min_price}%7C{max_price}%7C1")
    elif min_price and not max_price:
        query_parts.append(f"{price_key}={min_price}%7C2000000000%7C1")
    elif max_price and not min_price:
        query_parts.append(f"{price_key}=0%7C{max_price}%7C1")

    # Build final URL
    if query_parts:
        return f"{base_url}?{'&'.join(query_parts)}&sort=0"
    else:
        return base_url




# --------------------- TEST THE QUERY TO url ----------------------------------------------

# test_query = "i want to buy a property"
# paras = parse_query_with_gemini(test_query)
# print('------------PARSED PARAMS FROM GEMINI LLM---------------')
# print(paras)
# print('-----------------------------------spliter 1 --------------------------')
# my_url = build_prop_search_url(paras)
# print('-----------------------------------spliter 2 --------------------------')
# print(my_url)


# test_queries = [
#     "show me villa in dubai for sale 4 5 beds min price 5m and max price is 10m ",
#     "show me villa in dubai for rent 4 5 beds min price is 5m and max price is 10m "
# ]




# for q in test_queries:
#     print("\nQuery:", q)
#     params = parse_query_with_gemini(q)
#     print("Parsed:", params)
#     url = build_prop_search_url(params)
#     print("URL:  ", url)