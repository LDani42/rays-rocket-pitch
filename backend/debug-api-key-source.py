import os
import sys
from dotenv import load_dotenv, find_dotenv

# Check if OPENAI_API_KEY is set before loading .env
print("Environment variables before loading .env:")
env_key = os.environ.get("OPENAI_API_KEY")
if env_key:
    print(f"OPENAI_API_KEY from environment: {env_key[:5]}...{env_key[-4:]}")
else:
    print("OPENAI_API_KEY not found in environment variables")

# Find and load the .env file
env_path = find_dotenv(usecwd=True)
if env_path:
    print(f"\nFound .env file at: {env_path}")
    # Read the .env file content directly
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Look for OPENAI_API_KEY in the file content
    import re
    api_key_match = re.search(r'OPENAI_API_KEY\s*=\s*([^\n]+)', env_content)
    if api_key_match:
        dotenv_key = api_key_match.group(1).strip('"\'')
        print(f"OPENAI_API_KEY from .env file: {dotenv_key[:5]}...{dotenv_key[-4:]}")
    else:
        print("OPENAI_API_KEY not found in .env file content")
        
    # Now load the .env file
    load_dotenv(env_path)
else:
    print("\nNo .env file found")
    load_dotenv()  # Try to load from default location anyway

# Check if OPENAI_API_KEY is set after loading .env
print("\nEnvironment variables after loading .env:")
env_key = os.environ.get("OPENAI_API_KEY")
if env_key:
    print(f"OPENAI_API_KEY: {env_key[:5]}...{env_key[-4:]}")
else:
    print("OPENAI_API_KEY not found in environment variables")

print("\nPython path:")
for path in sys.path:
    print(path)
