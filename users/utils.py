import re

NETWORK_PROFILE_URL_REGEX = [
    re.compile(r'(http[s]?://)?(www\.)?gitlab\.com/(?P<username>\w+)[/]?$'),
    re.compile(r'(http[s]?://)?(www\.)?github\.com/(?P<username>\w+)[/]?$'),
    re.compile(r'(http[s]?://)?(www\.)?reddit\.com/u(ser)?/(?P<username>.*)\b[/]?$'),
    re.compile(r'^(?P<username>\w+#\w+)$'),  # Discord
    re.compile(r'(http[s]?://)?([\w.]+)?linkedin\.com/in/(?P<username>.+)$'),
    re.compile(r'(http[s]?://)twitter\.com/(?P<username>.+)$'),
    re.compile(r'(http[s]?://)plus.google\.com/\+(?P<username>\w+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)?(www\.)?facebook\.\w+/(?P<username>\w+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)vimeo\.com/(?P<username>\w+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)(www\.)?youtube\.com/channel/(?P<username>\w+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)(?P<username>\w+)\.deviantart\.com(/(\?.*)?)?'),
    re.compile(r'(http[s]?://)(www\.)?instagram\.com/(p/)?(?P<username>[\w-]+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)(www\.)?flickr\.com/photos/(?P<username>[\w@-]+)(/(\?.*)?)??$'),
    re.compile(r'(http[s]?://)(www\.)?myanimelist\.net/profile/(?P<username>[\w-]+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)(www\.)?imdb\.com/user/(?P<username>[\w-]+)(/(\?.*)?)?$')
]

NETWORK_URLS = [
    "https://gitlab.com/{}",
    "https://github.com/{}",
    "https://reddit.com/user/{}",
    "{}",  # Discord
    "https://linkedin.com/in/{}",
    "https://twitter.com/{}",
    "https://plus.google.com/+{}",
    "https://facebook.com/{}",
    "https://vimeo.com/{}",
    "https://youtube.com/channel/{}",
    "https://{}.deviantart.com/",
    "https://instagram.com/p/{}",
    "https://flickr.com/photos/{}",
    "https://myanimelist.net/profile/{}",
    "https://imdb.com/user/{}"
]


def get_network_identifier(network: int, link: str):
    if network >= len(NETWORK_PROFILE_URL_REGEX):
        raise Exception()  # TODO proper django exception
    return NETWORK_PROFILE_URL_REGEX[network].match(link).group('username')


def get_network_url(network: int, identifier: str):
    if network >= len(NETWORK_PROFILE_URL_REGEX):
        raise Exception()  # TODO proper django exception
    return NETWORK_URLS[network].format(identifier)

