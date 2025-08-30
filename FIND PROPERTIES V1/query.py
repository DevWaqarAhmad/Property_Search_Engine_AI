import google.generativeai as genai
from dotenv import load_dotenv
import os

# ------------------------- API KEY LOADED ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

#-----------------FUNCTION OF CREATE URLS--------------------------
def generate_find_properties_url(user_query):

#---------------TEST IN TERMINAL----------------------------------------

user_query = "8 bedroom villa with 6 baths for sale price range 65000 to 100000"
print("Query:", user_query)
url = generate_bayut_url(user_query)
print("Generated URL:", url)




