import google.generativeai as genai
from dotenv import load_dotenv
import json
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")



#------------------------FUNCTIONS   USER QUERY TO PARAMS------------------------------------------
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

#------------------------FUNCTION PARAMS TO URL---------------------------------------------------

def build_propertyfinder_url(params):
    purpose = params.get("purpose_property", "").lower()
    property_type = params.get("property_type", "").lower()
    bedrooms_input = params.get("bedrooms", "")
    baths_input = params.get("baths", "")
    min_price = params.get("min_price", "")
    max_price = params.get("max_price", "")

    buy_terms = ["buy", "sale", "for sale", "available", "purchase"]
    rent_terms = ["rent", "for rent", "rental", "leasing", "to rent"]

    type_map = {
        "apartment": "1",
        "villa": "35",
        "townhouse": "22",
        "penthouse": "20",
        "compound": "42",
        "duplex": "24",
        "full floor": "18",
        "half floor": "29",
        "whole building": "10",
        "bulk rent unit": "34",
        "bungalow": "31",
        "hotel and hotel apartment": "45"
    }

    bed_map = {
        "studio": "0",
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "7+": "7&bdr[]=8"
    }

    bath_map = {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "7+": "8"
    }

    if any(term in purpose for term in buy_terms):
        t_value = type_map.get(property_type, "1")
        t_param = f"&t={t_value}" if t_value else ""

        bdr_params = []
        if bedrooms_input:
            beds_list = [b.strip() for b in bedrooms_input] if isinstance(bedrooms_input, list) else [b.strip() for b in bedrooms_input.split(",")]
            for b in beds_list:
                if b in bed_map:
                    val = bed_map[b]
                    if "8" in val:
                        bdr_params.append("bdr[]=7")
                        bdr_params.append("bdr[]=8")
                    else:
                        bdr_params.append(f"bdr[]={val}")
        bdr_string = "&".join(bdr_params) if bdr_params else ""

        btr_params = []
        if baths_input:
            baths_list = [b.strip() for b in baths_input] if isinstance(baths_input, list) else [b.strip() for b in baths_input.split(",")]
            for b in baths_list:
                if b in bath_map:
                    btr_params.append(f"btr[]={bath_map[b]}")
        btr_string = "&".join(btr_params) if btr_params else ""

        price_parts = []
        if min_price: price_parts.append(f"pf={min_price}")
        if max_price: price_parts.append(f"pt={max_price}")
        price_string = "&".join(price_parts)

        return f"https://www.propertyfinder.ae/en/search?l=1&c=1{t_param}{('&' + bdr_string) if bdr_string else ''}{('&' + btr_string) if btr_string else ''}{('&' + price_string) if price_string else ''}&fu=0&ob=mr"

    elif any(term in purpose for term in rent_terms):
        t_value = type_map.get(property_type, "")
        t_param = f"&t={t_value}" if t_value else ""

        bdr_params = []
        if bedrooms_input:
            beds_list = [b.strip() for b in bedrooms_input] if isinstance(bedrooms_input, list) else [b.strip() for b in bedrooms_input.split(",")]
            for b in beds_list:
                if b in bed_map:
                    val = bed_map[b]
                    if "8" in val:
                        bdr_params.append("bdr[]=7")
                        bdr_params.append("bdr[]=8")
                    else:
                        bdr_params.append(f"bdr[]={val}")
        bdr_string = "&".join(bdr_params) if bdr_params else ""

        btr_params = []
        if baths_input:
            baths_list = [b.strip() for b in baths_input] if isinstance(baths_input, list) else [b.strip() for b in baths_input.split(",")]
            for b in baths_list:
                if b in bath_map:
                    btr_params.append(f"btr[]={bath_map[b]}")
        btr_string = "&".join(btr_params) if btr_params else ""

        price_parts = []
        if min_price: price_parts.append(f"pf={min_price}")
        if max_price: price_parts.append(f"pt={max_price}")
        price_string = "&".join(price_parts)

        return f"https://www.propertyfinder.ae/en/search?l=1&c=2{t_param}{('&' + bdr_string) if bdr_string else ''}{('&' + btr_string) if btr_string else ''}{('&' + price_string) if price_string else ''}&fu=0&rp=y&ob=mr"

    else:
        return "https://www.propertyfinder.ae/en/search?l=1&c=2&fu=0&rp=y&ob=mr"


# --------------------- TEST THE QUERY TO url ----------------------------------------------

# query = "Buy a 7+ bed whole building in Dubai, minimum 10M AED"
# paras = parse_query_with_gemini(query)
# print('------------Started---------------')
# print(paras)
# print('-----------------------------------spliter 1 --------------------------')
# my_url = build_propertyfinder_url(paras)
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
