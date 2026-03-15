import random

from ..constants import GROUP_TOPICS, GROUP_RATINGS
from .codeforces_api import get_problems


def recommend_problems(group, solved_problems, failed_topics, submission_count):
    """Build a list of 6 recommended problems for the user.

    Args:
        group: User skill group (A-D).
        solved_problems: Set of (contestId, index) tuples already solved.
        failed_topics: Counter of topics the user has failed on.
        submission_count: Total number of user submissions.

    Returns:
        List of up to 6 problem dicts.
    """
    problems = get_problems()
    group_topics = set(GROUP_TOPICS[group])

    # Add topics user struggles with only if there are more than 200 submissions
    if submission_count > 200:
        struggle_topics = [
            topic for topic, _ in failed_topics.most_common(3)
            if topic not in group_topics
        ]
        group_topics.update(struggle_topics[:3])

    recommended = []
    for rating, count in GROUP_RATINGS[group]:
        eligible_problems = [
            p for p in problems
            if p.get('rating') == rating
            and set(p.get('tags', [])).intersection(group_topics)
            and (p.get('contestId'), p.get('index')) not in solved_problems
        ]
        # Sort by contestId descending to prioritize recent problems
        eligible_problems.sort(key=lambda x: x.get('contestId', 0), reverse=True)
        # Take more than needed to allow for randomization
        candidates = eligible_problems[:min(count * 3, len(eligible_problems))]
        recommended.extend(random.sample(candidates, min(count, len(candidates))))

    # Ensure we have exactly 6 problems
    if len(recommended) > 6:
        recommended = random.sample(recommended, 6)
    elif len(recommended) < 6:
        additional_problems = [
            p for p in problems
            if p.get('rating') in [r for r, _ in GROUP_RATINGS[group]]
            and set(p.get('tags', [])).intersection(group_topics)
            and (p.get('contestId'), p.get('index')) not in solved_problems
            and p not in recommended
        ]
        additional_problems.sort(key=lambda x: x.get('contestId', 0), reverse=True)
        candidates = additional_problems[:min(6 * 3, len(additional_problems))]
        recommended.extend(
            random.sample(candidates, min(6 - len(recommended), len(candidates)))
        )

    return recommended[:6]
