# InsperaHelpDocs
This project enables efficient searching of help center documentation using semantic search and summarization techniques.

## Implementation Details

### Libraries and Tools
- **Streamlit**: For building the user interface.
- **FAISS**: For efficient similarity search and clustering of embeddings.
- **Google Generative AI**: For generating embeddings and summaries.
- **NumPy**: For numerical operations on embeddings.
- **JSON**: For handling metadata and article content.

### Key Components
1. **Article Scraping and Chunking (`_1_scraper.py`)**:
   - Articles are fetched by category and section from the help center using API calls or web scraping techniques.
   - The content is cleaned to remove unnecessary HTML tags, special characters, and other noise.
   - The cleaned content is saved to `data.json` for further processing.
   - Text is chunked into smaller pieces with overlap to preserve context, ensuring that no important information is lost during embedding. The chunks are saved to `chunks.json`.

2. **Embedding and Indexing (`_2_embeddings.py`)**:
   - The chunked content is loaded from `chunks.json` for processing.
   - Each chunk is embedded into a high-dimensional vector space using Google Generative AI's embedding model.
   - A FAISS index is created to store these embeddings, enabling fast similarity searches. The index is optimized for efficient retrieval of the most relevant chunks.

3. **Semantic Search and Summarization (`_3_query.py`)**:
   - User queries are embedded into the same vector space as the chunks using the same embedding model.
   - The FAISS index is queried to retrieve the top `k` chunks based on similarity scores.
   - The retrieved chunks are combined to form a coherent context for the query.
   - Google Generative AI is used to generate a concise and coherent summary based on the query and the retrieved context, ensuring that the user receives relevant and actionable information.

4. **User Interface (`_4_app.py`)**:
   - A Streamlit-based UI allows users to input queries in a simple and intuitive manner.
   - The app displays a summary of the query results, along with a list of relevant articles and their references.
   - Users can click on references to view the original articles or additional details.
   - The interface is designed to be responsive and user-friendly, ensuring a seamless experience for users.

## Steps to Run the Project

1. **Set Up Environment**:
   - Install the required Python libraries:
     ```bash
     pip install streamlit faiss-cpu numpy google-generativeai
     ```

2. **Run the Scraper**:
   - Fetch and process articles:
     ```bash
     python _1_scraper.py
     ```

3. **Generate Embeddings**:
   - Create embeddings and build the FAISS index:
     ```bash
     python _2_embeddings.py
     ```

4. **Run the Application**:
   - Start the Streamlit app:
     ```bash
     streamlit run _4_app.py
     ```

---

This version focuses on the technical aspects of the project, providing clear instructions and details about the implementation. Let me know if you'd like further adjustments!
