import requests, json
from bs4 import BeautifulSoup


# Define constants for the script
SECTION_ID = '22802387434397'
BASE_URL = 'https://support.inspera.com/api/v2/help_center/en-us'


# Fetch all articles from the Psychometrics section using the Zendesk API
def get_all_articles(section_id):
    # Extracts all article links from a given section ID
    url = f'{BASE_URL}/sections/{SECTION_ID}/articles.json'

    # The API returns a JSON response containing article details
    response = requests.get(url)

    # Gets articles from the JSON response
    all_articles = response.json().get('articles', [])

    print('Found '+ str(len(all_articles)) + ' articles in this section.')
    print('Fetching article contents...')

    return all_articles


def clean_html(html_body):
    soup = BeautifulSoup(html_body, 'html.parser')
    content_parts = []

    for tag in soup.find_all(['h2', 'h3', 'p', 'li']):
        text = tag.get_text(strip=True)
        if not text:
            continue
        if tag.name in ['h2', 'h3']:
            content_parts.append(f'\n## {text}' if tag.name == 'h2' else f'\n### {text}')
        elif tag.name == 'li':
            content_parts.append(f'- {text}')
        else:
            content_parts.append(text)

    return '\n'.join(content_parts).strip()


# Fetch each article's content using its ID and extract its HTML content
def get_full_article(article_id):
    # Construct the URL for the article using its ID
    url = f'{BASE_URL}/articles/{article_id}.json'

    # The API returns a JSON response containing article details
    response = requests.get(url)

    # Returns the article content from the JSON response
    return response.json()['article']


# Function to clean the HTML content of the article
def clean_html(html_body):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_body, "html.parser")
    content_parts = []

    # Extract relevant tags and their text content
    for tag in soup.find_all(["h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        # Skip empty text
        if not text:
            continue
        # Format the text based on the tag type
        if tag.name in ["h2", "h3"]:
            content_parts.append(f"\n## {text}" if tag.name == "h2" else f"\n### {text}")
        elif tag.name == "li":
            content_parts.append(f"- {text}")
        else:
            content_parts.append(text)
    
    # Join the content parts into a single string and return it
    return "\n".join(content_parts).strip()


# Main function to fetch article links and extract content
def main():
    # Psychometrics section ID
    section_id = '22802387434397'
    print('Fetching article links via API...')

    # Get the article links, IDs, and contents from the specified section
    all_articles = get_all_articles(section_id)

    # Initialize an empty list to store the content of all articles
    all_content = []

    # Loop through each article and fetch its content
    for article in all_articles:
        # Fetch the full article content using its ID
        full = get_full_article(article['id'])
        # Clean the HTML content and store it in the list
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

    print('✅ Finished! Data saved to data.json')


# Execting the code using the main function
if __name__ == '__main__':
    main()