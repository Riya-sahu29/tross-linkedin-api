"""
LinkedIn Profile API
"""
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from app.config import Settings, get_settings
from app.schemas import ErrorResponse, ProfileResponse
from app.services.apify_client import ApifyClient, ApifyRunError
from app.services.normalizer import normalize_profile
from app.utils.validators import is_valid_linkedin_profile_url

app = FastAPI(
    title="LinkedIn Profile API",
    description=(
        "Accepts a public LinkedIn profile URL and returns structured "
        "profile data as JSON. Data is sourced via a managed third-party "
        "scraping provider (Apify) — see README for why this approach "
        "was chosen."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProfileRequest(BaseModel):
    linkedin_url: str

    @field_validator("linkedin_url")
    @classmethod
    def must_be_linkedin_profile_url(cls, v: str) -> str:
        if not is_valid_linkedin_profile_url(v):
            raise ValueError(
                "linkedin_url must look like https://www.linkedin.com/in/<slug>"
            )
        return v


def verify_service_api_key(
    x_api_key: str = Header(default=""),
    settings: Settings = Depends(get_settings),
) -> None:
    if settings.SERVICE_API_KEY and x_api_key != settings.SERVICE_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing X-API-Key")


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok"}


@app.post(
    "/profile",
    response_model=ProfileResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
    tags=["profile"],
)
async def get_profile(
    payload: ProfileRequest,
    settings: Settings = Depends(get_settings),
    _: None = Depends(verify_service_api_key),
) -> ProfileResponse:
    client = ApifyClient(settings)
    try:
        raw = await client.fetch_linkedin_profile(payload.linkedin_url)
    except ApifyRunError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return normalize_profile(raw, source_url=payload.linkedin_url)