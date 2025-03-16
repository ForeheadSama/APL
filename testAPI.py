from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load environment variables from .env file
load_dotenv()

# Access an environment variable
api_key = os.getenv("GEMINI_API_KEY")

# Print the value (for testing)
print("API Key:", api_key)

# Use the model
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("List all concerts being held on March 17, 2025 in New York City.")
print(response.text)