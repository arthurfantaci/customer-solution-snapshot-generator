"""RAG-based transcript Q&A system using FAISS, VoyageAI embeddings, and Claude.

This module implements a Retrieval-Augmented Generation (RAG) system for
answering questions about meeting transcripts. It combines:
- FAISS vector database for efficient similarity search
- VoyageAI embeddings (voyage-law-2 model) for semantic text representation
- Anthropic Claude (claude-sonnet-4-5) for natural language generation
- LangChain for document loading, text splitting, and retrieval

The system loads transcript text, splits it into chunks, creates vector embeddings,
and uses semantic search to retrieve relevant context for answering questions.
"""

import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_voyageai import VoyageAIEmbeddings


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


def pretty_print_docs(docs: list[Any]) -> None:
    """Pretty print a list of LangChain document objects.

    Formats and displays retrieved documents with separators and numbering
    for easy reading and debugging of RAG retrieval results.

    Args:
        docs: List of LangChain Document objects with page_content attributes.

    Example:
        >>> docs = retriever.invoke("What was discussed?")
        >>> pretty_print_docs(docs)
        Document 1:

        [content of first document]

        ------------------------------------...

        Document 2:

        [content of second document]
    """
    print(
        f"\n{'-' * 100}\n\n".join(
            [f"Document {i + 1}:\n\n" + d.page_content for i, d in enumerate(docs)]
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
).as_retriever(search_kwargs={"k": 5})

background_prompt = "Your task is to describe the Customer's initial problem or challenge before using Quiznos Analytics's products and services. This description will set the stage for the narrative."
solution_prompt = "Detail the specific product/service from Quiznos Analytics/Talenti Data Works that was implemented. Explain how it was introduced and applied to the customer's problem."


relevant_docs = retriever.invoke(solution_prompt)
# pretty_print_docs(relevant_docs)

# # Example Message
# message = client.messages.create(
#     model="claude-sonnet-4-5-20250929",
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
def get_response(prompt: str) -> list[Any]:
    """Get a response from Claude AI based on the provided prompt.

    Sends a prompt to Claude API and returns the generated response content.
    Uses claude-sonnet-4-5-20250929 model with a 1000 token limit.

    Args:
        prompt: The input prompt/question to send to Claude. Should include
            both the query and any relevant context documents for RAG.

    Returns:
        List of content blocks from Claude's response. Typically contains
        text blocks with the generated answer.

    Raises:
        anthropic.APIError: If the API request fails.
        anthropic.AuthenticationError: If API key is invalid.

    Example:
        >>> prompt = "What is the customer's main challenge?"
        >>> response = get_response(prompt)
        >>> print(response)
        [TextBlock(text='The main challenge was...', type='text')]
    """
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content  # type: ignore[no-any-return]


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
