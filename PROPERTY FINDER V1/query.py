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
#------------------------FUNCTION PARAMS TO URL---------------------------------------------------
def build_property_finder_url(params):
# --------------------- TEST THE QUERY TO url ----------------------------------------------

test_query = "i want a villa in sharjah with 4 bedrooms"
paras = parse_query_with_gemini(test_query)
print('------------Started---------------')
print(paras)
print('-----------------------------------spliter 1 --------------------------')
my_url = build_property_finder_url(paras)
print('-----------------------------------spliter 2 --------------------------')
print(my_url)
https://findproperties.ae/for-rent/4-bedroom-villa/uae


test_queries = [
    "I want a 3 bedroom apartment for rent in Dubai",
    "Looking for a villa for sale in Abu Dhabi",
    "Need a studio apartment for sharing in Sharjah",
    "Find me a 4 bedroom villa for rent in UAE",
    "I need a shop for rent in Dubai",
    "Looking for a penthouse for sale in Dubai Marina",
    "Want a warehouse for rent in industrial area",
    "Find a 2 bedroom townhouse for rent",
    "Looking for a labour camp for rent in Abu Dhabi",
    "Need a hotel apartment for short stay in Dubai"
]

for q in test_queries:
    print("\nQuery:", q)
    params = parse_query_with_gemini(q)
    print("Parsed:", params)
    url = build_find_properties_url(params)
    print("URL:  ", url)