import streamlit as st
import json
import google.generativeai as genai

# Import the functions from _3_query.py
from _3_query import semantic_search, generate_summary, load_assets


# Set the paths for the FAISS index and metadata file
INDEX_FILE = 'faiss_chunks.index'
METADATA_FILE = 'metadata.json'

# Number of top results to retrieve
TOP_K = 5

# Set up the API key for Google Generative AI
api_key = st.secrets['GEMINI_API_KEY']
genai.configure(api_key=api_key)


# -------------------
# Streamlit UI
# -------------------
def display_ui(index_file=INDEX_FILE, metadata_file=METADATA_FILE):
    # Set the title of the Streamlit app
    st.header('Inspera Support AI')

    # Sidebar for information about the application
    st.sidebar.header('Have a question?')
    st.sidebar.subheader('Simply enter your query and we will answer it for you.')
    st.sidebar.write(
        '''
        This application allows you to respond to your query about the Inspera platform.
        It strictly adheres to Help Center articles and does not include any other information.

        Right now, it is only available in English and only searches on text content.
        But we are working on adding more languages and searching on images and videos as well.

        Stay tuned for more updates!
        '''
    )
    
    # Input box for search query
    query = st.text_input('', placeholder='Type your question here...')

    # When the user presses the 'Search' button
    if st.button('Search'):
        if query:
            # Load the FAISS index and metadata
            index, metadata = load_assets(index_file, metadata_file)

            # Perform semantic search on the query
            top_chunks = semantic_search(query, index, metadata, TOP_K)

            # Generate a summary based on the top chunks
            summary = generate_summary(query, top_chunks)

            # Display the summary and relevant articles
            st.subheader('Summary:')
            st.write(summary)

            st.subheader('Relevant Articles:')
            for chunk in top_chunks:
                st.markdown(f'- [{chunk["title"]}]({chunk["url"]})')
        else:
            st.warning('Please enter a query to search.')


# -------------------
# Main execution
# -------------------
if __name__ == '__main__':
    display_ui()
