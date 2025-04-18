import requests, json, uuid
from bs4 import BeautifulSoup


# Number of words in each chunk
CHUNK_SIZE = 300

# Number of words to overlap between chunks
OVERLAP = 50 

# The base URL for the Zendesk API
BASE_URL = 'https://support.inspera.com/api/v2/help_center/en-us'


# -------------------
# Function to fetch all categories from the Zendesk API
# -------------------
def get_all_categories():
    response = requests.get(f'{BASE_URL}/categories.json')
    response.raise_for_status()
    return response.json()['categories']


# -------------------
# Function to fetch all sections for a given category from the Zendesk API
# -------------------
def get_sections_for_category(category_id):
    response = requests.get(f'{BASE_URL}/categories/{category_id}/sections.json')
    response.raise_for_status()
    return response.json()['sections']


# -------------------
# Fetch all articles from the Psychometrics section using the Zendesk API
# -------------------
def get_all_articles(section_id):
    # Extracts all article links from a given section ID
    url = f'{BASE_URL}/sections/{section_id}/articles.json'

    # The API returns a JSON response containing page HTML
    response = requests.get(url)

    # Gets articles from the JSON response
    all_articles = response.json().get('articles', [])
    print(f'--- {len(all_articles)} articles')

    return all_articles


# -------------------
# Fetch each article's content using its ID and extract its HTML content
# -------------------
def get_full_article(article_id):
    print(f'Fetching article {article_id}...')

    # Construct the URL for the article using its ID
    url = f'{BASE_URL}/articles/{article_id}.json'

    # The API returns a JSON response containing page HTML
    response = requests.get(url)

    # Returns the article content from the JSON response
    return response.json()['article']


# -------------------
# Function to clean the HTML content of the article
# -------------------
def clean_html(html_body):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_body, 'html.parser')
    content_parts = []

    # Extract relevant tags and their text content
    for tag in soup.find_all(['h2', 'h3', 'p', 'li']):
        text = tag.get_text(strip=True)
        # Skip empty text
        if not text:
            continue
        # Format the text based on the tag type
        if tag.name in ['h2', 'h3']:
            content_parts.append(f'\n## {text}' if tag.name == 'h2' else f'\n### {text}')
        elif tag.name == 'li':
            content_parts.append(f'- {text}')
        else:
            content_parts.append(text)
    
    # Join the content parts into a single string and return it
    return '\n'.join(content_parts).strip()


# -------------------
# Function to write the cleaned content to a JSON file
# -------------------
def write_content_to_file(all_articles):
    # Initialize an empty list to store the content of all articles
    all_content = []

    # Loop through each article and fetch its content
    for article in all_articles:
        print(f'Adding article {article["id"]}...')
        full = get_full_article(article['id'])
        cleaned_body = clean_html(full['body'])
        # Append the cleaned content to the list
        all_content.append({
            'id': full['id'],
            'title': full['title'],
            'url': full['html_url'],
            'content': cleaned_body
        })
    
    # Save the cleaned content to a JSON file
    # Open a file in write mode and save the content as JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_content, f, indent=2, ensure_ascii=False)
    
    # Print the number of articles processed
    print(f'✅ Done. Stored {len(all_content)} articles.')


# -------------------
# Function to chunk the text into smaller pieces for processing
# -------------------
def chunk_text_to_file(json_articles, chunk_size, overlap):
    print('Chunking content and writing to file...')

    # Initialize an empty list to store the chunked data
    chunked_data = []

    # Loop through each article and split its content into chunks
    for article in json_articles:
        print(f'Chunking article {article["id"]}...')

        # Split the article content into words
        words = article['content'].split()
        # Initialize the starting index for chunking
        start = 0

        # Loop to create chunks of the specified size with overlap
        while start < len(words):
            # Split the text into chunks with some overlap to keep context between them
            end = start + chunk_size
            chunk = words[start:end]
            start += chunk_size - overlap
            
            # Append the chunked data to the list
            chunked_data.append({
                # Generate a unique ID for each chunk using UUID
                'chunk_id': str(uuid.uuid4()),
                'article_id': article['id'],
                'title': article['title'],
                'url': article['url'],
                'text': ' '.join(chunk)
            })

    # Write the chunked data to a JSON file
    # Open a file in write mode and save the chunked data as JSON
    with open('chunks.json', 'w', encoding='utf-8') as f:
        json.dump(chunked_data, f, indent=2, ensure_ascii=False)
    
    # Print the number of chunks created
    print(f'✅ Done. Stored {len(chunked_data)} chunks.')


# -------------------
# Main function to fetch article links and extract content
# -------------------
def main():
    categories = get_all_categories()
    print('🗃️ Categories and their Sections:\n')

    all_articles = []
    # Loop through each category and fetch its sections
    for category in categories:
        print(f'📁 {category["name"]} (ID: {category["id"]})')

        # Fetch sections for the current category
        sections = get_sections_for_category(category['id'])
        for section in sections:
            print(f'- 📄 {section["name"]} (ID: {section["id"]}')

            # Fetch articles for the specified section ID
            section_articles = get_all_articles(section['id'])
            all_articles.extend(section_articles)

    print(f'🔎 Found {len(all_articles)} articles.')

    # Write the content of all articles to a JSON file
    write_content_to_file(all_articles)

    # Load the content from the JSON file
    with open('data.json', 'r', encoding='utf-8') as f:
        json_articles = json.load(f)

    # Chunk the text and store them in a JSON file
    print('Set chunk size to 300 words and overlap to 50 words.')
    chunk_text_to_file(json_articles, chunk_size=300, overlap=50)


# -------------------
# Executing the code using the main function
# -------------------
if __name__ == '__main__':
    main()