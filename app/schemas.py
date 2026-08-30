"""
Response schema for the /profile endpoint.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    school: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Certification(BaseModel):
    name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None


class Language(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None


class ProfileResponse(BaseModel):
    source_url: str
    name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    about: Optional[str] = None
    profile_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    raw_fields_available: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str