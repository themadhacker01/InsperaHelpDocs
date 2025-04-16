import json
import os
import faiss
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai


# Paths to the files
INDEX_FILE = 'faiss_chunks.index'
METADATA_FILE = 'metadata.json'
# Number of top results to retrieve
TOP_K = 5

# Load environment variables from .env
load_dotenv()

# Set up the API key for Google Generative AI
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)


# -------------------
# Loads the FAISS index and metadata from the specified paths
# -------------------
def load_assets(index_path, metadata_path):
    print('Loading assets...')
    
    # Read the FAISS index from the specified path
    index = faiss.read_index(index_path)

    # Read the metadata from the specified JSON file
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    return index, metadata


# -------------------
# Embed the user query and run semantic search on FAISS
# -------------------
def semantic_search(query, index, metadata, k):
    print('Performing semantic search...')

    # Embed the query using Google Generative AI
    response = genai.embed_content(
        model='models/embedding-001',
        content=query,
        task_type='retrieval_query'
    )
    # Extract the embedding from the response and reshape it for FAISS
    query_embedding = np.array(response['embedding']).astype('float32').reshape(1, -1)

    # Perform the search on the FAISS index
    # Search for the top k nearest neighbors
    distances, indices = index.search(query_embedding, k)
    results = [metadata[i] for i in indices[0]]

    return results


# -------------------
# Generate a summary from the top results using Gemini
# -------------------
def generate_summary(chunks):
    print('Generating summary...')

    # Join the text of the top chunks to create a context for summarization
    context = '\n\n'.join([chunk['text'] for chunk in chunks])

    # Define the prompt for summarization
    prompt = (
        '''
        Use the following content to respond to the prompt concisely and clearly.
        Ignore content that is not relevant to the prompt.
        The response must be coherent and easy to read.
        If you do not know the answer, say "I don't know".
        If the answer is not in the content, say "The answer is not in the content".
        Do not make up answers or provide information that is not in the content.
        Do not include any disclaimers or unnecessary information.
        '''
        f'\n\n{context}'
    )

    # Generate the summary using Google Generative AI
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-002")
    response = model.generate_content(prompt)
    return response.text


# -------------------
# Main function to test the flow
# -------------------
def main():
    # Load the FAISS index and metadata
    index, metadata = load_assets(index_path=INDEX_FILE, metadata_path=METADATA_FILE)

    # Prompt the user for a search query
    query = input('Enter your search query: ')

    # Perform semantic search to find the top k chunks
    top_chunks = semantic_search(query, index, metadata, TOP_K)

    # Summarize the top chunks
    summary = generate_summary(top_chunks)

    print('\n🔎 Summary:')
    print(summary)

    print('\n📄 Relevant Articles:')
    # Display the titles and URLs of the top chunks
    for chunk in top_chunks:
        print(f'- {chunk["title"]}: {chunk["url"]}')


# -------------------
# Executing the code using the main function
# -------------------
if __name__ == '__main__':
    main()