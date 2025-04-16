import streamlit as st
import json
import os
import faiss
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

# Import the functions from 3_query.py
from _3_query import semantic_search, generate_summary, load_assets


# Set the paths for the FAISS index and metadata file
INDEX_FILE = 'faiss_chunks.index'
METADATA_FILE = 'metadata.json'

# Number of top results to retrieve
TOP_K = 5


# Load environment variables
load_dotenv()

# Set up the API key for Google Generative AI
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)


# -------------------
# Streamlit UI
# -------------------
def display_ui():
    st.title("Document Retrieval & Summarization")
    
    # Upload or specify file paths for index and metadata (optional)
    st.sidebar.header("File Paths")
    index_file = st.sidebar.text_input("FAISS Index File Path", INDEX_FILE)
    metadata_file = st.sidebar.text_input("Metadata File Path", METADATA_FILE)
    
    # Input box for search query
    query = st.text_input("Enter your query:", "")

    # When the user presses the "Search" button
    if st.button("Search"):
        if query:
            # Load the FAISS index and metadata
            index, metadata = load_assets(index_file, metadata_file)

            # Perform semantic search on the query
            top_chunks = semantic_search(query, index, metadata, TOP_K)

            # Generate a summary based on the top chunks
            summary = generate_summary(query, top_chunks)

            # Display the summary and relevant articles
            st.subheader("Summary:")
            st.write(summary)

            st.subheader("Relevant Articles:")
            for chunk in top_chunks:
                st.markdown(f"- [{chunk['title']}]({chunk['url']})")
        else:
            st.warning("Please enter a query to search.")


# -------------------
# Main execution
# -------------------
if __name__ == "__main__":
    display_ui()
