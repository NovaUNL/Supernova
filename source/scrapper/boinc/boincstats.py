import bs4
import requests
from django.core.cache import cache


def get_team_users(team_id):
    users = cache.get('boinc_team_users')
    if users is not None:
        return users

    response = requests.get(f"https://www.boincstats.com/stats/-1/user/list/0/0/{team_id}/0")
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    table = soup.find(id="tblStats")
    users = []
    for row in table.find_all('tr'):
        tds = row.find_all('td')
        if len(tds) != 12:
            continue
        _, _, _, _, username, points, daily, weekly, monthly, _, _, options = tds
        identifier = int(options.find('input', {'name': "id[]"}).attrs['value'])
        users.append({
            'identifier': identifier,
            'name': username.text,
            'points': int(float(points.text.replace(',', ''))),
            'daily': int(float(daily.text.replace(',', ''))),
            'weekly': int(float(weekly.text.replace(',', ''))),
            'monthly': int(float(monthly.text.replace(',', ''))),
        })
    cache.set('boinc_team_users', users, timeout=60 * 60 * 12)
    return users


def get_team_projects(team_id):
    projects = cache.get('boinc_team_projects')
    if projects is not None:
        return projects
    response = requests.get(f"https://www.boincstats.com/stats/-1/team/detail/{team_id}/projectList")
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    table = soup.find(id="tblStats")
    projects = []
    for row in table.find_all('tr'):
        tds = row.find_all('td')
        if len(tds) != 13:
            continue
        name, points, share, today, daily, weekly, monthly, _, _, _, _, _, _ = tds
        if name.text == 'BOINC combined':
            continue
        name = name.text
        if name == 'World Community Grid':
            name = 'WCG'
        projects.append({
            'name': name,
            'points': int(float(points.text.replace(',', ''))),
            'share': int(float(share.text.replace(',', ''))),
            'today': int(float(today.text.replace(',', ''))),
            'daily': int(float(daily.text.replace(',', ''))),
            'weekly': int(float(weekly.text.replace(',', ''))),
            'monthly': int(float(monthly.text.replace(',', ''))),
        })
    cache.set('boinc_team_projects', projects, timeout=60 * 60 * 48)
    return projects
