# Tako
[![Crowdin](https://badges.crowdin.net/tako/localized.svg)](https://translate.tako-bot.com)
[![Discord Server](https://img.shields.io/discord/952558753859919922?label=Discord%20Server)](https://dsc.gg/tako-server)
![latest tag](https://img.shields.io/github/v/tag/tako-discord/tako?color=sucess&label=latest%20tag&include_prereleases)
![last commit](https://img.shields.io/github/last-commit/tako-discord/tako)

A Discord bot done right. No bullshit like pay- or votewalls.

This is the rewrite for Kayano (now Tako). Before the rewrite it was written in JavaScript/Node.js with the Discord.js Library. But now it's written in Python with the discord.py Library. We have made some very great improvements and we hope you'll like it.

> **Warning** |
> This project is still in it's early days and might have a few bugs. We are trying hard to eliminate those as soon as possible.

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
    - Stable (Latest tag)
        - `REPO=https://github.com/tako-discord/tako.git && git clone $REPO --single-branch --branch $(git ls-remote --tags --refs $REPO | tail -n1 | cut -d/ -f3) -c advice.detachedHead=false`
    - Unstable/Development (Latest commit)
        - `git clone https://github.com/tako-discord/tako.git`
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

### 🔁 Updating
1. Switch to newest tag (recommended)
    - `git checkout $(git ls-remote --tags --refs $REPO | tail -n1 | cut -d/ -f3)`
2. Get latest code (unstable)
    - `git checkout master` (If you used the stable version previously)
    - `git pull`

## 🤝 Contributing
1. Fork this repository
2. Create a new branch
3. Make your changes in that branch
4.  * If you cloned your fork:
        * Run `pre-commit install --hook-type commit-msg` to install the needed pre-commit
        * Run `cz commit` to commit the changes (you need to `git add` the files first)
    * Otherwise:
        * Just follow the [Conventional Commit v1.0.0 Schema](https://www.conventionalcommits.org/en/v1.0.0/#specification)
5. Make a Pull Request
6. Be proud of yourself 👍

## 💖 Credits
**Huge thanks to**

...the core team
- 👑 [*@Pukimaa*](https://github.com/Pukimaa) - Creator & Developer
- 💻 [*@boloped*](https://github.com/boloped) - Developer

...all the testers
- [*@vaporvee*](https://github.com/vaporvee)
- [*@abUwUser*](https://github.com/abUwUser)
- [*@cmod31*](https://github.com/cmod31)
- [*@sheeepdev*](https://github.com/sheeepdev)
- [*@MeekOnGithub*](https://github.com/MeekOnGithub)
- *| Tzur |#3673*
- *Olex3#2900*

...and every other person helping. Like Contributors, Translators etc.

It's a big journey and we are happy to be on it with you!
<br /><br /><hr />
*Wow! You reached the end.*
<hr />
