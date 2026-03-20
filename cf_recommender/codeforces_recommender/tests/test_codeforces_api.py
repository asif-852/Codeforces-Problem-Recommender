from collections import Counter
from unittest.mock import patch, MagicMock

from django.test import TestCase

from codeforces_recommender.services.codeforces_api import (
    analyze_submissions,
    get_problems,
    get_user_info,
    get_user_submissions,
    PROBLEMSET_CACHE_KEY,
)


class AnalyzeSubmissionsTests(TestCase):
    """Unit tests for analyze_submissions — no mocking needed (pure function)."""

    def test_empty_submissions(self):
        solved, failed = analyze_submissions([])
        self.assertEqual(solved, set())
        self.assertEqual(failed, Counter())

    def test_single_accepted_submission(self):
        submissions = [
            {
                'verdict': 'OK',
                'problem': {
                    'contestId': 1, 'index': 'A',
                    'tags': ['math', 'greedy'],
                },
            }
        ]
        solved, failed = analyze_submissions(submissions)
        self.assertIn((1, 'A'), solved)
        self.assertEqual(failed, Counter())

    def test_single_failed_submission(self):
        submissions = [
            {
                'verdict': 'WRONG_ANSWER',
                'problem': {
                    'contestId': 2, 'index': 'B',
                    'tags': ['dp', 'graphs'],
                },
            }
        ]
        solved, failed = analyze_submissions(submissions)
        self.assertEqual(solved, set())
        self.assertEqual(failed, Counter({'dp': 1, 'graphs': 1}))

    def test_mixed_submissions(self):
        submissions = [
            {
                'verdict': 'OK',
                'problem': {'contestId': 1, 'index': 'A', 'tags': ['math']},
            },
            {
                'verdict': 'WRONG_ANSWER',
                'problem': {'contestId': 2, 'index': 'B', 'tags': ['dp']},
            },
            {
                'verdict': 'OK',
                'problem': {'contestId': 2, 'index': 'B', 'tags': ['dp']},
            },
        ]
        solved, failed = analyze_submissions(submissions)
        self.assertEqual(solved, {(1, 'A'), (2, 'B')})
        self.assertEqual(failed, Counter({'dp': 1}))

    def test_submission_without_contest_id_is_skipped(self):
        submissions = [
            {
                'verdict': 'OK',
                'problem': {'index': 'A', 'tags': ['math']},
            }
        ]
        solved, failed = analyze_submissions(submissions)
        self.assertEqual(solved, set())

    def test_submission_without_index_is_skipped(self):
        submissions = [
            {
                'verdict': 'OK',
                'problem': {'contestId': 1, 'tags': ['math']},
            }
        ]
        solved, failed = analyze_submissions(submissions)
        self.assertEqual(solved, set())

    def test_failed_submission_without_tags(self):
        submissions = [
            {
                'verdict': 'RUNTIME_ERROR',
                'problem': {'contestId': 3, 'index': 'C'},
            }
        ]
        solved, failed = analyze_submissions(submissions)
        self.assertEqual(solved, set())
        self.assertEqual(failed, Counter())


class GetUserInfoTests(TestCase):
    """Tests for get_user_info with mocked HTTP requests."""

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_successful_user_info(self, mock_get, mock_limiter):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'OK',
            'result': [{'handle': 'tourist', 'rating': 3500, 'rank': 'legendary grandmaster'}],
        }
        mock_get.return_value = mock_response

        result = get_user_info('tourist')

        self.assertEqual(result['handle'], 'tourist')
        self.assertEqual(result['rating'], 3500)
        self.assertEqual(result['group'], 'D')
        mock_get.assert_called_once()

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_user_not_found(self, mock_get, mock_limiter):
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'FAILED', 'comment': 'handles: User not found'}
        mock_get.return_value = mock_response

        result = get_user_info('nonexistent_user_xyz')

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'User not found')

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_malformed_json_response(self, mock_get, mock_limiter):
        import json
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError('err', 'doc', 0)
        mock_get.return_value = mock_response

        result = get_user_info('test_user')

        self.assertIn('error', result)
        self.assertIn('Invalid response', result['error'])

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_unrated_user_gets_group_a(self, mock_get, mock_limiter):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'OK',
            'result': [{'handle': 'newbie', 'rank': 'newbie'}],
        }
        mock_get.return_value = mock_response

        result = get_user_info('newbie')

        self.assertEqual(result['group'], 'A')


class GetUserSubmissionsTests(TestCase):
    """Tests for get_user_submissions with mocked HTTP requests."""

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_successful_fetch(self, mock_get, mock_limiter):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'OK',
            'result': [{'id': 1}, {'id': 2}],
        }
        mock_get.return_value = mock_response

        result = get_user_submissions('tourist')

        self.assertEqual(len(result), 2)

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_api_failure_returns_empty(self, mock_get, mock_limiter):
        import requests as req
        mock_get.side_effect = req.RequestException("Timeout")

        result = get_user_submissions('tourist')

        self.assertEqual(result, [])


class GetProblemsTests(TestCase):
    """Tests for get_problems with mocked HTTP and cache."""

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.cache')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_fetches_from_api_when_cache_miss(self, mock_get, mock_cache, mock_limiter):
        mock_cache.get.return_value = None
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'OK',
            'result': {'problems': [{'name': 'P1'}, {'name': 'P2'}]},
        }
        mock_get.return_value = mock_response

        result = get_problems()

        self.assertEqual(len(result), 2)
        mock_cache.set.assert_called_once()
        mock_get.assert_called_once()

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.cache')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_returns_cached_data(self, mock_get, mock_cache, mock_limiter):
        cached_problems = [{'name': 'Cached1'}, {'name': 'Cached2'}]
        mock_cache.get.return_value = cached_problems

        result = get_problems()

        self.assertEqual(result, cached_problems)
        mock_get.assert_not_called()

    @patch('codeforces_recommender.services.codeforces_api._rate_limiter')
    @patch('codeforces_recommender.services.codeforces_api.cache')
    @patch('codeforces_recommender.services.codeforces_api.requests.get')
    def test_api_failure_returns_empty(self, mock_get, mock_cache, mock_limiter):
        import requests as req
        mock_cache.get.return_value = None
        mock_get.side_effect = req.RequestException("Connection error")

        result = get_problems()

        self.assertEqual(result, [])
