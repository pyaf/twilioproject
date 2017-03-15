## What this project includes

- Custom User model (inheriting AbstractUser model)
- Authy Phone Verification API for phone number verification of user.

## Installation

- Create local virtual environment.
- Set `AUTHY_KEY` in `settings.py`.
- Install all requirements by `pip install -r requirements.txt`.
- Run migration by `python manage.py migrate`.
- Run server by `python manage.py runserver`.

## Deploy on Heroku

    $ git init
    $ git add -A
    $ git commit -m "Initial commit"

    $ heroku create
    $ git push heroku master

    $ heroku run python manage.py migrate
