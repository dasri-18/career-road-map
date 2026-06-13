from utils.models import SkillMatchResult
from utils.readiness_calculator import ReadinessCalculator


def test_readiness_scores_are_within_bounds() -> None:
    skill_match = SkillMatchResult(
        matching_skills=["Python", "SQL"],
        missing_required_skills=["Machine Learning"],
        missing_preferred_skills=["Docker"],
        skill_match_score=70.0,
        skill_gap_percentage=30.0,
        weighted_required_match=65.0,
        weighted_preferred_match=50.0,
        company_fit_score=60.0,
    )
    calculator = ReadinessCalculator()
    report = calculator.calculate(
        skill_match,
        project_count=2,
        certification_count=1,
        experience_years=1.2,
        placement_probability=65.0,
        interview_readiness=70.0,
    )
    assert 0 <= report.overall_readiness_score <= 100
    assert report.readiness_level in {
        "Highly Ready",
        "Ready with Minor Gaps",
        "Moderately Ready",
        "Developing",
        "Not Ready Yet",
    }
