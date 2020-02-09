import bs4
import requests
from django.core.cache import cache


def get_repo_stars(user='claudiop', repo='Supernova'):
    stars = cache.get('gitlab_stars')
    if stars is not None:
        return stars

    response = requests.get(f"https://gitlab.com/{user}/{repo}")
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    elem = soup.find(class_="count", title='Starrers')
    stars = int(elem.text)
    cache.set('gitlab_stars', stars, timeout=3600)
    return stars
