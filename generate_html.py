def create_landing_page(links):
    # Create wold selection landing page
    from jinja2 import Environment, FileSystemLoader
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')
    # Load the template
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('landing_page.html')

    # Render the template
    output_html = template.render(links=links)

    # Save the output into file
    with open(os.path.join(script_dir,'landing_page.html'), 'w', encoding='utf-8') as f:
        f.write(output_html)

    return None


def create_game_page(game):
    # Create the html for a dark wold game page.
    from jinja2 import Environment, FileSystemLoader
    import os
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')
    games_dir = os.path.join(script_dir, 'game')
    # Load the template
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('game.html')

    # Render the template
    output_html = template.render(game=game)

    # Save the output into file
    #json_file = os.path.join(games_dir, f'{d.get("game_id")}.html')
    with open(game.get('darkwold_file_path'), 'w', encoding='utf-8') as f:
        f.write(output_html)

    return None


def main():
    import os
    import extract_data
    extract_data.main()
    import json
    from functions import upload_file_ftps
    # Import the data
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'wold_career_games.json')
    with open(json_file, 'r') as file:
        data = json.load(file)

    links = []
    games_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'game')
    for d in data:
        d['darkwold_url'] = f'game/{d.get("game_id")}.html'
        d['darkwold_file_path'] = os.path.join(games_dir, f'{d.get("game_id")}.html')
        
        links.append({'game_id': d.get('game_id'),
                    'game_name': d.get('game_name'),
                    'game_url': d.get('game_url'),
                    'game_icon': d.get('game_icon'),
                    'darkwold_url': d.get('darkwold_url'),
                    'darkwold_file_path': d.get('darkwold_file_path')})
    # Create landing page
    create_landing_page(links)

    # Create game pages
    for game in data:
        create_game_page(game)

    # Create list of files to upload to FTP
    files = []
    files.append(('landing_page.html', '/darkwold/landing_page.html'))
    for link in links:
        files.append((link.get('darkwold_file_path'), '/darkwold/game/' + link.get('game_id') + '.html'))
        
    #for file in files:
    #    print(file)
        
    ftp_ini = os.path.join(os.path.dirname(os.path.abspath(__file__)),'ftp_settings.ini')
    import configparser
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(ftp_ini)
    ftp_user = config['settings']['user']
    ftp_password = config['settings']['pass']
    ftp_server = config['settings']['host']
    ftp_server_port = config['settings']['port']
    
    for f, d in files:
        print (f)
        print (d)
        upload_file_ftps(ftp_server, int(ftp_server_port), ftp_user, ftp_password, f, d)


if __name__ == '__main__':
    main()