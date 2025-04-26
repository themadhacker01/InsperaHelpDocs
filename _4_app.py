import streamlit as st
import json
import google.generativeai as genai

# Import the functions from _3_query.py
from _3_query import semantic_search, generate_summary, load_assets


# Set the paths for the FAISS index and metadata file
INDEX_FILE = 'faiss_chunks.index'
METADATA_FILE = 'metadata.json'

# Number of top results to retrieve
DEFAULT_TOP_K = 20
DEFAULT_PERSONA = 'Employee'
DEFAULT_STYLE = 'Formal'

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
    query = st.text_area('Text area to input query', placeholder='Type your question here...', label_visibility='collapsed', height=72)

    # Create a horizontal layout for the search button and dropdowns
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        # Persona dropdown
        persona = st.selectbox('Persona',
            [
                'Product Manager', 
                'Sales Person',
                'Service Desk Agent',
                'Data Scientist',
                'Account Manager',
                'Backend Engineer',
                'Data Analyst'
            ],
            label_visibility='collapsed'
        )

    with col2:
        # Length dropdown
        length = st.selectbox('Length', ['Regular', 'Concise', 'Explanatory'], label_visibility='collapsed')

    with col3:
        # Style dropdown
        style = st.selectbox('Style', ['Simple', 'Formal', 'Casual', 'Layman', 'Technical'], label_visibility='collapsed')
    
    with col4:
        # Search button with right alignment and filled color
        search_clicked = st.button('Search', type='primary', use_container_width=True)

    # When the user presses the 'Search' button
    if search_clicked:
        if query:
            # Adjust TOP_K based on the selected length
            top_k_map = {'Concise': 5, 'Regular': 20, 'Explanatory': 50}
            top_k = top_k_map.get(length, DEFAULT_TOP_K)

            # If no persona is selected, use the default persona
            if persona:
                prompt_persona = f'As an assistant to {persona}, you provide answers based on the context provided.\n'
            else:
                prompt_persona = f'As an assistant to {DEFAULT_PERSONA}, you provide answers based on the context provided.\n'
            
            # If no style is selected, use the default style
            if style:
                prompt_style = f'Respond in a {style} style.\n'
            else:
                prompt_style = f'Respond in a {DEFAULT_STYLE} style.\n'
            
            # Construct the query prompt
            query_prompt = prompt_persona + prompt_style + query

            # Load the FAISS index and metadata
            index, metadata = load_assets(index_file, metadata_file)

            # Perform semantic search on the query
            top_chunks = semantic_search(query_prompt, index, metadata, top_k)
            print(top_chunks)

            # Generate a summary based on the top chunks
            summary = generate_summary(query_prompt, top_chunks)

            # Display the summary and relevant articles
            st.header('Summary')
            st.write(summary)

            st.header('References')

            unique_references = {chunk["title"]: chunk["url"] for chunk in top_chunks}
            for title, url in unique_references.items():
                st.markdown(f'- [{title}]({url})')
        else:
            st.warning('Please enter a query to search.')


# -------------------
# Main execution
# -------------------
if __name__ == '__main__':
    display_ui()
