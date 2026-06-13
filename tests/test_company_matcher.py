from utils.company_matcher import CompanyRequirementRepository, SkillGapAnalyzer


def test_list_companies_includes_known_companies() -> None:
    repository = CompanyRequirementRepository()
    companies = repository.list_companies()
    assert "Google" in companies
    assert "Microsoft" in companies


def test_analyze_skill_gap_for_google() -> None:
    repository = CompanyRequirementRepository()
    analyzer = SkillGapAnalyzer(repository)
    company = repository.load_company("Google")
    result = analyzer.analyze(["Python", "Machine Learning", "Algorithms"], company)
    assert result.skill_match_score > 0
    assert "Data Structures" in result.missing_required_skills
    assert "System Design" in result.missing_required_skills
