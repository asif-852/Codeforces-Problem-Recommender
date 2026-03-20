from collections import Counter
from unittest.mock import patch

from django.test import TestCase

from codeforces_recommender.services.recommender import recommend_problems


def _make_problem(contest_id, index, rating, tags):
    """Helper to create a problem dict matching the Codeforces API shape."""
    return {
        'contestId': contest_id,
        'index': index,
        'name': f'Problem {contest_id}{index}',
        'rating': rating,
        'tags': tags,
    }


# A small, deterministic problem set used across tests.
MOCK_PROBLEMS = [
    _make_problem(100, 'A', 800, ['math', 'implementation']),
    _make_problem(101, 'A', 800, ['brute force', 'strings']),
    _make_problem(102, 'A', 900, ['greedy', 'sortings']),
    _make_problem(103, 'A', 900, ['math', 'greedy']),
    _make_problem(104, 'B', 900, ['implementation']),
    _make_problem(105, 'A', 1000, ['data structures', 'math']),
    _make_problem(106, 'B', 1000, ['two pointers', 'strings']),
    _make_problem(107, 'C', 1000, ['greedy', 'implementation']),
    _make_problem(108, 'A', 1100, ['binary search', 'graphs']),
    _make_problem(109, 'B', 1300, ['dp', 'greedy']),
    _make_problem(110, 'A', 1300, ['combinatorics', 'dp']),
    _make_problem(111, 'A', 1500, ['dp', 'graphs']),
    _make_problem(112, 'B', 1700, ['number theory', 'math']),
]


@patch(
    'codeforces_recommender.services.recommender.get_problems',
    return_value=MOCK_PROBLEMS,
)
class RecommendProblemsTests(TestCase):
    """Tests for the recommend_problems function with a mocked problem set."""

    def test_group_a_returns_up_to_6_problems(self, _mock_get):
        result = recommend_problems('A', set(), Counter(), 0)
        self.assertLessEqual(len(result), 6)
        self.assertGreater(len(result), 0)

    def test_group_a_respects_rating_range(self, _mock_get):
        result = recommend_problems('A', set(), Counter(), 0)
        for problem in result:
            self.assertIn(problem['rating'], [800, 900, 1000])

    def test_excludes_solved_problems(self, _mock_get):
        solved = {(100, 'A'), (101, 'A')}
        result = recommend_problems('A', solved, Counter(), 0)
        for problem in result:
            key = (problem['contestId'], problem['index'])
            self.assertNotIn(key, solved)

    def test_returns_problems_matching_group_topics(self, _mock_get):
        from codeforces_recommender.constants import GROUP_TOPICS
        result = recommend_problems('A', set(), Counter(), 0)
        group_topics_set = set(GROUP_TOPICS['A'])
        for problem in result:
            self.assertTrue(
                set(problem['tags']).intersection(group_topics_set),
                f"Problem {problem['name']} tags {problem['tags']} don't overlap with group A topics",
            )

    def test_struggle_topics_ignored_below_200_submissions(self, _mock_get):
        """With < 200 submissions, struggle topics should NOT expand the topic set."""
        failed = Counter({'dp': 10, 'graphs': 8, 'number theory': 5})
        result = recommend_problems('A', set(), failed, 100)
        # DP is not in Group A topics, so dp-only problems shouldn't appear
        for problem in result:
            # A problem that ONLY has non-group-A tags shouldn't be included
            from codeforces_recommender.constants import GROUP_TOPICS
            self.assertTrue(
                set(problem['tags']).intersection(set(GROUP_TOPICS['A'])),
            )

    def test_struggle_topics_added_above_200_submissions(self, _mock_get):
        """With > 200 submissions, the top struggle topics should be factored in."""
        # 'dp' is NOT in Group A topics, so if it gets added via struggle topics
        # then dp problems could appear in the results
        failed = Counter({'dp': 50, 'graphs': 30, 'number theory': 20})
        result = recommend_problems('A', set(), failed, 250)
        # We can't guarantee dp problems appear (depends on rating match),
        # but the function should not crash
        self.assertLessEqual(len(result), 6)

    def test_empty_problem_set_returns_empty(self, _mock_get):
        _mock_get.return_value = []
        result = recommend_problems('A', set(), Counter(), 0)
        self.assertEqual(result, [])

    def test_all_problems_solved_returns_empty(self, _mock_get):
        solved = {(p['contestId'], p['index']) for p in MOCK_PROBLEMS}
        result = recommend_problems('A', solved, Counter(), 0)
        self.assertEqual(result, [])
