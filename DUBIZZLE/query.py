import google.generativeai as genai
from dotenv import load_dotenv
import json
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

#--------------------------- FUNCTION QUERY TO PARAMS------------------------------

def parse_query_with_gemini(user_query):
    # --- Allowed parameters ---
    ALLOWED_PARAMS = {
        "purpose_property": ['rent', 'sale'],
        "property_type": ['apartment', 'townhouse', 'compound', 'duplex',
                                      'full floor', 'villa', 'penthouse', 'half floor', 'whole building',
                                      'warehouses', 'commercial-villas', 'commercial-plots', 'commercial-buildings',
                                      'industrial-land', 'showrooms', 'shops', 'labour-camps', 'bulk-units',
                                      'bulk rent unit', 'bungalow', 'hotel and hotel apartment', 'commerical-properties'
                                      ],
        "bedrooms": ['studio', '1', '2', '3', '4', '5', '6', '7', '7+'],
        "baths": ['1', '2', '3', '4', '5', '7','7+']
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




#------------------------FUNCTIONS   USER QUERY TO PARAMS------------------------------------------

def build_dubbizle_url(params):
    # --- Purpose ---
    if params.get('purpose_property') == 'rent':
        base_url = "https://sharjah.dubizzle.com/en/property-for-rent/"
    else:
        base_url = "https://sharjah.dubizzle.com/en/property-for-sale/"

    # --- Property type mapping ---
    residential_map = {
        "apartment": "residential/apartmentflat",
        "townhouse": "residential/townhouse",
        "penthouse": "residential/penthouse",
        "hotel and hotel apartment": "residential/hotel-apartment",
        "compound": "residential/villa-compound",
        "full floor": "residential/residential-floor",
        "half floor": "residential/residential-floor",
        "duplex": "residential/apartmentflat",
        "whole building": "residential/residential-building",
        "bungalow": "residential/villahouse",
    }

    commercial_map = {
        "warehouses": "commercial/warehouse",
        "commercial-villas": "commercial/commercial-villa",
        "commercial-plots": "commercial/commercial-land",
        "commercial-buildings": "commercial/commercial-building",
        "industrial-land": "commercial/industrial",
        "showrooms": "commercial/showroom",
        "shops": "commercial/shop",
        "labour-camps": "commercial/staff-accomm",
        "bulk-units": "commercial/other",
        "bulk rent unit": "commercial/other",
        "commerical-properties": "commercial/office",
    }

    property_type = params.get("property_type", "").lower()

    # --- Build final URL based on property type ---
    if property_type == "villa":
        final_url = base_url + "residential/villahouse/"
    elif property_type == "commercial-villas":
        final_url = base_url + "commercial/commercial-villa/"
    elif property_type in residential_map:
        final_url = base_url + residential_map[property_type] + "/"
    elif property_type in commercial_map:
        final_url = base_url + commercial_map[property_type] + "/"
    else:
        # Default fallback
        final_url = base_url + "residential/"
    
    # --- Add price filters ---
    url_params = []
    min_price = params.get('min_price')
    max_price = params.get('max_price')
    
    if min_price or max_price:
        if min_price and max_price:
            # Both min and max price provided
            url_params.append(f"price__gte={min_price}")
            url_params.append(f"price__lte={max_price}")
        elif min_price and not max_price:
            # Only min price, set very high max price
            url_params.append(f"price__gte={min_price}")
            url_params.append(f"price__lte=10000000000")
        elif max_price and not min_price:
            # Only max price, set min to 0
            url_params.append(f"price__gte=0")
            url_params.append(f"price__lte={max_price}")
    
    # --- Add bathroom filters ---
    baths = params.get('baths')
    if baths:
        if isinstance(baths, list):
            # Multiple bathroom values
            for bath in baths:
                url_params.append(f"bathrooms={bath}")
        else:
            # Single bathroom value
            url_params.append(f"bathrooms={baths}")
    
    # --- Add bedroom filters ---
    bedrooms = params.get('bedrooms')
    if bedrooms:
        if isinstance(bedrooms, list):
            # Multiple bedroom values
            for bedroom in bedrooms:
                url_params.append(f"bedrooms={bedroom}")
        else:
            # Single bedroom value
            url_params.append(f"bedrooms={bedrooms}")
    
    # Add all parameters to URL if any exist
    if url_params:
        final_url += "?" + "&".join(url_params)
    
    return final_url


#----------------------------------------

# query = "for rent shop in dubai"
# paras = parse_query_with_gemini(query)
# print('------------Started---------------')
# print(paras)
# print('-----------------------------------spliter 1 --------------------------')
# my_url = build_url(paras)
# print('-----------------------------------spliter 2 --------------------------')
# print(my_url)
#https://findproperties.ae/for-rent/4-bedroom-villa/uae


test_queries = [
    "looking for rent apartment in dubai with 3 baths and 2 bedrooms price maximum is 300,000",
    "i want villa for rent in sharjah with 2 5 bedrooms and 4 5 baths price is 100,000 to 500,000",
    "rent penthouse have 2 5 bedrooms and 4 baths price minimum is 400,000",
    "i want a commercial villa with 4 5 bedrooms and 3 4 bathrooms and price minimum is 500,000"
]




for q in test_queries:
    print("\nQuery:", q)
    params = parse_query_with_gemini(q)
    print("Parsed:", params)
    url = build_dubbizle_url(params)
    print("URL:  ", url)