import json
import logging
import threading
import time
from collections import Counter
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

from ..constants import CODEFORCES_API_BASE_URL, get_user_group

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate limiter for outgoing Codeforces API requests.
# The Codeforces API allows roughly 1 request per 2 seconds for
# unauthenticated clients.  This module-level limiter is thread-safe.
# ---------------------------------------------------------------------------

class _RateLimiter:
    """Simple thread-safe rate limiter that enforces a minimum interval between calls."""

    def __init__(self, min_interval: float = 2.0) -> None:
        self._min_interval = min_interval
        self._last_call: float = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        """Block until at least ``min_interval`` seconds have passed since the last call."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self._min_interval:
                sleep_time = self._min_interval - elapsed
                logger.debug("Rate limiter: sleeping %.2fs", sleep_time)
                time.sleep(sleep_time)
            self._last_call = time.monotonic()


_rate_limiter = _RateLimiter(min_interval=2.0)


def get_user_info(handle: str) -> dict[str, Any]:
    """Fetch user profile from the Codeforces API."""
    url = f"{CODEFORCES_API_BASE_URL}user.info?handles={handle}"
    logger.info("Fetching user info for handle=%s", handle)
    _rate_limiter.wait()
    response = requests.get(url, timeout=15)

    try:
        data = response.json()
    except json.JSONDecodeError:
        logger.warning("Malformed JSON response from user.info for handle=%s", handle)
        return {'error': 'Invalid response from Codeforces API. Please try again later.'}

    if data.get('status') == 'OK':
        user_data: dict[str, Any] = data['result'][0]
        user_data['group'] = get_user_group(user_data.get('rating', 0))
        logger.info(
            "User info fetched: handle=%s, rating=%s, group=%s",
            handle, user_data.get('rating', 'N/A'), user_data['group'],
        )
        return user_data

    logger.warning("User not found: handle=%s", handle)
    return {'error': 'User not found'}


def get_user_submissions(handle: str) -> list[dict[str, Any]]:
    """Fetch all submissions for a user from the Codeforces API."""
    url = f"{CODEFORCES_API_BASE_URL}user.status?handle={handle}"
    logger.info("Fetching submissions for handle=%s", handle)
    try:
        _rate_limiter.wait()
        response = requests.get(url, timeout=15)
        data = response.json()
        if data.get('status') == 'OK':
            submissions = data['result']
            logger.info("Fetched %d submissions for handle=%s", len(submissions), handle)
            return submissions
    except (requests.RequestException, json.JSONDecodeError, KeyError) as exc:
        logger.error("Failed to fetch submissions for handle=%s: %s", handle, exc)
    return []


PROBLEMSET_CACHE_KEY = "codeforces_problemset"


def get_problems() -> list[dict[str, Any]]:
    """Fetch the full Codeforces problem set, using a cache to avoid repeated API calls."""
    cached = cache.get(PROBLEMSET_CACHE_KEY)
    if cached is not None:
        logger.info("Returning cached problem set (%d problems)", len(cached))
        return cached

    url = f"{CODEFORCES_API_BASE_URL}problemset.problems"
    logger.info("Fetching Codeforces problem set from API")
    try:
        _rate_limiter.wait()
        response = requests.get(url, timeout=15)
        data = response.json()
        if data.get('status') == 'OK':
            problems = data['result']['problems']
            cache.set(
                PROBLEMSET_CACHE_KEY,
                problems,
                timeout=settings.PROBLEMSET_CACHE_TTL,
            )
            logger.info("Fetched and cached %d problems from Codeforces", len(problems))
            return problems
    except (requests.RequestException, json.JSONDecodeError, KeyError) as exc:
        logger.error("Failed to fetch problem set: %s", exc)
    return []


def analyze_submissions(
    submissions: list[dict[str, Any]],
) -> tuple[set[tuple[int, str]], Counter[str]]:
    """Analyze submissions to find solved problems and failed topic counts.

    Returns:
        tuple: (solved_problems set, failed_topics Counter)
    """
    solved_problems: set[tuple[int, str]] = set()
    failed_topics: Counter[str] = Counter()

    for submission in submissions:
        problem = submission['problem']
        if 'contestId' in problem and 'index' in problem:
            if submission['verdict'] == 'OK':
                solved_problems.add((problem['contestId'], problem['index']))
            else:
                failed_topics.update(problem.get('tags', []))

    logger.info(
        "Submission analysis: %d solved problems, %d unique failed topics",
        len(solved_problems), len(failed_topics),
    )
    return solved_problems, failed_topics
