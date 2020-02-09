import json

import requests
from django.core.cache import cache


def get_repo_stars(user='claudioap', repo='Supernova'):
    stars = cache.get('github_stars')
    if stars is not None:
        return stars

    response = requests.get(f"https://api.github.com/repos/{user}/{repo}")
    result = json.loads(response.text)
    stars = result['stargazers_count']
    cache.set('github_stars', stars, timeout=3600)
    return stars