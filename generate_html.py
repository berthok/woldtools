def main():
    import os
    import json
    from functions import build_wold_json_file
    from functions import create_landing_page, create_game_page
    from functions import upload_file_ftps

    # Extract data from the web into a JSON file
    build_wold_json_file()

    # Import the JSON file data
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'wold_career_games.json')
    with open(json_file, 'r') as file:
        games = json.load(file)

    # Create landing page
    create_landing_page(games)

    # Create game pages
    for game in games:
        create_game_page(game)

    # Create list of files to upload to FTP (local file, remote file)
    files = []
    files.append(('landing_page.html', '/darkwold/landing_page.html'))
    for game in games:
        files.append((game.get('darkwold_file_path'), f'/darkwold/{game.get("game_id")}.html'))

    # Load FTP Configuration
    ftp_ini = os.path.join(os.path.dirname(os.path.abspath(__file__)),'ftp_settings.ini')
    if os.path.exists(ftp_ini) == False:
        print('FTP settings file not found. Please create a file named "ftp_settings.ini" in the same directory as this script.')
    else:
        import configparser
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(ftp_ini)
        ftp_user = config['settings']['user']
        ftp_password = config['settings']['pass']
        ftp_server = config['settings']['host']
        ftp_server_port = config['settings']['port']
        
        # Upload files to FTP
        for input_file, output_file in files:
            print(f'Uploading {input_file} to {output_file}')
            upload_file_ftps(ftp_server, int(ftp_server_port), ftp_user, ftp_password, input_file, output_file)


if __name__ == '__main__':
    main()