import pytest

from utils.skill_extractor import SkillExtractor


@pytest.fixture()
def skill_extractor() -> SkillExtractor:
    return SkillExtractor()


def test_extract_skills_from_text(skill_extractor: SkillExtractor) -> None:
    text = (
        "Experienced in Python, machine learning, SQL, Docker, and AWS cloud services."
    )
    skills = skill_extractor.extract_skills(text)
    assert "Python" in skills
    assert "Machine Learning" in skills
    assert "SQL" in skills
    assert "Docker" in skills
    assert "AWS" in skills
