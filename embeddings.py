import json, os, faiss
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai


# Set the path to the JSON file containing the chunks
CHUNKS_FILE = 'chunks.json'

# Load environment variables from .env
load_dotenv()

# Set up the API key for Google Generative AI
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)


# Generate embeddings for the chunks using Google Generative AI
def generate_embeddings(chunks):    
    print('Generating embeddings for chunks...')

    # Initialize an empty list to store the embedded chunks
    embedded_chunks = []

    # Loop through each chunk and generate its embedding
    for chunk in chunks:
        # Generate the embedding for the chunk using the Google GenAI API
        response = genai.embed_content(
            model='models/embedding-001',
            content=chunk['text'],
            task_type='retrieval_document'
        )
        # Append the chunk with its embedding to the list
        embedded_chunks.append({
            'chunk_id': chunk['chunk_id'],
            'article_id': chunk['article_id'],
            'title': chunk['title'],
            'url': chunk['url'],
            'text': chunk['text'],
            'embedding': response['embedding']
        })
    
    # Return the list of embedded chunks
    print(f'✅ Embeddings created and stored for {len(embedded_chunks)} chunks.')
    return embedded_chunks


# Call the main function to execute the script
def main():
    # Load the chunks from the JSON file
    print('Loading chunks from JSON file...')
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Generate embeddings for the chunks
    embedded_chunks = generate_embeddings(chunks)
    print(embedded_chunks[0])

if __name__ == '__main__':
    main()