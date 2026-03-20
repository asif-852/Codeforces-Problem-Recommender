from django.test import TestCase

from codeforces_recommender.constants import get_user_group


class GetUserGroupTests(TestCase):
    """Test the get_user_group function at all boundary values."""

    def test_rating_zero_returns_group_a(self):
        self.assertEqual(get_user_group(0), 'A')

    def test_rating_999_returns_group_a(self):
        self.assertEqual(get_user_group(999), 'A')

    def test_rating_1000_returns_group_b(self):
        self.assertEqual(get_user_group(1000), 'B')

    def test_rating_1199_returns_group_b(self):
        self.assertEqual(get_user_group(1199), 'B')

    def test_rating_1200_returns_group_c(self):
        self.assertEqual(get_user_group(1200), 'C')

    def test_rating_1399_returns_group_c(self):
        self.assertEqual(get_user_group(1399), 'C')

    def test_rating_1400_returns_group_d(self):
        self.assertEqual(get_user_group(1400), 'D')

    def test_rating_2000_returns_group_d(self):
        self.assertEqual(get_user_group(2000), 'D')

    def test_negative_rating_returns_group_a(self):
        self.assertEqual(get_user_group(-100), 'A')
