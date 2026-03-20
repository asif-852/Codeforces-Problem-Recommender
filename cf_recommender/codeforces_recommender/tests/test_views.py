from collections import Counter
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class ValidateHandleViewTests(TestCase):
    """Integration tests for input validation on both API endpoints."""

    def setUp(self):
        self.client = APIClient()

    def test_user_info_empty_handle(self):
        response = self.client.get('/api/user/ /')
        self.assertEqual(response.status_code, 400)

    def test_user_info_handle_too_long(self):
        long_handle = 'a' * 25
        response = self.client.get(f'/api/user/{long_handle}/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('at most', response.data['error'])

    def test_recommend_invalid_chars(self):
        response = self.client.get('/api/recommend/bad handle!/')
        # Django URL routing may not match this, which is fine (404)
        self.assertIn(response.status_code, [400, 404])


class UserInfoViewTests(TestCase):
    """Integration tests for /api/user/<handle>/."""

    def setUp(self):
        self.client = APIClient()

    @patch('codeforces_recommender.views.get_user_info')
    def test_successful_response(self, mock_get_user_info):
        mock_get_user_info.return_value = {
            'handle': 'tourist',
            'rating': 3500,
            'rank': 'legendary grandmaster',
            'group': 'D',
        }
        response = self.client.get('/api/user/tourist/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['handle'], 'tourist')
        self.assertEqual(response.data['rating'], 3500)

    @patch('codeforces_recommender.views.get_user_info')
    def test_user_not_found_returns_404(self, mock_get_user_info):
        mock_get_user_info.return_value = {'error': 'User not found'}
        response = self.client.get('/api/user/nonexistent/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)


class RecommendViewTests(TestCase):
    """Integration tests for /api/recommend/<handle>/."""

    def setUp(self):
        self.client = APIClient()

    @patch('codeforces_recommender.views.recommend_problems')
    @patch('codeforces_recommender.views.analyze_submissions')
    @patch('codeforces_recommender.views.get_user_submissions')
    @patch('codeforces_recommender.views.get_user_info')
    def test_successful_recommendation(
        self, mock_user_info, mock_submissions, mock_analyze, mock_recommend,
    ):
        mock_user_info.return_value = {
            'handle': 'test_user',
            'rating': 1100,
            'rank': 'pupil',
            'group': 'B',
        }
        mock_submissions.return_value = [{'id': 1}, {'id': 2}]
        mock_analyze.return_value = (set(), Counter())
        mock_recommend.return_value = [
            {'contestId': 100, 'index': 'A', 'name': 'Test Problem', 'rating': 1100, 'tags': ['math']},
        ]

        response = self.client.get('/api/recommend/test_user/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('user_info', response.data)
        self.assertIn('recommended_problems', response.data)
        self.assertIn('important_topics', response.data)
        self.assertIn('struggle_topics', response.data)
        self.assertEqual(response.data['user_info']['handle'], 'test_user')
        self.assertEqual(len(response.data['recommended_problems']), 1)

    @patch('codeforces_recommender.views.get_user_info')
    def test_user_not_found_returns_404(self, mock_user_info):
        mock_user_info.return_value = {'error': 'User not found'}
        response = self.client.get('/api/recommend/nonexistent/')
        self.assertEqual(response.status_code, 404)

    @patch('codeforces_recommender.views.recommend_problems')
    @patch('codeforces_recommender.views.analyze_submissions')
    @patch('codeforces_recommender.views.get_user_submissions')
    @patch('codeforces_recommender.views.get_user_info')
    def test_struggle_topics_included_for_experienced_user(
        self, mock_user_info, mock_submissions, mock_analyze, mock_recommend,
    ):
        mock_user_info.return_value = {
            'handle': 'experienced',
            'rating': 1500,
            'rank': 'specialist',
            'group': 'D',
        }
        # 201 submissions to trigger struggle topic detection
        mock_submissions.return_value = [{'id': i} for i in range(201)]
        mock_analyze.return_value = (
            set(),
            Counter({'dp': 50, 'graphs': 30, 'math': 20}),
        )
        mock_recommend.return_value = []

        response = self.client.get('/api/recommend/experienced/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['struggle_topics']), 3)
        self.assertEqual(response.data['struggle_topics'][0], 'dp')

    @patch('codeforces_recommender.views.recommend_problems')
    @patch('codeforces_recommender.views.analyze_submissions')
    @patch('codeforces_recommender.views.get_user_submissions')
    @patch('codeforces_recommender.views.get_user_info')
    def test_no_struggle_topics_for_new_user(
        self, mock_user_info, mock_submissions, mock_analyze, mock_recommend,
    ):
        mock_user_info.return_value = {
            'handle': 'newbie',
            'rating': 800,
            'rank': 'newbie',
            'group': 'A',
        }
        mock_submissions.return_value = [{'id': i} for i in range(50)]
        mock_analyze.return_value = (
            set(),
            Counter({'math': 10, 'dp': 5}),
        )
        mock_recommend.return_value = []

        response = self.client.get('/api/recommend/newbie/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['struggle_topics'], [])
