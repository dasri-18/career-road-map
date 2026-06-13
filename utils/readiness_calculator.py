"""Readiness score calculation and ML-backed prediction utilities."""

from __future__ import annotations

from .models import ReadinessReport, SkillMatchResult


class ReadinessCalculator:
    """Calculate readiness scores from skill, project, certification, and experience signals."""

    def calculate(
        self,
        skill_match: SkillMatchResult,
        project_count: int,
        certification_count: int,
        experience_years: float,
        placement_probability: float,
        interview_readiness: float,
    ) -> ReadinessReport:
        """Create a readiness report with weighted scores."""
        technical_score = self._technical_score(skill_match)
        project_score = self._project_score(project_count)
        certification_score = self._certification_score(certification_count)
        experience_score = self._experience_score(experience_years)

        overall = (
            (0.50 * technical_score)
            + (0.20 * project_score)
            + (0.10 * certification_score)
            + (0.10 * experience_score)
            + (0.10 * skill_match.company_fit_score)
        )
        overall = self._clamp(overall)

        placement_probability = self._clamp(placement_probability)
        interview_readiness = self._clamp(interview_readiness)
        readiness_level = self._readiness_level(overall)
        summary = self._summary(overall, readiness_level, skill_match)

        return ReadinessReport(
            overall_readiness_score=round(overall, 2),
            technical_readiness_score=round(technical_score, 2),
            project_readiness_score=round(project_score, 2),
            certification_score=round(certification_score, 2),
            experience_score=round(experience_score, 2),
            placement_probability=round(placement_probability, 2),
            interview_readiness=round(interview_readiness, 2),
            readiness_level=readiness_level,
            summary=summary,
        )

    def heuristic_prediction(
        self,
        technical_score: float,
        project_score: float,
        certification_score: float,
        experience_score: float,
        company_fit_score: float,
    ) -> tuple[float, float]:
        """Return fallback placement and interview predictions without a serialized model."""
        placement = (
            (0.45 * technical_score)
            + (0.25 * project_score)
            + (0.10 * certification_score)
            + (0.10 * experience_score)
            + (0.10 * company_fit_score)
        ) / 100.0
        interview = (
            (0.45 * technical_score)
            + (0.30 * project_score)
            + (0.15 * experience_score)
            + (0.10 * company_fit_score)
        )
        return self._clamp(placement), self._clamp(interview)

    @staticmethod
    def _technical_score(skill_match: SkillMatchResult) -> float:
        """Technical readiness is driven mostly by required skill coverage."""
        return (
            (0.70 * skill_match.weighted_required_match)
            + (0.20 * skill_match.company_fit_score)
            + (0.10 * skill_match.weighted_preferred_match)
        )

    @staticmethod
    def _project_score(project_count: int) -> float:
        """Score project readiness based on count and portfolio depth."""
        if project_count >= 5:
            return 95.0
        if project_count == 4:
            return 85.0
        if project_count == 3:
            return 75.0
        if project_count == 2:
            return 60.0
        if project_count == 1:
            return 40.0
        return 20.0

    @staticmethod
    def _certification_score(certification_count: int) -> float:
        """Score certifications with diminishing returns."""
        if certification_count >= 3:
            return 90.0
        if certification_count == 2:
            return 75.0
        if certification_count == 1:
            return 55.0
        return 25.0

    @staticmethod
    def _experience_score(experience_years: float) -> float:
        """Score experience from internships through senior professional levels."""
        if experience_years >= 5:
            return 95.0
        if experience_years >= 3:
            return 85.0
        if experience_years >= 1:
            return 70.0
        if experience_years >= 0.5:
            return 55.0
        return 35.0

    @staticmethod
    def _readiness_level(score: float) -> str:
        """Map numeric readiness to a human-readable level."""
        if score >= 85:
            return "Highly Ready"
        if score >= 70:
            return "Ready with Minor Gaps"
        if score >= 55:
            return "Moderately Ready"
        if score >= 40:
            return "Developing"
        return "Not Ready Yet"

    @staticmethod
    def _summary(
        score: float, readiness_level: str, skill_match: SkillMatchResult
    ) -> str:
        """Create a concise readiness summary."""
        missing_count = len(skill_match.missing_required_skills)
        return (
            f"{readiness_level} at {score:.1f}% readiness. "
            f"{len(skill_match.matching_skills)} skills match the target company, "
            f"and {missing_count} required skills should be prioritized."
        )

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp values to a 0-100 range."""
        return float(max(0.0, min(100.0, value)))
