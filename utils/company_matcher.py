"""Company requirement loading, TF-IDF matching, and skill gap analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import COMPANY_DATA_DIR
from .models import CompanyRequirement, SkillMatchResult


class CompanyRequirementRepository:
    """Load and manage company requirement JSON files."""

    def __init__(self, company_data_dir: str | Path = COMPANY_DATA_DIR) -> None:
        self.company_data_dir = Path(company_data_dir)

    def list_companies(self) -> list[str]:
        """Return available company names in deterministic order."""
        names: list[str] = []
        for path in sorted(self.company_data_dir.glob("*.json")):
            try:
                with path.open("r", encoding="utf-8") as file:
                    payload = json.load(file)
                names.append(str(payload.get("company_name", path.stem.capitalize())))
            except Exception:
                names.append(path.stem.capitalize())
        return names

    def load_company(self, company_name: str) -> CompanyRequirement:
        """Load a company requirement file by name."""
        path = self.company_data_dir / f"{company_name.lower()}.json"
        if not path.exists():
            raise FileNotFoundError(f"Company data file not found: {path}")
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return CompanyRequirement(
            company_name=payload["company_name"],
            role_family=payload.get("role_family", "Software / Data / Cloud Engineer"),
            required_skills=payload.get("required_skills", []),
            preferred_skills=payload.get("preferred_skills", []),
            hiring_focus_areas=payload.get("hiring_focus_areas", []),
            description=payload.get("description", ""),
            baseline_difficulty=float(payload.get("baseline_difficulty", 3.0)),
        )

    def load_custom_company(
        self,
        company_name: str,
        required_skills: list[str],
        preferred_skills: list[str] | None = None,
        hiring_focus_areas: list[str] | None = None,
    ) -> CompanyRequirement:
        """Build a custom company requirement object from user input."""
        return CompanyRequirement(
            company_name=company_name or "Custom Company",
            role_family="Custom Role Family",
            required_skills=[
                {"skill": skill.strip(), "weight": 5}
                for skill in required_skills
                if skill.strip()
            ],
            preferred_skills=[
                {"skill": skill.strip(), "weight": 3}
                for skill in (preferred_skills or [])
                if skill.strip()
            ],
            hiring_focus_areas=hiring_focus_areas or ["Custom hiring focus"],
            description="Custom company requirement generated from user input.",
            baseline_difficulty=3.0,
        )

    def requirement_text(self, company: CompanyRequirement) -> str:
        """Create a text representation of company requirements for TF-IDF."""
        required = " ".join(company.normalized_required_skills)
        preferred = " ".join(company.normalized_preferred_skills)
        focus = " ".join(company.hiring_focus_areas)
        return f"{company.description} {company.role_family} {required} {preferred} {focus}"


class SkillGapAnalyzer:
    """Compare resume skills against company requirements using weights and TF-IDF."""

    def __init__(self, repository: CompanyRequirementRepository | None = None) -> None:
        self.repository = repository or CompanyRequirementRepository()

    def analyze(
        self, resume_skills: list[str], company: CompanyRequirement
    ) -> SkillMatchResult:
        """Analyze skill match and gaps for a resume profile and company."""
        resume_skill_set = {skill.lower() for skill in resume_skills}
        required = self._weighted_items(company.required_skills)
        preferred = self._weighted_items(company.preferred_skills)

        matching_required = [
            skill for skill, _ in required if skill.lower() in resume_skill_set
        ]
        missing_required = [
            skill for skill, _ in required if skill.lower() not in resume_skill_set
        ]
        matching_preferred = [
            skill for skill, _ in preferred if skill.lower() in resume_skill_set
        ]
        missing_preferred = [
            skill for skill, _ in preferred if skill.lower() not in resume_skill_set
        ]

        required_weight = sum(weight for _, weight in required) or 1.0
        preferred_weight = sum(weight for _, weight in preferred) or 1.0
        weighted_required_match = (
            sum(
                weight
                for skill, weight in required
                if skill.lower() in resume_skill_set
            )
            / required_weight
        )
        weighted_preferred_match = (
            sum(
                weight
                for skill, weight in preferred
                if skill.lower() in resume_skill_set
            )
            / preferred_weight
        )
        skill_match_score = self._weighted_score(
            weighted_required_match, weighted_preferred_match
        )
        skill_gap_percentage = round((1.0 - skill_match_score) * 100.0, 2)

        company_text = self.repository.requirement_text(company)
        resume_text = " ".join(resume_skills)
        company_fit_score = self._cosine_similarity(resume_text, company_text)

        return SkillMatchResult(
            matching_skills=list(dict.fromkeys(matching_required + matching_preferred)),
            missing_required_skills=missing_required,
            missing_preferred_skills=missing_preferred,
            skill_match_score=round(skill_match_score * 100.0, 2),
            skill_gap_percentage=skill_gap_percentage,
            weighted_required_match=round(weighted_required_match * 100.0, 2),
            weighted_preferred_match=round(weighted_preferred_match * 100.0, 2),
            company_fit_score=round(company_fit_score * 100.0, 2),
        )

    def compare_companies(
        self, resume_skills: list[str], companies: list[CompanyRequirement]
    ) -> dict[str, SkillMatchResult]:
        """Analyze the same resume against multiple companies."""
        return {
            company.company_name: self.analyze(resume_skills, company)
            for company in companies
        }

    @staticmethod
    def _weighted_items(items: list[dict[str, Any]]) -> list[tuple[str, float]]:
        """Normalize skill dictionaries into weighted tuples."""
        normalized: list[tuple[str, float]] = []
        seen: set[str] = set()
        for item in items:
            if not isinstance(item, dict) or "skill" not in item:
                continue
            skill = str(item["skill"]).strip()
            if not skill or skill.lower() in seen:
                continue
            weight = float(item.get("weight", 3))
            normalized.append((skill, max(1.0, min(5.0, weight))))
            seen.add(skill.lower())
        return normalized

    @staticmethod
    def _weighted_score(required_score: float, preferred_score: float) -> float:
        """Combine required and preferred skill scores."""
        return (0.75 * required_score) + (0.25 * preferred_score)

    @staticmethod
    def _cosine_similarity(resume_text: str, company_text: str) -> float:
        """Calculate TF-IDF cosine similarity between resume and company text."""
        if not resume_text.strip() or not company_text.strip():
            return 0.0
        try:
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            matrix = vectorizer.fit_transform([resume_text, company_text])
            score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
            return float(np.clip(score, 0.0, 1.0))
        except ValueError:
            return 0.0
