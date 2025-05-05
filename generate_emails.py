def load_json_config(config_file):
    import json
    with open(config_file, 'r') as file:
        return json.load(file)


def write_json_config(config_file, data):
    import json
    with open(config_file, 'w') as file:
        json.dump(data, file, indent=4, default=str)


def send_email(sender_email, sender_password, smtp_server, smtp_port, recipient_list, subject, body):
    import smtplib
    import ssl
    #from email.message import EmailMessage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    #msg = EmailMessage()
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, sender_password)
            # Recipient list is entered here in the sendmail function
            server.sendmail(sender_email, recipient_list, msg.as_string())
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def create_email_body(game, most_recent_email_datetime):
    import os
    from jinja2 import Environment, FileSystemLoader
    # Load the template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('email_body_new_posts.html')

    # Render the template
    body = template.render(game=game)

    return body


def generate_emails():
    import os
    from datetime import datetime
    # Load configuration files
    if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),'email_config.json')):
        email_configuration = load_json_config(os.path.join(os.path.dirname(os.path.abspath(__file__)),'email_config.json'))
    else:
        print('No email_config.json file found. Not able to run this function.')
        return None
    
    # Load game data
    if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),'wold_career_games.json')):
        wold_career_games = load_json_config(os.path.join(os.path.dirname(os.path.abspath(__file__)),'wold_career_games.json'))
    else:
        print('No wold_career_games.json file found. Not able to run this function.')
        return None

    # Check most_recent_post_datetime for each game against the most_recent_post_datetime in the email_configuration
    for game in wold_career_games:
        print(f"Checking {game['game_id']}")
        # Check to make sure the game exists in the email_configuration
        if game['game_id'] not in email_configuration:
            email_configuration[game['game_id']] = {'most_recent_post_datetime': '1900-01-01 00:00:00',
                                                    'last_email_sent_datetime': '1900-01-01 00:00:00',
                                                    'recipients': [],
                                                    'game_enabled': 0}
        if email_configuration[game['game_id']].get('game_enabled') == 0:
            print(f" - Game {game['game_id']} is disabled. Skipping email.")
            continue
        if game['most_recent_post_datetime'] > email_configuration[game['game_id']]['most_recent_post_datetime']:
            # Create recipient list
            recipient_list = list(set(email_configuration[game['game_id']]['recipients'] + 
                                      email_configuration['admin']['recipients']))
            if recipient_list == []:
                print(f" - No recipients for {game['game_id']}. Skipping email.")
            else:
                # Create email subject
                subject = f"{game['game_name']} - New Posts - ({game.get('most_recent_post_datetime')})"
                # Create email body
                body = create_email_body(game, email_configuration[game['game_id']]['most_recent_post_datetime'])
                # Send an email
                print(f" - Sending email for [{game['game_id']}]")
                server_config = email_configuration['server_config']

                # Wait 2 seconds before sending email
                # Otherwise the smtp server thinks we are spamming
                import time
                time.sleep(2)
                send_email(sender_email=server_config['sender_email'],
                        sender_password=server_config['sender_password'],
                        smtp_server=server_config['smtp_server'],
                        smtp_port=int(server_config['smtp_port']),
                        recipient_list=recipient_list,
                        subject=subject,
                        body=body)
                # Update most_recent_post_datetime in email_configuration
                email_configuration[game['game_id']]['most_recent_post_datetime'] = game['most_recent_post_datetime']
                # Update last_email_sent_datetime in email_configuration
                email_configuration[game['game_id']]['last_email_sent_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            print(f"No new posts for [{game['game_id']}]. Skipping email.")

    # Write Email Configuration Data
    write_json_config(os.path.join(os.path.dirname(os.path.abspath(__file__)),'email_config.json'), email_configuration)

def generate_sheriff_report_email(report_file_name):
    # Generate the email for the sheriff report
    import os
    from datetime import datetime, timedelta
    # Load configuration files
    if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),'email_config.json')):
        email_configuration = load_json_config(os.path.join(os.path.dirname(os.path.abspath(__file__)),'email_config.json'))
    else:
        print('No email_config.json file found. Not able to run this function.')
        return None
    if 'sheriff' not in email_configuration:
        print('No sheriff configuration found. Not able to run this function.')
        return None
    
    # Load game data
    if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),'wold_career_games.json')):
        games = load_json_config(os.path.join(os.path.dirname(os.path.abspath(__file__)),'wold_career_games.json'))
    else:
        print('No wold_career_games.json file found. Not able to run this function.')
        return None
    
    # Check the last run datetime for the sheriff report. If today is a Monday and the last run date is not today, send the email.
    if datetime.now().strftime('%A') == 'Monday':
        if email_configuration['sheriff']['last_email_sent_date'] != datetime.now().strftime('%Y-%m-%d'):
            # Create recipient list
            recipient_list = list(set(email_configuration['sheriff']['recipients'] + 
                                      email_configuration['admin']['recipients']))
            if recipient_list == []:
                print(f" - No recipients for sheriff report. Skipping email.")
            else:
                # Create email subject
                subject = f"Wold Sheriff Report - ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"

                # Load the template to create the email body
                from jinja2 import Environment, FileSystemLoader
                script_dir = os.path.dirname(os.path.abspath(__file__))
                template_dir = os.path.join(script_dir, 'templates')
                env = Environment(loader=FileSystemLoader(template_dir))
                template = env.get_template('email_body_sheriff_report.html')

                # Create email body
                if 'snapshot' in report_file_name:
                    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                    yesterday_report_file_name = report_file_name.replace('snapshot', yesterday_date)
                    body = template.render(games=games, report_file_name=yesterday_report_file_name)
                else:
                    body = template.render(games=games, report_file_name=report_file_name)
               
                # Send an email
                print(f" - Sending sheriff report email")
                server_config = email_configuration['server_config']

                # Wait 2 seconds before sending email
                # Otherwise the smtp server thinks we are spamming
                import time
                time.sleep(2)
                send_email(sender_email=server_config['sender_email'],
                        sender_password=server_config['sender_password'],
                        smtp_server=server_config['smtp_server'],
                        smtp_port=int(server_config['smtp_port']),
                        recipient_list=recipient_list,
                        subject=subject,
                        body=body)
                
                # Update last_email_sent_datetime in email_configuration
                email_configuration['sheriff']['last_email_sent_date'] = datetime.now().strftime('%Y-%m-%d')

                # Write Email Configuration Data
                write_json_config(os.path.join(os.path.dirname(os.path.abspath(__file__)),'email_config.json'), email_configuration)
        else:
            print(f" - Sheriff report email already sent today. Skipping email.")
    else:
        print(f"Today is not Monday. Skipping sheriff report email.")
    
    
    email_configuration['sheriff']['last_email_sent_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    generate_emails()

if __name__ == '__main__':
    main()