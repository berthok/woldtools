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


def extract_game_icon_url(text, keyword):
    import re
    """
    Extracts a URL from the given text that contains both 'Game Icon' and the specified keyword.
    
    Args:
        text (str): The input string containing one or more URLs.
        keyword (str): The keyword that must be present in the URL.
        
    Returns:
        str or None: The extracted URL, or None if not found.
    """
    # Regular expression to match URLs
    url_pattern = r'https?://\S+'  # Matches URLs starting with http or https

    # Find all URLs in the text
    urls = re.findall(url_pattern, text)

    # Filter URLs that contain both "Game Icon" and the keyword
    for url in urls:
        #print(url)
        if "Game_Icon" in url and keyword in str(url).lower():
            return url

    return None


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
                        game_icon = extract_game_icon_url(response.text, game_id)
                        game_icon = game_icon.replace('\"','')

                        result.append({"game_id": game_id,
                                       "game_name": game_name,
                                       "game_url": game_url,
                                       "game_icon": game_icon})

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


def clean_posts(posts):
    # Iterates through posts and cleans up each post for display

    for post in posts:
        clean_post = post.get('raw_post')
        # Remove leading and trailing white space
        clean_post = clean_post.strip()
        # Replace <big> tag with a div of class "post_header"
        clean_post = clean_post.replace('<big>', '<div class=\"post_header\">')
        clean_post = clean_post.replace('</big>', '</div class=\"post_header\">')
        clean_post = clean_post.replace('<div class=\"post_header\"><b>', '<div class=\"post_header\">')
        clean_post = clean_post.replace('</b></div class=\"post_header\">', '</div class=\"post_header\">')
        # Replace formatting around post datetiem with a div of class "post_datetime"
        clean_post = clean_post.replace('<font size=\"-1\"><br>', '<div class=\"post_datetime\">')
        clean_post = clean_post.replace('</font><br>', '</div class=\"post_datetime\">')
        # Replace &nbsp; characters
        clean_post = clean_post.replace('&nbsp;', '')
        # Remove the trailing div of class "hrThin"
        clean_post = clean_post.replace('<br><br><div class=\"hrThin\"></div>', '')
        # Replace single and double quote characters
        clean_post = replace_smart_quotes(clean_post)
        # Mark quotes with a div of class "dialog"
        clean_post = clean_post.replace('<b>\"', '<div class=\"dialog\">\"')
        clean_post = clean_post.replace('\"</b>', '\"</div class=\"dialog\">')
        # Count all number of open dialog divs
        # Count all number of close dialog divs
        # If the number of close divs are lower than the open divs...
        # Split up the string based on open divs...
        # Starting with element [1], look for close divs
        # If a close div is missing, look for a [/b] tag and add it afterwards
        # If a close div is missing, look for a " and add it afterwards
        # If neither of those is present and it is the last element, add the close div at the end of the string


        # If the number of open divs are lower than the close divs...

        # Remove trailing line break
        if clean_post.endswith('<br>'):
            clean_post = clean_post[:-4]
        # Wrap post contents (non-header) in div of class "post_contents"
        clean_post = clean_post.replace('</div class=\"post_datetime\">\n','</div class=\"post_datetime\"><div class=\"post_contents\">')
        clean_post = clean_post + '</div class=\"post_contents\">'

        #! Need to do a count of each dialog div and tag to make sure every open tag is closed.

        # Apply changes
        post['clean_post'] = clean_post

    return posts


def extract_ac(text):
    # Extracts the AC from a string. Can be AC9 or AC 9. Can handle 2-digit AC values as well.
    import re

    match = re.search(r'AC\s*(\d+)', text)
    return int(match.group(1)) if match else None


def extract_hp(text):
    # Extracts HP as "HP 12/14" or "HP12/14" or "HP 12/14/3" as (current, max, temp)
    import re

    match = re.search(r'HP\s*(\d+)/(\d+)(?:/(\d+))?', text)
    if match:
        current_hp = int(match.group(1))
        max_hp = int(match.group(2))
        temp_hp = int(match.group(3)) if match.group(3) else 0
        return current_hp, max_hp, temp_hp
    return None


def extract_passive_perception(text):
    # Extracts PP as "PP9" or "PP9" or "PP13" or "PP 13"
    import re

    match = re.search(r'PP\s*(\d+)', text)
    if match:
        return int(match.group(1))
    return None


def extract_conditions(text):
    # Extracts conditions and returns them in a list
    from objects import conditions

    result = []

    conditions_list = conditions.keys()
    for c in conditions_list:
        if str(c).lower() in str(text).lower():
            result.append({c: conditions.get(c)})

    return result


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
        post['ac'] = extract_ac(post.get('raw_header'))

        # Extract Hit Points
        post['hp'] = extract_hp(post.get('raw_header'))

        # Extract Passive Perception
        post['pp'] = extract_passive_perception(post.get('raw_header'))

        # Extract Conditions
        post['conditions'] = extract_conditions(post.get('raw_header'))

    return posts
