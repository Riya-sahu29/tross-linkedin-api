"""
Maps raw output from the supreme_coder/linkedin-profile-scraper Apify
actor into the stable ProfileResponse schema.
"""
from typing import Any, Dict, List, Optional

from app.schemas import Certification, Education, Experience, Language, ProfileResponse


def _format_date(date_obj: Optional[Dict[str, Any]]) -> Optional[str]:
    if not date_obj:
        return None
    year = date_obj.get("year")
    month = date_obj.get("month")
    if year and month:
        return f"{month:02d}/{year}"
    if year:
        return str(year)
    return None


def _best_image_url(image_dict: Optional[Dict[str, str]]) -> Optional[str]:
    if not image_dict:
        return None
    # Prefer the largest available resolution
    for key in ("800x800", "1400x350", "400x400", "200x200", "800x200", "100x100"):
        if key in image_dict and image_dict[key]:
            return image_dict[key]
    values = [v for v in image_dict.values() if v]
    return values[0] if values else None


def _map_experience(positions: List[Dict[str, Any]]) -> List[Experience]:
    mapped = []
    for item in positions or []:
        company = item.get("company") or {}
        time_period = item.get("timePeriod") or {}
        start = time_period.get("startDate")
        end = time_period.get("endDate")
        mapped.append(
            Experience(
                title=item.get("title"),
                company=company.get("name"),
                location=item.get("locationName") or None,
                start_date=_format_date(start),
                end_date=_format_date(end) if end else ("Present" if start else None),
                duration=item.get("totalDuration"),
                description=item.get("description") or None,
            )
        )
    return mapped


def _map_education(educations: List[Dict[str, Any]]) -> List[Education]:
    mapped = []
    for item in educations or []:
        time_period = item.get("timePeriod") or {}
        mapped.append(
            Education(
                school=item.get("schoolName"),
                degree=item.get("degreeName") or None,
                field_of_study=item.get("fieldOfStudy") or None,
                start_date=_format_date(time_period.get("startDate")),
                end_date=_format_date(time_period.get("endDate")),
            )
        )
    return mapped


def _map_certifications(raw_list: List[Dict[str, Any]]) -> List[Certification]:
    mapped = []
    for item in raw_list or []:
        mapped.append(
            Certification(
                name=item.get("name") or item.get("title"),
                issuing_organization=item.get("authority") or item.get("company"),
                issue_date=_format_date(item.get("timePeriod", {}).get("startDate"))
                if isinstance(item.get("timePeriod"), dict)
                else item.get("date"),
                credential_id=item.get("licenseNumber") or item.get("credentialId"),
            )
        )
    return mapped


def _map_languages(raw_list: List[Any]) -> List[Language]:
    mapped = []
    for item in raw_list or []:
        if isinstance(item, str):
            mapped.append(Language(name=item, proficiency=None))
        elif isinstance(item, dict):
            mapped.append(
                Language(
                    name=item.get("name") or item.get("title"),
                    proficiency=item.get("proficiency") or item.get("level"),
                )
            )
    return mapped


def _map_skills(raw_list: List[Any]) -> List[str]:
    skills = []
    for item in raw_list or []:
        if isinstance(item, str):
            skills.append(item)
        elif isinstance(item, dict):
            name = item.get("name") or item.get("title")
            if name:
                skills.append(name)
    return skills


_KNOWN_KEYS = {
    "firstName", "lastName", "headline", "geoLocationName", "geoCountryName",
    "summary", "pictureUrl", "coverImageUrl", "positions", "educations",
    "skills", "certifications", "languages", "inputUrl", "publicIdentifier",
}


def normalize_profile(raw: Dict[str, Any], source_url: str) -> ProfileResponse:
    first_name = raw.get("firstName") or ""
    last_name = raw.get("lastName") or ""
    full_name = f"{first_name} {last_name}".strip() or None

    extra_keys = [k for k in raw.keys() if k not in _KNOWN_KEYS]

    return ProfileResponse(
        source_url=source_url,
        name=full_name,
        headline=raw.get("headline"),
        location=raw.get("geoLocationName"),
        about=raw.get("summary"),
        profile_image_url=_best_image_url(raw.get("pictureUrl")),
        banner_image_url=_best_image_url(raw.get("coverImageUrl")),
        experience=_map_experience(raw.get("positions") or []),
        education=_map_education(raw.get("educations") or []),
        skills=_map_skills(raw.get("skills") or []),
        certifications=_map_certifications(raw.get("certifications") or []),
        languages=_map_languages(raw.get("languages") or []),
        raw_fields_available=extra_keys,
    )