import json
import faiss
import numpy as np
import google.generativeai as genai
import streamlit as st


# Paths to the files
INDEX_FILE = 'faiss_chunks.index'
METADATA_FILE = 'metadata.json'

# Number of top results to retrieve
TOP_K = 20

# Model name for Google Generative AI
MODEL_NAME = 'models/gemini-2.0-flash'

# Set up the API key for Google Generative AI
api_key = st.secrets['GEMINI_API_KEY']
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

    # Count the number of distances in each range
    bins = np.arange(0, 1, 0.1)  # Create bins for the range 0-1 with step 0.1
    histogram, _ = np.histogram(distances, bins=bins)

    # Print the counts for each range
    for i in range(len(histogram)):
        print(f"Range {bins[i]:.1f}-{bins[i+1]:.1f}: {histogram[i]}")
    
    return results


# -------------------
# Generate a summary from the top results using Gemini
# -------------------
def generate_summary(query, top_chunks):
    print('Generating response...')

    # Join the text of the top chunks to create a context for summarization
    context = '\n\n'.join([chunk['text'] for chunk in top_chunks])

    # Initialize the Google Generative AI model
    model = genai.GenerativeModel(model_name=MODEL_NAME)

    # Define the prompt for summarization
    init_prompt = (
        '''
        # Instructions to respond to the query
        You are a helpful assistant that provides answers based on the context provided.
        You will be given a query and a context.
        Respond to the query in the clearest way possible.
        Use the context that is relevant to the query.
        Provide some additional informatin in the response, if relevant.
        Do not change the terminology or keywords used in the document.
        The response must be coherent and sensible.
        Structure the response into subheaders and paragraphs.
        Do not add a header. Subheaders must be short and relevant to the content.
        Use bullet points, lists and tables where appropriate.

        # Handling edge cases
        If the answer is not in the context, say "The answer is not in the context".
        Do not make up answers.
        Tell them a concise description of the information that is in the context.

        # Suggestions for improving the query
        Start the paragraph with "*Tip:*" and write the entire suggestion in italics.
        Always add a suggestion ways to improve the query so that it is more clear and specific.
        '''
        f'\n\Query:\n{query}'
        f'\n\nContext:\n{context}'
    )

    # Generate the summary using Google Generative AI
    init_response = model.generate_content(init_prompt)

    return init_response.text


# -------------------
# Main function to test the flow
# -------------------
def main(index_path=INDEX_FILE, metadata_path=METADATA_FILE, top_k=TOP_K):
    # Load the FAISS index and metadata
    index, metadata = load_assets(index_path, metadata_path)

    # Prompt the user for a search query
    query = input('Enter your search query: ')

    # Perform semantic search to find the top k chunks
    top_chunks = semantic_search(query, index, metadata, top_k)

    # Summarize the top chunks
    summary = generate_summary(query, top_chunks)

    print('\n🔎 Query Response:')
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