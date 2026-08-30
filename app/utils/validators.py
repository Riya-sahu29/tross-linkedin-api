import re
from urllib.parse import urlparse

_LINKEDIN_PROFILE_PATTERN = re.compile(
    r"^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?$"
)


def is_valid_linkedin_profile_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    return bool(_LINKEDIN_PROFILE_PATTERN.match(url.strip()))