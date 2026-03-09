# codeforces_recommender/views.py
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from collections import Counter
import random
import json

CODEFORCES_API_BASE_URL = 'https://codeforces.com/api/'

TOPICS = [
    '2-sat', 'binary search', 'bitmasks', 'brute force', 'chinese remainder theorem',
    'combinatorics', 'constructive algorithms', 'data structures', 'dfs and similar',
    'divide and conquer', 'dp', 'dsu', 'expression parsing', 'fft', 'flows', 'games',
    'geometry', 'graph matchings', 'graphs', 'greedy', 'hashing', 'implementation',
    'interactive', 'math', 'matrices', 'meet-in-the-middle', 'number theory',
    'probabilities', 'schedules', 'shortest paths', 'sortings', 'string suffix structures',
    'strings', 'ternary search', 'trees', 'two pointers'
]

GROUP_TOPICS = {
    'A': ['brute force', 'constructive algorithms', 'data structures', 'implementation', 'math', 'sortings', 'strings', 'two pointers', 'greedy'],
    'B': ['binary search', 'bitmasks', 'dfs and similar', 'geometry', 'graphs', 'greedy', 'interactive', 'matrices', 'ternary search', 'trees'],
    'C': ['greedy', '2-sat', 'combinatorics', 'divide and conquer', 'dp', 'dsu', 'games', 'number theory', 'probabilities', 'trees', 'graphs', 'shortest paths'],
    'D': TOPICS  # All topics for Group D
}

GROUP_RATINGS = {
    'A': [(800, 1), (900, 2), (1000, 3)],
    'B': [(1100, 1), (1200, 1), (1300, 3), (1400, 1)],
    'C': [(1300, 1), (1400, 2), (1500, 2), (1600, 1)],
    'D': [(1500, 1), (1600, 1), (1700, 2), (1800, 2)]
}

def get_user_group(rating):
    if rating < 1000:
        return 'A'
    elif 1000 <= rating < 1200:
        return 'B'
    elif 1200 <= rating < 1400:
        return 'C'
    else:
        return 'D'


def user_info(handle):
    url = f"{CODEFORCES_API_BASE_URL}user.info?handles={handle}"
    response = requests.get(url)

    # Check if response is empty or not JSON
    try:
        data = response.json()  # Attempt to parse JSON response
    except json.JSONDecodeError:
        # Handle JSON decoding error (empty or non-JSON response)
        return {'error': 'Invalid response from Codeforces API. Please try again later.'}

    if data.get('status') == 'OK':
        user_data = data['result'][0]
        user_data['group'] = get_user_group(user_data.get('rating', 0))
        return user_data

    return {'error': 'User not found'}

def get_user_submissions(handle):
    url = f"{CODEFORCES_API_BASE_URL}user.status?handle={handle}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        return data['result']
    return []

def analyze_submissions(submissions):
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

def get_problems():
    url = f"{CODEFORCES_API_BASE_URL}problemset.problems"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        return data['result']['problems']
    return []

def recommend_problems(handle, user_rating, group, solved_problems, failed_topics, submission_count):
    problems = get_problems()
    group_topics = set(GROUP_TOPICS[group])

    # Add topics user struggles with only if there are more than 200 submissions
    if submission_count > 200:
        struggle_topics = [topic for topic, _ in failed_topics.most_common(3) if topic not in group_topics]
        group_topics.update(struggle_topics[:3])

    recommended = []
    for rating, count in GROUP_RATINGS[group]:
        eligible_problems = [
            p for p in problems
            if p.get('rating') == rating
            and set(p.get('tags', [])).intersection(group_topics)
            and (p.get('contestId'), p.get('index')) not in solved_problems
        ]
        # Sort problems by contestId in descending order to get the most recent ones
        eligible_problems.sort(key=lambda x: x.get('contestId', 0), reverse=True)
        # Take more problems than needed to allow for randomization
        candidates = eligible_problems[:min(count * 3, len(eligible_problems))]
        recommended.extend(random.sample(candidates, min(count, len(candidates))))

    # Ensure we have exactly 6 problems
    if len(recommended) > 6:
        recommended = random.sample(recommended, 6)
    elif len(recommended) < 6:
        # If we have less than 6 problems, add more from the user's group
        additional_problems = [
            p for p in problems
            if p.get('rating') in [r for r, _ in GROUP_RATINGS[group]]
            and set(p.get('tags', [])).intersection(group_topics)
            and (p.get('contestId'), p.get('index')) not in solved_problems
            and p not in recommended
        ]
        additional_problems.sort(key=lambda x: x.get('contestId', 0), reverse=True)
        candidates = additional_problems[:min(6 * 3, len(additional_problems))]
        recommended.extend(random.sample(candidates, min(6 - len(recommended), len(candidates))))
        

    # Final shuffle to randomize the order
    # random.shuffle(recommended)
    # recommended.sort(key=lambda x: x.get('rating', 0))


    return recommended[:6]  # Ensure we return exactly 6 problems

@api_view(['GET'])
def recommend_problems_view(request, handle):
    # Call user_info without request
    user_data = user_info(handle)
    if 'error' in user_data:
        return Response(user_data, status=404)

    submissions = get_user_submissions(handle)
    submission_count = len(submissions)
    solved_problems, failed_topics = analyze_submissions(submissions)

    user_rating = user_data.get('rating', 0)
    group = get_user_group(user_rating)

    recommended = recommend_problems(handle, user_rating, group, solved_problems, failed_topics, submission_count)

    response_data = {
        'user_info': user_data,
        'recommended_problems': recommended,
        'important_topics': list(GROUP_TOPICS[group]),
        'struggle_topics': [topic for topic, _ in failed_topics.most_common(3)] if submission_count > 200 else []
    }

    return JsonResponse(response_data)
    

def home(request):
    return render(request, 'codeforces_recommender/home.html')
