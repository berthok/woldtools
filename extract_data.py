from functions import fetch_career_games, fetch_career_game_data
from functions import isolate_posts_from_raw_data, parse_headers_from_posts
from functions import clean_posts
from functions import parse_header_information, extract_and_parse_datetime
from functions import export_data_to_file
import colorama
from colorama import Fore

def main():
    colorama.init()
    # Gather up a list of all current games
    career_games = fetch_career_games()

    print('Loading Data for Career Games...')

    for game in career_games:
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
                                                                          'url': post.get('header_urls')[0].get('url'),
                                                                          'hp': post.get('hp'),
                                                                          'ac': post.get('ac'),
                                                                          'pp': post.get('pp')}
                    else:
                        game['characters'][post.get('character_name')] = {'name': post.get('character_name'),
                                                                          'url': None,
                                                                          'hp': post.get('hp'),
                                                                          'ac': post.get('ac'),
                                                                          'pp': post.get('pp')}
        #game['characters'] = sorted(list(set(game.get('characters'))))
        #game.get('characters').remove('DM')
        game['characters'] = dict(sorted(game.get('characters').items()))

        print('          - Found these characters...')
        for character in game.get('characters'):
            print(f'             - {character}')

    print('Exporting Data to JSON...')
    export_data_to_file(career_games)
    print('Done!')

    colorama.deinit()


if __name__ == "__main__":
    main()
