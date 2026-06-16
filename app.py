from __future__ import annotations

from pathlib import Path
from typing import Any
import traceback

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.company_matcher import CompanyRequirementRepository, SkillGapAnalyzer
from utils.config import ensure_directories, RESUMES_DIR
from utils.database import SQLiteRepository
from utils.pdf_parser import PDFResumeParser
from utils.placement_model import PlacementPredictor
from utils.project_recommendation import ProjectRecommendationEngine
from utils.readiness_calculator import ReadinessCalculator
from utils.report_generator import ReportGenerator
from utils.roadmap_generator import RoadmapGenerator
from utils.skill_extractor import SkillExtractor


@st.cache_resource
def get_services() -> dict[str, Any]:
    ensure_directories()
    return {
        "parser": PDFResumeParser(SkillExtractor()),
        "company_repository": CompanyRequirementRepository(),
        "analyzer": SkillGapAnalyzer(),
        "calculator": ReadinessCalculator(),
        "roadmap_generator": RoadmapGenerator(),
        "project_engine": ProjectRecommendationEngine(),
        "placement_predictor": PlacementPredictor(),
        "report_generator": ReportGenerator(),
        "database": SQLiteRepository(),
    }


@st.cache_data
def load_company_options() -> list[str]:
    repository = CompanyRequirementRepository()
    companies = repository.list_companies()
    preferred = [
        "Google",
        "Microsoft",
        "Amazon",
        "TCS",
        "Infosys",
        "Accenture",
        "Deloitte",
        "Cognizant",
    ]
    ordered = [company for company in preferred if company in companies]
    ordered.extend([company for company in companies if company not in ordered])
    ordered.append("Custom Company")
    return ordered


def save_uploaded_resume(uploaded_file: bytes, file_name: str) -> Path:
    ensure_directories()
    sanitized_name = Path(file_name).name
    file_path = RESUMES_DIR / sanitized_name
    file_path.write_bytes(uploaded_file)
    return file_path


def build_gauge_chart(overall_score: float) -> go.Figure:
    return go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=overall_score,
            title={"text": "Overall Readiness"},
            delta={"reference": 70, "increasing": {"color": "green"}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "royalblue"},
                "steps": [
                    {"range": [0, 40], "color": "#ff4d4d"},
                    {"range": [40, 70], "color": "#ffcc00"},
                    {"range": [70, 100], "color": "#00cc96"},
                ],
            },
        )
    )


def build_radar_chart(report: Any) -> go.Figure:
    categories = [
        "Technical",
        "Project",
        "Certifications",
        "Experience",
        "Placement",
    ]
    values = [
        report.technical_readiness_score,
        report.project_readiness_score,
        report.certification_score,
        report.experience_score,
        report.placement_probability,
    ]
    return go.Figure(
        data=[
            go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name="Readiness",
            )
        ],
        layout=go.Layout(polar={"radialaxis": {"range": [0, 100]}}, showlegend=False),
    )


def build_skill_gap_chart(skill_match: Any) -> go.Figure:
    categories = ["Matched Skills", "Missing Required", "Missing Preferred"]
    values = [
        len(skill_match.matching_skills),
        len(skill_match.missing_required_skills),
        len(skill_match.missing_preferred_skills),
    ]
    return px.bar(
        x=categories,
        y=values,
        labels={"x": "Category", "y": "Count"},
        title="Skill Match Breakdown",
    )


def create_report_bytes(
    candidate_name: str,
    email: str | None,
    target_role: str | None,
    company_name: str,
    profile_text: str,
    skill_match: Any,
    readiness_report: Any,
    roadmap: dict[str, list[Any]],
    recommendations: list[Any],
) -> bytes:
    generator = get_services()["report_generator"]
    return generator.create_pdf(
        candidate_name=candidate_name,
        email=email,
        target_role=target_role,
        company_name=company_name,
        profile_text=profile_text,
        skill_match=skill_match,
        readiness_report=readiness_report,
        roadmap=roadmap,
        recommendations=recommendations,
    )


def get_unemployed_roadmap_tree() -> str:
    return """
Unemployed Student
│
├── Choose Career Domain
│   ├── Web Development
│   ├── Data Science
│   ├── AI/ML
│   ├── Cyber Security
│   └── Cloud Computing
│
├── Learn Fundamentals
│   ├── Programming (Python/Java/C++)
│   ├── DBMS
│   ├── OOPs
│   ├── Operating Systems
│   └── Computer Networks
│
├── Develop Skills
│   ├── Data Structures & Algorithms
│   ├── Git & GitHub
│   ├── Problem Solving
│   └── Aptitude & Reasoning
│
├── Build Projects
│   ├── Mini Project 1
│   ├── Mini Project 2
│   ├── Major Project
│   └── Portfolio Website
│
├── Create Professional Profiles
│   ├── Resume
│   ├── LinkedIn Profile
│   └── GitHub Profile
│
├── Apply for Internships
│   ├── Google
│   ├── Microsoft
│   ├── Amazon
│   ├── Infosys
│   ├── TCS
│   ├── Wipro
│   └── Accenture
│
├── Prepare for Interviews
│   ├── Coding Questions
│   ├── Technical Subjects
│   ├── Mock Interviews
│   └── Communication Skills
│
└── Get Internship
    ├── Gain Experience
    ├── Learn Industry Tools
    └── Convert Internship to Full-Time Job
"""


def display_roadmap_tree() -> None:
    st.subheader("🎯 Unemployed Internship Roadmap")
    
    roadmap_stages = {
        "01 Choose Career Domain": [
            "Web Development",
            "Data Science",
            "AI/ML",
            "Cyber Security",
            "Cloud Computing",
        ],
        "02 Learn Fundamentals": [
            "Programming (Python/Java/C++)",
            "DBMS",
            "OOPs",
            "Operating Systems",
            "Computer Networks",
        ],
        "03 Develop Skills": [
            "Data Structures & Algorithms",
            "Git & GitHub",
            "Problem Solving",
            "Aptitude & Reasoning",
        ],
        "04 Build Projects": [
            "Mini Project 1",
            "Mini Project 2",
            "Major Project",
            "Portfolio Website",
        ],
        "05 Create Professional Profiles": [
            "Resume",
            "LinkedIn Profile",
            "GitHub Profile",
        ],
        "06 Apply for Internships": [
            "Google",
            "Microsoft",
            "Amazon",
            "Infosys",
            "TCS",
            "Wipro",
            "Accenture",
        ],
        "07 Prepare for Interviews": [
            "Coding Questions",
            "Technical Subjects",
            "Mock Interviews",
            "Communication Skills",
        ],
        "08 Get Internship": [
            "Gain Experience",
            "Learn Industry Tools",
            "Convert Internship to Full-Time Job",
        ],
    }
    
    cols = st.columns(2)
    for idx, (stage, items) in enumerate(roadmap_stages.items()):
        with cols[idx % 2]:
            with st.expander(f"📍 {stage}", expanded=(idx < 2)):
                for item in items:
                    st.write(f"  • {item}")



def main() -> None:
    st.set_page_config(page_title="AI Career Roadmap Generator", layout="wide")
    services = get_services()
    st.title("AI Career Roadmap Generator")
    st.markdown(
        "Use the form below to upload your resume, select a target company, and receive a personalized career readiness report."
    )
    display_roadmap_tree()


    with st.sidebar.form("profile_form"):
        name = st.text_input("Candidate name", value="")
        email = st.text_input("Email address", value="")
        target_role = st.text_input("Target role", value="Software Engineer")
        education_level = st.selectbox(
            "Highest education level",
            ["High School", "Diploma", "Bachelor's", "Master's", "Doctorate", "Other"],
            index=2,
        )
        company_choice = st.selectbox("Target company", load_company_options())
        custom_company_name = ""
        custom_required = ""
        custom_preferred = ""
        custom_focus = ""
        if company_choice == "Custom Company":
            custom_company_name = st.text_input("Custom company name", value="")
            custom_required = st.text_area(
                "Required skills (comma-separated)",
                value="Python, SQL, Machine Learning",
            )
            custom_preferred = st.text_area(
                "Preferred skills (comma-separated)",
                value="Cloud Computing, Git, Agile",
            )
            custom_focus = st.text_area(
                "Hiring focus areas (comma-separated)", value="Engineering, Data, Cloud"
            )
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        submitted = st.form_submit_button("Analyze career readiness")

    if not submitted:
        st.info("Upload a PDF resume and click Analyze career readiness to begin.")
        return

    if not name or not uploaded_file:
        st.error("Please provide your name and upload a resume PDF.")
        return

    try:
        resume_bytes = uploaded_file.read()
        saved_path = save_uploaded_resume(resume_bytes, uploaded_file.name)
        resume_profile = services["parser"].parse_file(saved_path)

        if company_choice == "Custom Company":
            company_data = services["company_repository"].load_custom_company(
                company_name=custom_company_name or "Custom Company",
                required_skills=[
                    skill.strip()
                    for skill in custom_required.split(",")
                    if skill.strip()
                ],
                preferred_skills=[
                    skill.strip()
                    for skill in custom_preferred.split(",")
                    if skill.strip()
                ],
                hiring_focus_areas=[
                    focus.strip() for focus in custom_focus.split(",") if focus.strip()
                ],
            )
        else:
            company_data = services["company_repository"].load_company(company_choice)

        skill_match = services["analyzer"].analyze(resume_profile.skills, company_data)
        roadmap = services["roadmap_generator"].generate_multi_duration(
            skill_match.missing_required_skills + skill_match.missing_preferred_skills,
            services["parser"].skill_extractor.extract_skill_details(
                resume_profile.raw_text
            ),
        )
        recommendations = services["project_engine"].recommend(
            skill_match.missing_required_skills + skill_match.missing_preferred_skills,
            company_data.hiring_focus_areas,
        )

        placement_probability, interview_readiness = services[
            "placement_predictor"
        ].predict(
            {
                "experience_years": resume_profile.experience_years,
                "project_count": len(resume_profile.projects),
                "certification_count": len(resume_profile.certifications),
                "skill_match_score": skill_match.skill_match_score,
                "project_relevance_score": len(resume_profile.projects) * 12.5,
                "company_fit_score": skill_match.company_fit_score,
            }
        )

        readiness_report = services["calculator"].calculate(
            skill_match=skill_match,
            project_count=len(resume_profile.projects),
            certification_count=len(resume_profile.certifications),
            experience_years=resume_profile.experience_years,
            placement_probability=placement_probability,
            interview_readiness=interview_readiness,
        )

        profile_id = services["database"].save_user_profile(
            name, email, target_role, education_level
        )
        upload_id = services["database"].save_resume_upload(
            profile_id, uploaded_file.name, str(saved_path), resume_profile.raw_text
        )
        analysis_id = services["database"].save_skill_analysis(
            profile_id, upload_id, company_data.company_name, target_role, skill_match
        )
        services["database"].save_readiness_report(analysis_id, readiness_report)
        services["database"].save_resume_profile(profile_id, resume_profile)

        st.success("Career readiness analysis complete!")
        st.subheader("Readiness summary")
        st.write(readiness_report.summary)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                build_gauge_chart(readiness_report.overall_readiness_score),
                use_container_width=True,
            )
            st.plotly_chart(
                build_skill_gap_chart(skill_match), use_container_width=True
            )
        with col2:
            st.plotly_chart(
                build_radar_chart(readiness_report), use_container_width=True
            )
            st.metric("Placement probability", f"{placement_probability:.1f}%")
            st.metric("Interview readiness", f"{interview_readiness:.1f}%")

        st.subheader("Resume insights")
        st.write(
            "**Detected skills:**",
            ", ".join(resume_profile.skills) or "No skills detected",
        )
        st.write(
            "**Education:**",
            ", ".join(resume_profile.education) or "No education detected",
        )
        st.write(
            "**Projects:**",
            ", ".join(resume_profile.projects) or "No projects detected",
        )
        st.write(
            "**Certifications:**",
            ", ".join(resume_profile.certifications) or "No certifications detected",
        )
        st.write("**Experience estimate:**", f"{resume_profile.experience_years} years")

        st.subheader("Learning roadmap")
        for label, entries in roadmap.items():
            with st.expander(label.title(), expanded=(label == "90 day roadmap")):
                for item in entries:
                    st.markdown(f"**{item.day_range} — {item.skill}**")
                    st.markdown(f"- Objective: {item.objective}")
                    st.markdown(f"- Practice: {item.recommended_practice}")
                    st.markdown(f"- Deliverable: {item.deliverable}")
                    st.markdown(f"- Estimated hours: {item.estimated_hours}")

        st.subheader("Recommended projects")
        for project in recommendations:
            st.markdown(f"### {project.title}")
            st.write(project.description)
            st.write(f"Skills: {', '.join(project.skills_covered)}")
            st.write(
                f"Difficulty: {project.difficulty} — Estimated hours: {project.estimated_hours}"
            )

        report_bytes = create_report_bytes(
            candidate_name=name,
            email=email,
            target_role=target_role,
            company_name=company_data.company_name,
            profile_text=resume_profile.raw_text,
            skill_match=skill_match,
            readiness_report=readiness_report,
            roadmap=roadmap,
            recommendations=recommendations,
        )
        st.download_button(
            "Download PDF report",
            data=report_bytes,
            file_name=f"career_readiness_report_{name.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )

    except Exception as error:
        st.error("An unexpected error occurred during analysis. Check the app logs for details.")
        st.text_area("Analysis traceback", traceback.format_exc(), height=300)


if __name__ == "__main__":
    main()
