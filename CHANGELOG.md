## 1.14.0 (2023-09-28)

### Feat

- **info**: add `/animal` command

### Fix

- **info/animal**: hotfixes

### Refactor

- **i18n**: added danish and turkish
- **config**: use lingva.ml as main api and tl.tako-bot.com as fallback (faster now)

## 1.13.0 (2023-03-19)

### Feat

- **errors**: use user locale instead of guild locale and timestamp for cooldown
- **youtube**: add error if no search results were found
- add `/daily`
- add `/beg`
- **helper**: use sql files to initialize the database (and migrate)
- **info/stats**: let the `/stats` commmand be run in non-guild conversations and when the bot is not logged in yet

### Fix

- **helper**: fix issues with db init

### Refactor

- **daily**: use database to check the cooldown

## 1.12.1 (2023-03-18)

### Fix

- **random**: don't mention when choosing something random

## 1.12.0 (2023-03-18)

### Feat

- add `/random choose`
- **opencollective**: sync opencollective metadata every 12h
- add warn system

### Fix

- **anti-phishing**: use regex now...finally discord.gift won't be blocked lmao
- **warn**: limit amount of characters for the reason of a warn

### Refactor

- **translator**: remove debug print statement
- **license**: MIT -> custom license based on MIT
- **warnings**: sort warnings by date descending (latest is shown first)
- **i18n/group_name**: add all group names
- **anti-phishing**: temporarily remove the AntiPhishing cog
- **TakoBot**: move TakoBot class from `TakoBot.py` to `main.py`
- **utils**: better typing
- remove `OLD_CHANGELOG.md`
- **permissions**: change permissions from checks to default permissions
- **config**: use tl.tako-bot.com as main translation api

## 1.11.0 (2023-02-28)

### Feat

- switch to new translation api (lingva-translate)

### Fix

- **affirmation**: fix affirmations not responding

### Refactor

- **reddit**: remove request timeout
- **main**: remove presence intent (not needed)

## 1.10.0 (2023-02-25)

### Feat

- add `/reddit` command
- **ip**: add `/ip` command

### Fix

- **config**: forgot to save __init__.py that removes the import :skull:
- **TakoBot**: fix presence not updating

### Refactor

- **rpc**: better rpc
- **uwuify**: add descriptions for fields and use percentage from 0-100 instead of 0-1
- move language related features into seperate folder

## 1.9.0 (2023-02-11)

### Feat

- **TakoBot**: use sharded bot

### Fix

- better sharding
- **polls**: fix polls changing the question answer
- change language associated with belgium flag (#20)

### Perf

- **polls**: delete poll from db when stopped

## 1.8.0 (2023-02-03)

### Feat

- **polls**: add ability to stop polls
- **languages**: add Japanese (3%) and Tagalog (5%)
- **uwu**: add uwuify command

### Fix

- **uwuify**: defer response
- hotfix presence update

## 1.7.2 (2023-02-02)

### Fix

- **autojoinroles**: fix permission check when owner
- **auto_translate**: hotfix default style not working

### Refactor

- **topic**: better warning if index out of range

### Perf

- improve startup time

## 1.7.1 (2023-01-31)

### Fix

- **auto_translate**: fix translation not being send inside thread if the original message was inside a thread
- **i18n**: updated German (#17)

### Refactor

- **topic**: update topics, add warning if invalid topic id
- **ban_game**: remove `ban_game` command

## 1.7.0 (2023-01-30)

### Feat

- **auto_react**: add maximum emojis to add (due to Discord Limitation)

### Fix

- **meme**: use new api url

### Perf

- **utils**: improve translation function

## 1.6.0 (2023-01-24)

### Feat

- add auto_react

### Fix

- **i18n**: new crowdin updates
- **utils**: make guild id in error_embed optional
- fix exit code in workflow
- **config**: fix ruff linter
- **autotranslate**: fix no webhook token error

## 1.5.0 (2023-01-07)

### Feat

- **moderation**: add slowmode command
- **economy**: remove gambling
- **topics**: add all topics
- **utils**: addtranslation api fallback

### Fix

- **utils**: fix translate function

## 1.4.1 (2023-01-04)

### Fix

- **i18n**: updated German, Hebrew

## 1.4.0 (2023-01-04)

### Feat

- **cz**: update changelog on bump
- add pre-commit for conventional commit messages

### Fix

- **cogs/config**: fix import error
- **utils**: filatest version not being converted correctly
- **cz**: use correct start revision
- **cz**: add changelog start revision

## 1.3.1 (2023-01-04)

### Feat

- add pre-commit for conventional commit messages

### Fix

- **cz**: use correct start revision
- **cz**: add changelog start revision
