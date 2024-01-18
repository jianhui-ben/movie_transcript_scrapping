## scrape the movie transcript data from https://subslikescript.com/

import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os


def scrape_movie_script(url):
    """
    Scrapes the movie script from the given URL.

    Args:
        url (str): The URL of the webpage containing the movie script.

    Returns:
        list: A list containing the movie title and the script content.
              If the script is not found, the script content will be None.

    Raises:
        None

    """
    # Set a custom User-Agent header to mimic a regular browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send a GET request to the URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the div with class 'full-script'
        div = soup.find('div', class_='full-script')

        # Extract movie title and year
        movie_title_year = extract_movie_title_year(soup.title.string)

        # Prepare the result list
        result = [movie_title_year, div.text] if div else [movie_title_year, None]

        # Add a delay to avoid rate limiting
        time.sleep(1)

        return result

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def extract_movie_title_year(script_title):
    """
    Extracts the movie title and year from a given script title.

    Args:
        script_title (str): The title of the script.

    Returns:
        str: The movie title and year in the format "movie_title (year)".
             Returns None if no match is found.
    """
    # Define a regular expression pattern to extract the movie title with or without space before the year
    pattern = r'^(.*?\S)\s?(\(\d{4}\))'
    
    # Use re.search to find the pattern in the string
    match = re.search(pattern, script_title)

    # Extract the matched parts (group 1 and group 2) if a match is found
    if match:
        movie_title = match.group(1)
        year = match.group(2)
        return f"{movie_title} {year}"
    else:
        return None

def extract_movie_urls(page_url):
    """
    Extracts movie URLs from a given page URL.

    Args:
        page_url (str): The URL of the page to scrape.

    Returns:
        list: A list of movie URLs extracted from the page.

    Raises:
        None

    """
    # Set a custom User-Agent header to mimic a regular browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send a GET request to the URL
    response = requests.get(page_url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the ul with class 'scripts-list'
        ul = soup.find('ul', class_='scripts-list')

        # Find all links within the ul
        script_links = ul.find_all('a')

        # Extract URLs from the links
        movie_urls = ['https://subslikescript.com/' + link['href'] for link in script_links]

        return movie_urls

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None


# ## 1. Example usage for scraping one page (for one movie)
# url = 'https://subslikescript.com/movie/A_Blade_in_the_Dark-85303'
# result = scrape_movie_script(url)

# if result:
#     print("Movie Title and Year:", result[0])
#     print("Script Content:")
#     print(result[1])
# else:
#     print("Scraping failed.")


# # 2. Example usage for scraping the first page (page 1)
# page_url = 'https://subslikescript.com/movies?page=1'
# movie_urls = extract_movie_urls(page_url)

# if movie_urls:
#     print("Movie URLs:")
#     for url in movie_urls:
#         print(url)
# else:
#     print("Scraping failed.")
    


def save_to_jsonl(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for entry in data:
            json.dump(entry, file, ensure_ascii=False)
            file.write('\n')

# # 3. Example usage for scraping the first page's transcript and save into a local jsonl file
# # for analytical purpose, it's better to be saved in parquet format
# page_url = 'https://subslikescript.com/movies?page=1'
# movie_urls = extract_movie_urls(page_url)

# # List to store scraped data
# dataset = []

# if movie_urls:
#     for url in movie_urls:
#         result = scrape_movie_script(url)
#         if result:
#             entry = {
#                 "Movie Title and Year": result[0],
#                 "Script Content": result[1]
#             }
#             dataset.append(entry)

# # Save the dataset to a JSONL file
# save_to_jsonl(dataset, 'movie_dataset.jsonl')
        

# 4. Example usage for scraping multiple pages
start_page = 1
end_page = 1794 ## last page is 1794
pages_per_file = 100

# List to store scraped data
dataset = []

# Create the 'data' folder if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')


for page in range(start_page, end_page + 1):
    page_url = f'https://subslikescript.com/movies?page={page}'
    movie_urls = extract_movie_urls(page_url)

    if movie_urls:
        for url in movie_urls:
            print(f"Parsing transcript for {url}")
            result = scrape_movie_script(url)
            if result:
                entry = {
                    "Movie Title and Year": result[0],
                    "Script Content": result[1]
                }
                dataset.append(entry)

    # Save the dataset to a new JSONL file every 'pages_per_file' pages
    if page % pages_per_file == 0 or page == end_page:
        filename = f'data/movie_dataset_page_{page - pages_per_file + 1}_to_page_{page}.jsonl'
        save_to_jsonl(dataset, filename)
        dataset = []  # Clear the dataset for the next set of pages

    # Add a delay to avoid rate limiting
    time.sleep(1)

print("Scraping and saving completed.")
