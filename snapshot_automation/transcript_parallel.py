import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_voyageai import VoyageAIEmbeddings
from anthropic import Anthropic

from dotenv import load_dotenv

load_dotenv()

voyage_api_key = os.getenv("VOYAGEAI_API_KEY")

# Get the API key from the environment variable
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Verify API key is loaded (without exposing it)
if anthropic_api_key:
    print("Anthropic API key loaded successfully")
else:
    print("Warning: Anthropic API key not found")

# Ensure the API key is available
if not anthropic_api_key:
	raise ValueError("ANTHROPIC_API_KEY not found in .env file")

# Initialize the Anthropic client with the loaded API key
client = Anthropic(api_key=anthropic_api_key)

# Helper functions for printing docs

def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n\n".join(
        [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )

# Use an absolute path
file_path = os.path.join(os.path.dirname(__file__), "vtt_files/plain_text_output.txt")

# Instantiate the TextLoader and load the documents
text_loader = TextLoader(file_path)
documents = text_loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

retriever = FAISS.from_documents(
    texts, VoyageAIEmbeddings(voyage_api_key=voyage_api_key, model="voyage-law-2")
).as_retriever(search_kwargs={"k":5})

background_prompt = "Your task is to describe the Customer's initial problem or challenge before using Qlik's products and services. This description will set the stage for the narrative."
solution_prompt = "Detail the specific product/service from Qlik/Talend that was implemented. Explain how it was introduced and applied to the customer's problem."


relevant_docs = retriever.invoke(solution_prompt)
#pretty_print_docs(relevant_docs)

# # Example Message
# message = client.messages.create(
#     model="claude-3-5-sonnet-20240620",
#     max_tokens=2000,
#     temperature=0,
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Your task is to analyze the following report:  \n<report>  \n[Full text of [Matterport SEC filing 10-K 2023](https://investors.matterport.com/node/9501/html), not pasted here for brevity]  \n</report>  \n  \nSummarize this annual report in a concise and clear manner, and identify key market trends and takeaways. Output your findings as a short memo I can send to my team. The goal of the memo is to ensure my team stays up to date on how financial institutions are faring and qualitatively forecast and identify whether there are any operating and revenue risks to be expected in the coming quarter. Make sure to include all relevant details in your summary and analysis."
#                 }
#             ]
#         }
#     ]
# )
# print(message.content)


# Example usage for Jack
def get_response(prompt):
	message = client.messages.create(
		model="claude-3-5-sonnet-20240620",
		max_tokens=1000,
		messages=[
			{"role": "user", "content": prompt}
		]
	)
	return message.content

# Combine the query and the relevant document contents
combined_input = (
    "Here are some documents that might help answer the question: "
    + solution_prompt
    + "\n\nRelevant Documents:\n"
    + "\n\n".join([doc.page_content for doc in relevant_docs])
	+ "\n\nPlease provide an answer based ONLY on the provided documents. If the answer is not found in the documents, respond with 'I'm not sure'."
    
)

print(combined_input)
# Test the function
response = get_response(combined_input)
print(response)