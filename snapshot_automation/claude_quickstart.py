import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("ANTHROPIC_API_KEY")

# Print the loaded API key for verification
print(f"Loaded API Key: {api_key}")

# Ensure the API key is available
if not api_key:
	raise ValueError("ANTHROPIC_API_KEY not found in .env file")

# Initialize the Anthropic client with the loaded API key
client = Anthropic(api_key=api_key)

# Example usage
def get_response(prompt):
	message = client.messages.create(
		model="claude-3-5-sonnet-20240620",
		max_tokens=1000,
		messages=[
			{"role": "user", "content": prompt}
		]
	)
	return message.content

# Test the function
user_prompt = "What are three interesting facts about Python programming?"
response = get_response(user_prompt)
print(response)