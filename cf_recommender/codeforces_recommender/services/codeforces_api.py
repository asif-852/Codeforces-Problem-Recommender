import requests
import json
from collections import Counter

from ..constants import CODEFORCES_API_BASE_URL, get_user_group


def get_user_info(handle):
    """Fetch user profile from the Codeforces API."""
    url = f"{CODEFORCES_API_BASE_URL}user.info?handles={handle}"
    response = requests.get(url, timeout=15)

    try:
        data = response.json()
    except json.JSONDecodeError:
        return {'error': 'Invalid response from Codeforces API. Please try again later.'}

    if data.get('status') == 'OK':
        user_data = data['result'][0]
        user_data['group'] = get_user_group(user_data.get('rating', 0))
        return user_data

    return {'error': 'User not found'}


def get_user_submissions(handle):
    """Fetch all submissions for a user from the Codeforces API."""
    url = f"{CODEFORCES_API_BASE_URL}user.status?handle={handle}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if data.get('status') == 'OK':
            return data['result']
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        pass
    return []


def get_problems():
    """Fetch the full Codeforces problem set."""
    url = f"{CODEFORCES_API_BASE_URL}problemset.problems"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if data.get('status') == 'OK':
            return data['result']['problems']
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        pass
    return []


def analyze_submissions(submissions):
    """Analyze submissions to find solved problems and failed topic counts.

    Returns:
        tuple: (solved_problems set, failed_topics Counter)
    """
    solved_problems = set()
    failed_topics = Counter()

    for submission in submissions:
        problem = submission['problem']
        if 'contestId' in problem and 'index' in problem:
            if submission['verdict'] == 'OK':
                solved_problems.add((problem['contestId'], problem['index']))
            else:
                failed_topics.update(problem.get('tags', []))

    return solved_problems, failed_topics
