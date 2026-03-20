import logging
import re

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .constants import GROUP_TOPICS, HANDLE_MAX_LENGTH, HANDLE_PATTERN, get_user_group
from .services.codeforces_api import get_user_info, get_user_submissions, analyze_submissions
from .services.recommender import recommend_problems

logger = logging.getLogger(__name__)


def validate_handle(handle: str) -> str | None:
    """Validate a Codeforces handle.

    Returns None if valid, or an error message string if invalid.
    """
    if not handle or not handle.strip():
        return 'Handle cannot be empty.'
    if len(handle) > HANDLE_MAX_LENGTH:
        return f'Handle must be at most {HANDLE_MAX_LENGTH} characters.'
    if not re.match(HANDLE_PATTERN, handle):
        return 'Handle can only contain letters, digits, underscores, and hyphens.'
    return None


@api_view(['GET'])
def user_info_view(request: Request, handle: str) -> Response:
    error = validate_handle(handle)
    if error:
        logger.warning("Validation failed for handle=%r: %s", handle, error)
        return Response({'error': error}, status=400)

    user_data = get_user_info(handle)
    if 'error' in user_data:
        return Response(user_data, status=404)
    return Response(user_data)


@api_view(['GET'])
def recommend_problems_view(request: Request, handle: str) -> Response:
    error = validate_handle(handle)
    if error:
        logger.warning("Validation failed for handle=%r: %s", handle, error)
        return Response({'error': error}, status=400)

    user_data = get_user_info(handle)
    if 'error' in user_data:
        return Response(user_data, status=404)

    submissions = get_user_submissions(handle)
    submission_count = len(submissions)
    solved_problems, failed_topics = analyze_submissions(submissions)

    user_rating = user_data.get('rating', 0)
    group = get_user_group(user_rating)

    recommended = recommend_problems(group, solved_problems, failed_topics, submission_count)

    response_data = {
        'user_info': user_data,
        'recommended_problems': recommended,
        'important_topics': list(GROUP_TOPICS[group]),
        'struggle_topics': (
            [topic for topic, _ in failed_topics.most_common(3)]
            if submission_count > 200
            else []
        ),
    }

    return Response(response_data)
