def generate_sheriff_report():
    import os
    import json

    # Import the JSON file data
    #json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'wold_data_example.json')
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'wold_career_games.json')
    with open(json_file, 'r') as file:
        games = json.load(file)

    from functions import build_sheriff_report_page, upload_file_ftps

    report_file = build_sheriff_report_page(games)

    # Create list of files to upload to FTP (local file, remote file)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sheriff_report_dir = os.path.join(script_dir, 'sheriff_reports')
    if not os.path.exists(sheriff_report_dir):
        os.makedirs(sheriff_report_dir)
    files = [(report_file, f'/darkwold/sheriff_reports/{os.path.basename(report_file)}')]

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
        upload_to_ftp = str(config['settings']['upload_to_ftp']).lower()
        
        # Upload files to FTP
        if upload_to_ftp == 'true':
            print('Uploading files to FTP server...')
            for input_file, output_file in files:
                print(f'Uploading {input_file} to {output_file}')
                upload_file_ftps(ftp_server, int(ftp_server_port), ftp_user, ftp_password, input_file, output_file)
        else:
            print('Skipping FTP upload as per configuration.')
    
    from generate_emails import generate_sheriff_report_email
    for input_file, output_file in files:
        # Grab filename from the input file path
        filename = os.path.basename(input_file)
        # Generate the email for the sheriff report
        generate_sheriff_report_email(filename)


if __name__ == '__main__':
    generate_sheriff_report()