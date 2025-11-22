import os

from anthropic import Anthropic
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("ANTHROPIC_API_KEY")

# Verify API key is loaded (without exposing it)
if api_key:
    print("API key loaded successfully")
else:
    print("Warning: API key not found")

# Ensure the API key is available
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

# Initialize the Anthropic client with the loaded API key
client = Anthropic(api_key=api_key)


# Example usage
def get_response(prompt):
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content


# Test the function
user_prompt = "What are three interesting facts about Python programming?"
response = get_response(user_prompt)
print(response)
