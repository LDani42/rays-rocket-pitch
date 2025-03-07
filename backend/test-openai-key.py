import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment variables or .env file")
    exit(1)

print(f"Found API key: {api_key[:5]}...{api_key[-4:]}")

# Initialize the client
client = OpenAI(api_key=api_key)

try:
    # Make a simple API call with minimal tokens
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one word."}
        ],
        max_tokens=10,
        temperature=0.7
    )
    
    # Get the response content
    message_content = response.choices[0].message.content
    
    print("\nAPI TEST SUCCESSFUL!")
    print(f"Response: {message_content}")
    print("Your OpenAI API key is working correctly.")
    
except Exception as e:
    print("\nAPI TEST FAILED!")
    print(f"Error: {str(e)}")
    
    if "insufficient_quota" in str(e):
        print("\nYour account has run out of credits. You need to:")
        print("1. Visit https://platform.openai.com/account/billing")
        print("2. Add a payment method or purchase more credits")
        print("3. Check for any usage limits on your account")
    elif "invalid_api_key" in str(e) or "invalid" in str(e):
        print("\nYour API key appears to be invalid. You need to:")
        print("1. Visit https://platform.openai.com/api-keys")
        print("2. Create a new API key")
        print("3. Update your .env file with the new key")
    elif "rate limit" in str(e).lower():
        print("\nYou've hit a rate limit. You need to:")
        print("1. Wait a while before trying again")
        print("2. Consider upgrading your OpenAI plan for higher rate limits")
