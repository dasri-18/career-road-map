"""Utility package for the AI Career Roadmap Generator."""

from .config import PROJECT_ROOT
from .models import (
    CompanyRequirement,
    ProjectRecommendation,
    ReadinessReport,
    ResumeProfile,
    RoadmapItem,
    SkillMatchResult,
)

__all__ = [
    "PROJECT_ROOT",
    "CompanyRequirement",
    "ProjectRecommendation",
    "ReadinessReport",
    "ResumeProfile",
    "RoadmapItem",
    "SkillMatchResult",
]
