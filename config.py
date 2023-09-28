# * Defaults
DEFAULT_COLOR = 0x4ADE80
DELETE_THUMBNAILS = True
DEFAULT_COLOR_STR = "0x4ADE80"
# Used if not logged in
DEFAULT_BOT_NAME = "Tako#5528"

# * Roles for badges and checks (Use None to remove)
MAIN_GUILD = 952558753859919922
DONATOR_ROLE = 969286409200468028
TRANSLATOR_ROLE = 980904580286140426
ALPHA_TESTER_ROLE = 969306314981376071
DEV_ROLE = 969285824107642990
SURVEY_ROLES = [1026487071625457754, 1062067399395913808]  # currently unused

# * Economy
CURRENCY = " <:TK:1025679113777848320>"  # we will allow custom currencies in the future
DEFAULT_BANK = 0
DEFAULT_WALLET = 1000

# * APIs etc.
TRANSLATE_API = "https://tl.tako-bot.com"  # no / at the end is important
TRANSLATE_API_FALLBACK = "https://lingva.ml"  # no / at the end is important
IMGEN = "https://imgen.tako-bot.com"  # no / at the end is important
REPO = "tako-discord/tako"
RAW_GH = "https://raw.githubusercontent.com/"  # Used for version check (pyproject.toml)
OC_WEBHOOK_CHANNEL_ID = 1084813618685677659  # used by the Open Collective Integration

# Regex used for valid sources on the emoji command ("^https?:\/example[].]org\/"" recommended, seperate with "|")
# ! If removed people can enter every url even non-image ones (viruses etc.).
ALLOWED_SOURCES = "^https?:\/\/cdn3[.]emoji[.]gg\/|^https:\/\/cdn[.]discordapp[.]com\/|^https?:\/\/i[.]imgur[.]com\/|^https?:\/\/raw[.]githubusercontent[.]com\/"

# * Social Media (optional and removable)
EMOJI_YT = "<:youtube:991732817585242112>"  # optional
EMOJI_TWITTER = "<:twitter:991732692905377794>"  # optional
TWITTER_LINK = "https://twitter.com/DiscordTako"  # optional
YOUTUBE_LINK = "https://youtube.com/channel/UCRFUsdQIfinsdiKhLUs7ZFQ"  # optional

# * Emojis (<[a if animated]:[emoji_name]:[emoji_id]>)
EMOJI_ALPHA_TESTER = "🧪"
EMOJI_DONATOR = "💖"
EMOJI_TRANSLATOR = "🌐"
EMOJI_DEV = "💻"
EMOJI_START_BAR = "<:start:1051545120459194469>"
EMOJI_START_BAR_FULL = "<:start_full:1051545121855901757>"
EMOJI_MIDDLE_BAR = "<:middle:1051545111957344276>"
EMOJI_MIDDLE_BAR_FULL = "<:middle_full:1051545113991598192>"
EMOJI_END_BAR = "<:end:1051545107788218368>"
EMOJI_END_BAR_FULL = "<:end_full:1051545109784690810>"
EMOJI_UPVOTE = "<:upvote:1080473415909117972>"
EMOJI_CHECKMARK = "<:checkmark:1080545976839848048>"
EMOJI_CROSS = "<:cross:1080545978949566484>"
EMOJI_INFO = "<:info:1080849011159871488>"
EMOJI_ARROW_FIRST = "<:arrowFirst:1080837380182908999>"
EMOJI_ARROW_LEFT = "<:arrowLeft:1080837384305909801>"
EMOJI_ARROW_RIGHT = "<:arrowRight:1080837372201148457>"
EMOJI_ARROW_LAST = "<:arrowLast:1080837382179401808>"

# Currently unused
ANTI_PHISHING_LIST = [
    "https://raw.githubusercontent.com/tako-discord/discord-phishing-links/main/domain-list.json",
    "https://raw.githubusercontent.com/tako-discord/discord-phishing-links/main/suspicious-list.json",
]
