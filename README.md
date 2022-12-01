# Tako
[![Crowdin](https://badges.crowdin.net/tako/localized.svg)](https://translate.tako.rocks)

A Discord bot done right. No bullshit like pay- or votewalls.

This is the rewrite for Kayano (now Tako). Before the rewrite it was written in JavaScript/Node.js with the Discord.js Library. But now it's written in Python with the discord.py Library. We have made some very great improvements and we hope you'll like it.

> **Warning** |
> This project is still in *beta* and might be unstable and buggy

> **Note** | We strongly recommend using [the public bot](https://top.gg/bot/878366398269771847) instead of selfhosting as it's well configured and does not have any disadvantages. Selfhosting is very complicated if you want everything to work perfectly.

## 🏃‍♂️ Get Started
> Do you need help or found a bug?
> [Open an issue](https://github.com/tako-discord/tako/issues/new)!
### 📀 What you need
- [Python](https://www.python.org/) (3.10 or higher)
- [PIP](https://pip.pypa.io/)
- [PostgreSQL](https://www.postgresql.org/) (Tested: v14-15)

Be sure to install everything before heading to the next step.
### 📥 Installation
Please note that instead of `python` your command may be `python3` or similar.
1. Clone this repository
    - `git clone https://github.com/kayano-bot/tako`
2. Install dependencies
    - `cd tako`
    - `pip install -r requirements.txt`
3. Create the database
    - [postgresql.org/docs/15/tutorial-createdb.html](https://www.postgresql.org/docs/15/tutorial-createdb.html)
4. Add Secrets
    - Create a `bot_secrets.py` inside the `tako` folder
    - Use this as a template:
    ```python
    TOKEN = "" # https://discord.com/developers/applications
    DB_NAME = "tako" # Or however you named your database
    DB_HOST = "localhost" # gonna be different if using a non-local database
    DB_PORT = 5432 # Optional port of the DB (Default: 5432)
    DB_USER = "postgres"
    DB_PASSWORD = ""
    YOUTUBE_API_KEY = "" # https://developers.google.com/youtube/v3/getting-started
    TMDB_API_KEY = "" # https://www.themoviedb.org/documentation/api
    ```
    - More info: soon™️
5. Initialize Database
    - `python helper.py` (Be sure that you are still in the `tako` folder you cloned earlier)
    - Choose "Init Database"
6. Start the bot
    - `python helper.py` and choose "Start the bot" *OR* `python main.py`
7. Sync commands
    - Inside discord run `tk!sync` (or if available: `/sync`) in a channel the bot has access to. This is to make all slash commands visible.
8. Enjoy! 😀

## 🤝 Contributing
1. Fork this repository
2. Create a new branch
3. Make your changes in that branch
4. Commit with [gitmoji](https://gitmoji.dev/) as a commit guide
5. Make a Pull Request
6. Be proud of yourself 👍

## 💖 Credits
Huge thanks to the discord.py Community, helping out if I had any question.
Another big thanks goes out to the users using this bot and all the contributors to this project.

Also huge thanks to the other (core) developer(s):
- [*@boloped*](https://github.com/boloped)
- [*LyQuid*](https://github.com/LyQuid12)

and all the testers:
- [*@abUwUser*](https://github.com/abUwUser)
- [*@cmod31*](https://github.com/cmod31)
- [*@sheeepdev*](https://github.com/sheeepdev)
- [*@MeekOnGithub*](https://github.com/MeekOnGithub)
- *| Tzur |#3673*
- *Olex3#2900*
