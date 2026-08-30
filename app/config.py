
"""
Application configuration, loaded from environment variables.
"""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")
    APIFY_ACTOR_ID: str = os.getenv("APIFY_ACTOR_ID", "supreme_coder~linkedin-profile-scraper")
    APIFY_RUN_TIMEOUT_SECS: int = int(os.getenv("APIFY_RUN_TIMEOUT_SECS", "90"))
    SERVICE_API_KEY: str = os.getenv("SERVICE_API_KEY", "")

    def validate(self) -> None:
        if not self.APIFY_API_TOKEN:
            raise RuntimeError(
                "APIFY_API_TOKEN is not set. Add it to your environment "
                "or a local .env file (see .env.example)."
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings