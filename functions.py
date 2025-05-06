
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
    from objects import wold_url

    result = []

    # Send a GET request to the website
    response = requests.get(wold_url)

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
            if '<!-- E' in raw_post:
                raw_post = raw_post.split('<!-- E')[0]
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
        # Replace <big> tag with a span of class "post_header"
        clean_post = clean_post.replace('<big>', '<span class=\"post-header\">')
        clean_post = clean_post.replace('</big>', '</span class=\"post-header\">')
        clean_post = clean_post.replace('<span class=\"post-header\"><b>', '<span class=\"post-header\">')
        clean_post = clean_post.replace('</b></span class=\"post-header\">', '</span class=\"post-header\">')
        # Replace formatting around post datetime with a span of class "post_datetime"

        clean_post = clean_post.replace('<font size=\"-1\"><br>', '<span class=\"post-datetime\">')
        clean_post = clean_post.replace('</font><br>', '</span class=\"post-datetime\">')
        # Replace &nbsp; characters
        clean_post = clean_post.replace('&nbsp;', '')
        # Remove the trailing div of class "hrThin"
        clean_post = clean_post.replace('<br><br><div class=\"hrThin\"></div>', '')
        # Replace single and double quote characters
        clean_post = replace_smart_quotes(clean_post)

        # Remove trailing line break
        if clean_post.endswith('<br>'):
            clean_post = clean_post[:-4]
        # Wrap post contents (non-header) in div of class "post-contents"
        clean_post = clean_post.replace('</span class=\"post-datetime\">\n','</span class=\"post-datetime\"><div class=\"post-contents\">')
        clean_post = clean_post + '</div class=\"post-contents\">'

        # Wrap post contents (header) in div of "post-clean-header"
        clean_post_header = clean_post.split('<div class=\"post-contents\">')[0]
        if '; <br>' in clean_post_header:
            clean_post_header = clean_post_header.replace('; <br>','<span class=\"post-datetime\">')
        if '<font size=\"-1\">' in clean_post_header:
            clean_post_header = clean_post_header.replace('<font size=\"-1\">','<span class=\"dice-rolls\">')
            clean_post_header = clean_post_header.replace('<span class=\"post-datetime\">',';</span class=\"dice-rolls\"><span class=\"post-datetime\">')
        clean_post_header = clean_post_header.replace('<br>','')
        clean_post_header = '<div class=\"post-clean-header\">' + clean_post_header + '</div class=\"post-clean-header\">'

        # Apply changes
        post['clean_post'] = clean_post
        post['clean_post_header'] = clean_post_header
        post['clean_post_contents'] = '<div class=\"post-contents\">' + clean_post.split('<div class=\"post-contents\">')[1]

    return posts


def extract_dice_rolls(roll_string):
    # Regular expression pattern to match dice rolls
    import re

    #pattern = r'(\d*d\d+([+-]\d+)?=\d+|\d*d\d+([+-]\d+)?)'
    pattern = r'\d*d\d+(?:[+-]\d+)?=\d+\s*;'
    
    # Find all matches using re.findall()
    matches = re.findall(pattern, roll_string)

    rolls = []
    for match in matches:
        match = match.replace(';','').strip()
        if str(match).startswith('d'):
            # Give natural 20s a special class
            if str(match).startswith('d20'):
                modifier, result_value = str(match).split('=')
                modifier = modifier.replace('d20','').replace('+','')
                if modifier == '':
                    modifier = '0'
                if 20 + int(modifier) == int(result_value):
                    rolls.append('<span class=\"nat-20\">1' + str(match) + '</span>')
                else:
                    rolls.append('1' + str(match))
            else:
                rolls.append('1' + str(match))
        #rolls.append(str(match))
    #if rolls == ['1d']:
    #    rolls = []

    # Return the matched rolls
    return rolls


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
    # Extracts urls from a string
    import re

    pattern = r'<a\s+[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>'
    matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

    links = [{"url": match[0], "text": match[1].strip()} for match in matches]
    return links


def find_dms(text):
    # Searches for DM names and returns them
    import re

    pattern = r'(?:[-–—]\s*)?(DM|GM|CoGM|Co-DM|CoDM)\s+([A-Z][a-zA-Z]*(?:\s+(?:and|&)?\s*[A-Z][a-zA-Z]*)*)\b'
    matches = re.findall(pattern, text)

    # Extract only the names, ignoring the DM/GM prefix
    return [match[1] for match in matches]


def export_data_to_file(data):
    # Write dictionary to a JSON file
    import os
    import json
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"wold_career_games.json")
    with open(json_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, default=str)  # indent=4 makes it more readable


def parse_header_information(posts):
    # Iterates through posts and parses header information
    # AC 14 67/67 Sakura Kanuzaki; Julio A. (example of problem header)
    for post in posts:
        header = post.get('raw_header')
        # print('Parsing header:')
        # print(header)

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
        post['ac'] = extract_ac(header)

        # Extract Hit Points
        post['hp'] = extract_hp(header)

        # Extract Passive Perception
        post['pp'] = extract_passive_perception(header)

        # Extract Conditions
        post['conditions'] = extract_conditions(header)

        # Extract Dice Rolls
        post['dice_rolls'] = extract_dice_rolls(post.get('clean_post_header'))

    return posts


def upload_file_ftps(host, port, username, password, local_file, remote_path):
    from ftplib import FTP_TLS
    try:
        # Connect to the FTPS server
        ftps = FTP_TLS()
        ftps.connect(host, port)
        ftps.login(username, password)
        ftps.prot_p()  # Switch to secure data connection (explicit FTPS)

        # Open the file and upload it
        with open(local_file, "rb") as file:
            content = file.read().decode("utf-8", errors="replace")
        with open("your_file_fixed.html", "w", encoding="utf-8") as file:
            file.write(content)
        with open(local_file, "rb") as file:
            ftps.storbinary(f"STOR {remote_path}", file)

        print(f"File '{local_file}' uploaded successfully to '{remote_path}'")

        # Close the connection
        ftps.quit()

    except Exception as e:
        print(f"Error: {e}")


def build_wold_json_file():
    import os
    import colorama
    from colorama import Fore
    from datetime import datetime

    colorama.init()
    # Gather up a list of all current games
    career_games = fetch_career_games()

    print('Loading Data for Career Games...')

    for game in career_games:
        game['page_generation_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f' - {Fore.CYAN}{game.get("game_name")}{Fore.RESET} ({game.get("game_id")})')
        print(f'    - URL: {Fore.YELLOW}{game.get("game_url")}{Fore.RESET}')

        print('       - Fetching Raw Data...')
        game['raw_data'] = fetch_career_game_data(game.get('game_url'))

        print('       - Isolating Posts from Raw Data...')
        game['posts'] = isolate_posts_from_raw_data(game.get('raw_data'))
        print(f'          - Found {Fore.GREEN}{len(game.get("posts"))}{Fore.RESET} Posts')

        print('       - Cleaning Posts...')
        game['posts'] = clean_posts(game.get('posts'))
        print('          - Done')

        print('       - Parsing Post Datetimes...')
        for post in game.get('posts'):
            post['post_datetime'] = extract_and_parse_datetime(post.get('raw_post'))
            game['most_recent_post_datetime'] = post.get('post_datetime')
        print(f'          - Most Recent Post: {Fore.LIGHTMAGENTA_EX}{game.get("most_recent_post_datetime")}{Fore.RESET}')

        print('       - Parsing Header Info From Posts...')
        game['posts'] = parse_headers_from_posts(game['posts'])
        print('          - Done')

        print('       - Parsing Header Post Info...')
        game['posts'] = parse_header_information(game['posts'])

        # Generate list of characters
        game['characters'] = {}
        for post in game.get('posts'):
            if post.get('character_name'):
                if post.get('character_name') != 'DM':
                    if len(post.get('header_urls')) > 0:
                        game['characters'][post.get('character_name')] = {'name': post.get('character_name'),
                                                                          'given_name': str(post.get('character_name')).split(' ')[0],
                                                                          'url': post.get('header_urls')[0].get('url'),
                                                                          'hp': post.get('hp'),
                                                                          'ac': post.get('ac'),
                                                                          'pp': post.get('pp')}
                    else:
                        game['characters'][post.get('character_name')] = {'name': post.get('character_name'),
                                                                          'given_name': str(post.get('character_name')).split(' ')[0],
                                                                          'url': None,
                                                                          'hp': post.get('hp'),
                                                                          'ac': post.get('ac'),
                                                                          'pp': post.get('pp')}
        # Sort the characters by name
        game['characters'] = dict(sorted(game.get('characters').items()))

        # Add custom class for all characters mentioned in the posts
        for post in game.get('posts'):
            for character in game.get('characters').values():
                if character.get('given_name') in post.get('clean_post_contents'):
                    if len(str(character.get('given_name'))) > 2:
                        post['clean_post_contents'] = post['clean_post_contents'].replace(character.get('given_name'), f'<span class=\"character-mention\">{character.get("given_name")}</span>')

        # Add dice roll statistics to the game
        game = build_dice_roll_statistics(game)


        # Create URL for the Dark Wold game page
        game['darkwold_url'] = f'game/{game.get("game_id")}.html'

        # Create the Dark Wold game page file path
        games_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'game')
        game['darkwold_file_path'] = os.path.join(games_dir, f'{game.get("game_id")}.html')

    print('Exporting Data to JSON...')
    export_data_to_file(career_games)
    print('Done!')

    colorama.deinit()


def build_dice_roll_statistics(game):
    import os
    import colorama
    from colorama import Fore
    from datetime import datetime

    game['dice_rolls'] = []
    game['dice_roll_statistics'] = {}

    for character in game.get('characters').values():
        character['dice_rolls'] = []
        character['dice_roll_statistics'] ={}

    colorama.init()
    
    for post in game.get('posts'):
        post_date = post.get('post_datetime').isoformat()
        if len(post.get('dice_rolls')) > 0:
            for dice_roll in post.get('dice_rolls'):
                if '1d20' in dice_roll:
                    roll = dice_roll.replace('<span class=\"nat-20\">','').replace('</span>','').replace('1d20','')
                    if '+' in roll:
                        mod, total = roll.split('=')
                        raw_roll = int(total) - int(mod)
                    elif '-' in roll:
                        mod, total = roll.split('=')
                        raw_roll = int(total) - int(mod)
                    else:
                        raw_roll = int(roll.replace('=',''))
                    game['dice_rolls'].append({post_date : raw_roll})
                    if post.get('character_name') in game.get('characters').keys():
                        game['characters'][post.get('character_name')]['dice_rolls'].append({post_date : raw_roll})

    game_rolls = game.get('dice_rolls')
    game_roll_list = []
    for roll in game_rolls:
        for r in roll.values():
            game_roll_list.append(r)
    if len(game_roll_list) == 0:
        game['dice_roll_statistics']['average'] = 0
    else:
        game['dice_roll_statistics']['average'] = sum(game_roll_list) / len(game_roll_list)

    for character in game.get('characters').values():
        character_rolls = character.get('dice_rolls')
        character_roll_list = []
        for roll in character_rolls:
            for r in roll.values():
                character_roll_list.append(r)
        if len(character_roll_list) == 0:
            character['dice_roll_statistics']['average'] = 0
        else:
            character['dice_roll_statistics']['average'] = sum(character_roll_list) / len(character_roll_list)

    


    colorama.deinit()
    return game
    


def create_landing_page(game_links):
    # Create wold selection landing page
    import os
    from jinja2 import Environment, FileSystemLoader
    
    # Load the template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('landing_page.html')

    # Render the template
    output_html = template.render(links=game_links)

    # Save the output into file
    with open(os.path.join(script_dir,'landing_page.html'), 'w', encoding='utf-8') as f:
        f.write(output_html)

    return None


def create_game_page(game):
    # Create the html for a dark wold game page.
    import os
    from jinja2 import Environment, FileSystemLoader
    
    # Load the template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('game.html')

    # Render the template
    output_html = template.render(game=game)

    # Save the output into file
    with open(game.get('darkwold_file_path'), 'w', encoding='utf-8') as f:
        f.write(output_html)

    return None

def build_sheriff_report_page(games):
    # Create the html for a sheriff report page.
    import os
    from jinja2 import Environment, FileSystemLoader
    from datetime import datetime, timedelta

    # Load the template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('sheriff_report.html')

    today = datetime.now().strftime('%Y-%m-%d')
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    # In your Python code before rendering the template:
    for game in games:
        for post in game.get('posts'):
            # Parse the datetime string into a datetime object
            if isinstance(post.get('post_datetime'), str):
                dt_obj = datetime.strptime(post.get('post_datetime'), '%Y-%m-%d %H:%M:%S')
                # Format with day of week
                post['formatted_datetime'] = dt_obj.strftime('%A, %B %d, %Y at %I:%M %p')
            else:
                # Already a datetime object
                post['formatted_datetime'] = post.post_datetime.strftime('%A, %B %d, %Y at %I:%M %p')

    # Render the template
    output_html = template.render(games=games, one_week_ago=one_week_ago, today=today)

    # if today is Monday, save the file as sheriff_report_<today>.html
    if datetime.now().weekday() == 0:  # Monday
        # Check to see if the file already exists
        sheriff_report_dir = os.path.join(script_dir, 'sheriff_reports')
        if os.path.exists(os.path.join(sheriff_report_dir,f'sheriff_report_{today}.html')):
            print('File already exists')
            today = 'snapshot'
        else:
            # If it does not exist, create it
            today = datetime.now().strftime('%Y-%m-%d')
    else:
        today = 'snapshot'
    # Save the output into file
    # Create the sheriff report directory if it doesn't exist
    sheriff_report_dir = os.path.join(script_dir, 'sheriff_reports')
    if not os.path.exists(sheriff_report_dir):
        os.makedirs(sheriff_report_dir)
    with open(os.path.join(sheriff_report_dir,f'sheriff_report_{today}.html'), 'w', encoding='utf-8') as f:
        f.write(output_html)

    return os.path.join(sheriff_report_dir,f'sheriff_report_{today}.html')

def build_sheriff_reports_landing_page():
    # Create the html for a sheriff report landing page.
    import os
    from jinja2 import Environment, FileSystemLoader
    sheriff_report_dir_name = 'sheriff_reports'

    # Load the template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('sheriff_report_landing_page.html')

    # Get list of files in the sheriff_reports directory
    sheriff_report_dir = os.path.join(script_dir, sheriff_report_dir_name)
    files = os.listdir(sheriff_report_dir)

    links = {}
    for file in files:
        if file.endswith('.html'):
            if 'snapshot' in file:
                links['Current Post Snapshot'] = file
            else:
                date_str = file.split('_')[2].split('.')[0]
                links[f'Post Report for {date_str}'] = file
            # Get the date from the filename
            date_str = file.split('_')[2].split('.')[0]
            

    # Render the template
    output_html = template.render(links=links)

    # Save the output into file
    with open(os.path.join(script_dir,'sheriff_report_landing_page.html'), 'w', encoding='utf-8') as f:
        f.write(output_html)

    return os.path.join(script_dir,'sheriff_report_landing_page.html')
    