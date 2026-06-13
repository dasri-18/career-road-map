"""Typed dataclasses used across the roadmap generator modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ResumeProfile:
    """Structured resume information extracted from raw resume text."""

    skills: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    experience_years: float = 0.0
    raw_text: str = ""


@dataclass(frozen=True)
class CompanyRequirement:
    """Company-specific skill requirements and hiring focus areas."""

    company_name: str
    role_family: str
    required_skills: list[dict[str, Any]]
    preferred_skills: list[dict[str, Any]]
    hiring_focus_areas: list[str]
    description: str
    baseline_difficulty: float = 3.0

    @property
    def normalized_required_skills(self) -> list[str]:
        """Return only canonical skill names for required skills."""
        return [
            item["skill"] for item in self.required_skills if isinstance(item, dict)
        ]

    @property
    def normalized_preferred_skills(self) -> list[str]:
        """Return only canonical skill names for preferred skills."""
        return [
            item["skill"] for item in self.preferred_skills if isinstance(item, dict)
        ]

    @property
    def all_skills(self) -> list[str]:
        """Return required and preferred skills without duplicates."""
        return list(
            dict.fromkeys(
                self.normalized_required_skills + self.normalized_preferred_skills
            )
        )


@dataclass(frozen=True)
class SkillMatchResult:
    """Skill matching and gap analysis output."""

    matching_skills: list[str]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]
    skill_match_score: float
    skill_gap_percentage: float
    weighted_required_match: float
    weighted_preferred_match: float
    company_fit_score: float


@dataclass(frozen=True)
class ReadinessReport:
    """Overall readiness and sub-score report."""

    overall_readiness_score: float
    technical_readiness_score: float
    project_readiness_score: float
    certification_score: float
    experience_score: float
    placement_probability: float
    interview_readiness: float
    readiness_level: str
    summary: str


@dataclass(frozen=True)
class RoadmapItem:
    """Single learning roadmap activity."""

    day_range: str
    skill: str
    objective: str
    recommended_practice: str
    estimated_hours: int
    deliverable: str
    priority: str


@dataclass
class ProjectRecommendation:
    """Recommended project generated from missing skills."""

    title: str
    description: str
    skills_covered: list[str]
    difficulty: str
    estimated_hours: int
    deliverables: list[str]
    coverage_score: float = 0.0
