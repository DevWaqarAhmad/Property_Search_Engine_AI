from dotenv import load_dotenv
import os
import google.generativeai as genai
from llm import chatbot_property_search 

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")


def is_property_query(user_input):
    """
    Enhanced detection for property-related queries.
    
    Args:
        user_input (str): User's input message
        
    Returns:
        bool: True if it's a property query, False otherwise
    """
    user_input_lower = user_input.lower()
    property_keywords = [
        'rent', 'rental', 'renting', 'lease',
        'buy', 'buying', 'purchase', 'sale', 'sell',
        'apartment', 'flat', 'studio', 'villa', 'house', 'townhouse', 'penthouse',
        'property', 'properties', 'real estate',
        'bedroom', 'br', '1br', '2br', '3br', '4br', '5br',
        'bathroom', 'bath', 'washroom',
        'dubai', 'abu dhabi', 'sharjah', 'ajman',
        'marina', 'downtown', 'jvc', 'jlt', 'business bay', 'deira'
    ]
    
    location_phrases = [
        'in dubai', 'in abu dhabi', 'in sharjah', 'in ajman',
        'near marina', 'in marina', 'at marina',
        'downtown area', 'business bay area',
        'jumeirah village', 'jumeirah lake towers'
    ]
    
 
    action_phrases = [
        'looking for', 'searching for', 'find me', 'show me',
        'i want to', 'i need', 'help me find',
        'available properties', 'property search'
    ]
    

    has_property_keyword = any(keyword in user_input_lower for keyword in property_keywords)
    has_location_phrase = any(phrase in user_input_lower for phrase in location_phrases)
    has_action_phrase = any(phrase in user_input_lower for phrase in action_phrases)
    
    return has_property_keyword or (has_location_phrase and has_action_phrase)


def chatbot_response(user_input):
    """
    Main chatbot response function that routes queries appropriately.
    
    Args:
        user_input (str): User's input message
        
    Returns:
        str: Formatted response
    """
    try:
        # Enhanced property query detection
        if is_property_query(user_input):
            print("🔍 Detected property query - searching Bayut...")
            
            # Call the enhanced bayut scraper
            scraped_result = chatbot_property_search(user_input)

            print(f'[DEBUG] scraped_result:  {scraped_result}]')
            
            # Check if it's an error message or actual results
            if scraped_result.startswith("❌"):
                return scraped_result + "\n\n💡 Try rephrasing your query with more specific details like location, property type, or price range."
            else:
                return scraped_result + "\n\n💬 Need help refining your search? Just ask!"

        # Otherwise, use Gemini for general conversation with custom personality
        print("💭 General query - using Gemini AI...")
        
        # Add context to make it respond as Property Search engine
        context = """You are a Property Search Engine AI assistant specializing in UAE real estate. 
        When asked about your identity, respond that you are a Property Search Engine UAE Based.
        For non-property questions, provide helpful answers while maintaining your real estate expertise identity.
        Keep responses friendly and professional."""
        
        enhanced_prompt = f"{context}\n\nUser question: {user_input}"
        print('response----------------------------------------------------')
        response = model.generate_content(enhanced_prompt)

        print('Response:', response.text)
        return response.text

    except Exception as e:
        return f"❌ Error: {str(e)}\n\n💡 Please try again or rephrase your question."


def display_welcome_message():
    """Display welcome message with usage examples."""
    print("="*60)
    print("🏠 PROPERTY SEARCH ENGINE")
    print()
    print("Type 'exit' to quit, 'help' for more examples")
    print("-"*60)


def display_help():
    """Display help message with more examples."""
    print("\n" + "="*50)
    print("🆘 HELP - HOW TO SEARCH FOR PROPERTIES")
    print("="*50)
    print("Format: [Purpose] + [Property Type] + [Location] + [Details]")
    print()
    print("🏠 Property Types: apartment, villa, townhouse, studio, penthouse")
    print("📍 Popular Areas: Marina, JVC, Downtown, JLT, Business Bay, Deira")
    print("💰 Price Examples: 'under 100k', '80k-120k', 'max 90000'")
    print("🛏️  Bedrooms: '2BR', '3 bedroom', 'studio'")
    print()
    print("✅ Good Examples:")
    print("   • 'Rent 2BR apartment Marina under 90k'")
    print("   • 'Buy villa Arabian Ranches 3 bedroom'")
    print("   • 'Studio for rent in JVC max 50000'")
    print("   • 'Show me apartments in Downtown Dubai'")
    print()
    print("❌ Less effective:")
    print("   • 'Property' (too vague)")
    print("   • 'Something cheap' (no location/type)")
    print("-"*50 + "\n")


user_in = "i waant property in satwa"

print('test start - ------------------')
pr = chatbot_response(user_in)
print('pr:', pr)
print('test end - ------------------')

# if __name__ == "__main__":
#     display_welcome_message()
#
#     while True:
#         query = input("\n💬 You: ")
#
#         if query.lower() in ["exit", "quit", "bye"]:
#             print("\n👋 Chatbot: Thank you for using Property Search Chatbot! Goodbye!")
#             break
#         elif query.lower() in ["help", "examples", "how"]:
#             display_help()
#             continue
#         elif query.strip() == "":
#             print("🤔 Chatbot: Please enter a message!")
#             continue
#
#         print("🤖 Chatbot: ", end="", flush=True)
#         answer = chatbot_response(query)
#         print(answer)