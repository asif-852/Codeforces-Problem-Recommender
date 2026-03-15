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
    'D': TOPICS,
}

GROUP_RATINGS = {
    'A': [(800, 1), (900, 2), (1000, 3)],
    'B': [(1100, 1), (1200, 1), (1300, 3), (1400, 1)],
    'C': [(1300, 1), (1400, 2), (1500, 2), (1600, 1)],
    'D': [(1500, 1), (1600, 1), (1700, 2), (1800, 2)],
}

# Codeforces handles: 1-24 chars, letters, digits, underscores, hyphens
HANDLE_MAX_LENGTH = 24
HANDLE_PATTERN = r'^[a-zA-Z0-9_-]+$'


def get_user_group(rating):
    """Classify a user into skill group A-D based on their rating."""
    if rating < 1000:
        return 'A'
    elif rating < 1200:
        return 'B'
    elif rating < 1400:
        return 'C'
    else:
        return 'D'
