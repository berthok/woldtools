WOLD_URL = "https://www.woldiangames.com/games_index_career.htm"


def extract_and_parse_datetime(text):
    import re
    from datetime import datetime
    # Regex pattern to match "Friday February 14th, 2025 11:20:54 PM"
    pattern = r'\b[A-Za-z]+ \w+ \d{1,2}(?:st|nd|rd|th)?, \d{4} \d{1,2}:\d{2}:\d{2} [APM]{2}\b'

    # Search for the datetime string in the larger text
    match = re.search(pattern, text)

    if match:
        date_str = match.group()

        # Remove ordinal suffix (st, nd, rd, th)
        clean_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

        # Define datetime format
        date_format = "%A %B %d, %Y %I:%M:%S %p"

        # Parse and return datetime object
        return datetime.strptime(clean_date_str, date_format)

    return None  # Return None if no match is found


def replace_smart_quotes(text):
    import re
    replacements = {
        '&quot;': '"',
        '&#34;': '"', "&#39;": "'",
        "“": '"', "”": '"',  # Double quotes
        "‘": "'", "’": "'"   # Single quotes
    }
    return re.sub("|".join(re.escape(k) for k in replacements), lambda m: replacements[m.group()], text)


def fetch_career_games():
    # Gather info about all current career games in the Wold
    import requests
    import re

    result = []

    # Send a GET request to the website
    response = requests.get(WOLD_URL)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Define the regex pattern to match the entire <a> tag
        pattern = r'<a\s+[^>]*>.*?</a>'

        # Find all matches for the pattern
        links = re.findall(pattern, response.text, re.DOTALL)

        # Iterate through links
        for link in links:
            # Remove the base href tag from the string to avoid extracting it by mistake
            link = link.replace('_base_href="https://www.woldiangames.com/inc/themes/DEFAULT/"','')

            # Define the regex pattern to match the <a> tag with <img> inside it
            pattern = r'<a\s+[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>.*?<img\s+[^>]*alt=["\']([^"\']+)["\'][^>]*>.*?</a>'

            # Find all matches for the pattern
            matches = re.findall(pattern, link, re.DOTALL)

            # If data exists, extract the data into a list of dict entries
            if len(matches) == 1:
                for match in matches:
                    # Avoid Archived results
                    if 'Archived' not in match[1]:
                        game_id = match[0].split('=')[1]
                        game_name = match[1]
                        game_url = match[0]

                        result.append({"game_id": game_id,
                                       "game_name": game_name,
                                       "game_url": game_url})

        return result
    else:
        print(f"Failed to retrieve the website: {response.status_code}")
        return result


def fetch_career_game_data(url):
    # Gather info about a specific career game
    import requests

    r = requests.get(url)
    r.encoding = 'utf-8'
    raw_data = r.content.decode(r.apparent_encoding, errors='replace')

    return raw_data


def isolate_posts_from_raw_data(raw_data):
    # Searches through raw data for posts and returns them in a list
    post_start = '<!-- START NEW POST -->'
    post_end = '''<br/>
  <br/>'''

    posts = []
    post_counter = 0
    for data in raw_data.split(post_start):
        if '<head>' not in data:
            post_counter = post_counter + 1
            raw_post = data.split(post_end)[0]
            posts.append({"post_id": post_counter,
                        "raw_post": raw_post})

    return posts


def parse_headers_from_posts(posts):
    # Iterates through posts and parses out headers
    for post in posts:
        header = post.get('raw_post').split('</big>')[0]
        header = header.split('</b>')[0]
        header = header.replace('<big><b>', '')
        header = header.strip('\t \r\n')
        post['raw_header'] = header
    return posts


def extract_links(html):
    import re

    pattern = r'<a\s+[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>'
    matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

    links = [{"url": match[0], "text": match[1].strip()} for match in matches]
    return links


def find_dms(text):
    import re
    # Searches for DM names and returns them
    pattern = r'(?:[-–—]\s*)?(DM|GM|CoGM|Co-DM|CoDM)\s+([A-Z][a-zA-Z]*(?:\s+(?:and|&)?\s*[A-Z][a-zA-Z]*)*)\b'
    matches = re.findall(pattern, text)

    # Extract only the names, ignoring the DM/GM prefix
    return [match[1] for match in matches]


def export_data_to_file(data):
    # Write dictionary to a JSON file
    import json

    with open("wold_career_games.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, default=str)  # indent=4 makes it more readable


def parse_header_information(posts):
    # Iterates through posts and parses header information
    # AC 14 67/67 Sakura Kanuzaki; Julio A. (example of problem header)
    for post in posts:
        header = post.get('raw_header')

        # Detect if post is by a GM
        post['dm_post'] = 0
        if 'DM ' in header or 'GM ' in header:
            post['dm_post'] = 1
            post['dm'] = find_dms(header)

        # Extract URLs
        post['header_urls'] = []
        if '</a>' in header:
            post['header_urls'] = extract_links(header)

        # Extract Player Name
        post['player_name'] = 'Unknown'
        if ')' in header and '(' in header:
            post['player_name'] = header.split(')')[0].split('(')[1]

        # Extract Character Name
        if len(post.get('header_urls')) == 1:
            for url in post.get('header_urls'):
                if url.get('text') == 'Character' or url.get('text') == 'Character Sheet':
                    post['character_name'] = header.split('(')[0].strip()
                else:
                    post['character_name'] = url.get('text')
        if post.get('dm_post') == 1:
            post['character_name'] = 'DM'

        if post.get('character_name'):
            post['character_name'] = replace_smart_quotes(post.get('character_name'))

        # Extract Armor Class
        # Extract Hit Points
        # Extract Passive Perception
        # Extract Conditions

    return posts
