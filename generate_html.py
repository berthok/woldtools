def create_landing_page(links):
    # Create wold selection landing page
    from jinja2 import Environment, FileSystemLoader

    # Load the template
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('landing_page.html')

    # Render the template
    output_html = template.render(links=links)

    # Save the output into file
    with open('landing_page.html', 'w', encoding='utf-8') as f:
        f.write(output_html)

    return None


def create_game_page(game):
    # Create the html for a dark wold game page.
    from jinja2 import Environment, FileSystemLoader

    # Load the template
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('game.html')

    # Render the template
    output_html = template.render(game=game)

    # Save the output into file
    with open(game.get('darkwold_url'), 'w', encoding='utf-8') as f:
        f.write(output_html)

    return None


def main():
    import json
    # Import the data
    with open('wold_career_games.json', 'r') as file:
        data = json.load(file)

    links = []

    for d in data:
        d['darkwold_url'] = f'game/{d.get("game_id")}.html'
        links.append({'game_id': d.get('game_id'),
                    'game_name': d.get('game_name'),
                    'game_url': d.get('game_url'),
                    'game_icon': d.get('game_icon'),
                    'darkwold_url': d.get('darkwold_url')})
    # Create landing page
    create_landing_page(links)

    # Create game pages
    for game in data:
        create_game_page(game)


if __name__ == '__main__':
    main()