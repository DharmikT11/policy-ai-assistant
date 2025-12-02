import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
# If .env isn't working, uncomment the line below and paste your key temporarily (Delete after!)
# api_key = "PASTE_YOUR_KEY_HERE" 

if not api_key:
    print("❌ Error: No API Key found.")
else:
    print(f"✅ Key found: {api_key[:5]}...")
    genai.configure(api_key=api_key)

    print("\n🔍 Listing available models for this key:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")