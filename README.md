# woldtools
The Wold is a fictional world where much storytelling takes place. These tools help facilitate that storytelling.

## post_preview.html
When you post in the Wold you aren't given any way to preview your formatting choices, and there's no way to edit you post after you submit it. So this is a nice help with organizing your post before you submit it to your story.
### Features:
* Insert the common formatting tags into your post
* Insert some custom tags like **Dialog** and **OOC**
* Create your character 'Post Name' in proper format through some prompts with the **Post Name** button.

## generate_html.py
This program will download career game data from all active games in the Wold. It will format them into a json structure and output the data to your filesystem. Then it will build several websites in html using jinja and the json data.
* landing_pages.html
* game/game_id.html

## generate_emails.py
This program will analyze the career game data and look for new posts. If it finds any, it will send emails to recipients. It formats the email using jinja and json data.
