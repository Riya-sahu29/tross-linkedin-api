
from typing import Any, Dict, List, Optional

import httpx

from app.config import Settings

APIFY_BASE_URL = "https://api.apify.com/v2"


class ApifyRunError(Exception):
    """Raised when the Apify actor run fails or returns no data."""


class ApifyClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    async def fetch_linkedin_profile(self, profile_url: str) -> Dict[str, Any]:
        actor_id = self._settings.APIFY_ACTOR_ID
        url = f"{APIFY_BASE_URL}/acts/{actor_id}/run-sync-get-dataset-items"

        params = {"token": self._settings.APIFY_API_TOKEN}
        payload = {"urls": [{"url": profile_url}]}

        timeout = httpx.Timeout(self._settings.APIFY_RUN_TIMEOUT_SECS)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, params=params, json=payload)
            except httpx.TimeoutException as exc:
                raise ApifyRunError(
                    f"Apify actor run timed out after {self._settings.APIFY_RUN_TIMEOUT_SECS}s"
                ) from exc

        if response.status_code == 401:
            raise ApifyRunError("Apify authentication failed — check APIFY_API_TOKEN.")
        if response.status_code >= 400:
            raise ApifyRunError(
                f"Apify actor run failed with status {response.status_code}: {response.text[:500]}"
            )

        items: Optional[List[Dict[str, Any]]] = response.json()
        if not items:
            raise ApifyRunError(
                "No data returned for this profile. It may be private, "
                "deleted, or blocked by LinkedIn's anti-scraping measures."
            )

        return items[0]