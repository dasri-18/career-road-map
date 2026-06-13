"""Project recommendation engine based on missing skills."""

from __future__ import annotations

from .models import ProjectRecommendation


class ProjectRecommendationEngine:
    """Recommend portfolio projects that close identified skill gaps."""

    def recommend(
        self, missing_skills: list[str], hiring_focus_areas: list[str] | None = None
    ) -> list[ProjectRecommendation]:
        """Return recommended projects sorted by coverage and relevance."""
        if not missing_skills:
            return [
                ProjectRecommendation(
                    title="Advanced Portfolio Enhancement",
                    description="Strengthen existing skills with deployment, testing, monitoring, and documentation.",
                    skills_covered=["Testing", "Git", "System Design"],
                    difficulty="Medium",
                    estimated_hours=30,
                    deliverables=[
                        "Production-style README",
                        "CI pipeline",
                        "Deployed demo",
                    ],
                )
            ]

        missing_set = {skill.lower() for skill in missing_skills}
        focus_set = {focus.lower() for focus in (hiring_focus_areas or [])}
        scored_recommendations = []
        for item in self._catalog():
            if not self._covers_any(item.skills_covered, missing_set):
                continue
            score = self._coverage_score(item, missing_set, focus_set)
            item.coverage_score = score
            scored_recommendations.append(item)
        scored_recommendations.sort(key=lambda item: item.coverage_score, reverse=True)
        return scored_recommendations[:5]

    def _catalog(self) -> list[ProjectRecommendation]:
        """Return the built-in project catalog."""
        return [
            ProjectRecommendation(
                title="Resume Screening System",
                description="Build an NLP system that parses resumes, extracts skills, and ranks candidates against job descriptions.",
                skills_covered=[
                    "Python",
                    "NLP",
                    "Machine Learning",
                    "Data Analysis",
                    "REST APIs",
                ],
                difficulty="Medium",
                estimated_hours=35,
                deliverables=["Model notebook", "FastAPI service", "Streamlit demo"],
            ),
            ProjectRecommendation(
                title="Fraud Detection System",
                description="Train and deploy a machine learning model to detect fraudulent transactions with explainable metrics.",
                skills_covered=[
                    "Python",
                    "Machine Learning",
                    "Data Analysis",
                    "SQL",
                    "MLOps",
                ],
                difficulty="Medium",
                estimated_hours=40,
                deliverables=["EDA notebook", "Trained model", "Evaluation report"],
            ),
            ProjectRecommendation(
                title="Recommendation Engine",
                description="Create a content-based and collaborative recommendation system for courses, jobs, or products.",
                skills_covered=[
                    "Python",
                    "Machine Learning",
                    "SQL",
                    "Data Analysis",
                    "REST APIs",
                ],
                difficulty="Medium",
                estimated_hours=35,
                deliverables=["Recommendation API", "Evaluation metrics", "Demo UI"],
            ),
            ProjectRecommendation(
                title="AWS Deployment Project",
                description="Deploy a full-stack application on AWS using S3, Lambda, API Gateway, and CloudWatch.",
                skills_covered=["AWS", "Cloud Computing", "Python", "REST APIs", "Git"],
                difficulty="Medium",
                estimated_hours=30,
                deliverables=[
                    "Infrastructure diagram",
                    "Deployed API",
                    "Monitoring dashboard",
                ],
            ),
            ProjectRecommendation(
                title="Serverless Architecture Project",
                description="Build an event-driven serverless workflow with cloud functions, queues, storage, and logging.",
                skills_covered=["AWS", "Azure", "Cloud Computing", "Docker", "CI/CD"],
                difficulty="Hard",
                estimated_hours=45,
                deliverables=["Serverless app", "IaC template", "Load test results"],
            ),
            ProjectRecommendation(
                title="AI Career Roadmap Generator",
                description="Build a Streamlit application that parses resumes, compares skills, predicts readiness, and exports reports.",
                skills_covered=[
                    "Python",
                    "Streamlit",
                    "Machine Learning",
                    "NLP",
                    "Data Visualization",
                    "PDF Parsing",
                ],
                difficulty="Hard",
                estimated_hours=55,
                deliverables=[
                    "Streamlit app",
                    "SQLite database",
                    "PDF report generator",
                ],
            ),
            ProjectRecommendation(
                title="Real-Time Chat Application",
                description="Develop a real-time chat app with authentication, rooms, persistence, and deployment.",
                skills_covered=["NodeJS", "React", "REST APIs", "SQL", "Docker"],
                difficulty="Medium",
                estimated_hours=35,
                deliverables=["Frontend UI", "Backend API", "Containerized deployment"],
            ),
            ProjectRecommendation(
                title="Data Analytics Dashboard",
                description="Analyze a business dataset and create an interactive dashboard with KPIs and insights.",
                skills_covered=[
                    "Python",
                    "Data Analysis",
                    "Data Visualization",
                    "SQL",
                    "Power BI",
                ],
                difficulty="Easy",
                estimated_hours=25,
                deliverables=["Cleaned dataset", "Dashboard", "Insight report"],
            ),
            ProjectRecommendation(
                title="Kubernetes Microservices Demo",
                description="Containerize microservices and deploy them with Kubernetes, Helm, and CI/CD pipelines.",
                skills_covered=[
                    "Docker",
                    "Kubernetes",
                    "CI/CD",
                    "Git",
                    "System Design",
                ],
                difficulty="Hard",
                estimated_hours=50,
                deliverables=["Helm chart", "Cluster deployment", "Pipeline logs"],
            ),
            ProjectRecommendation(
                title="DSA Interview Practice Tracker",
                description="Build a web app to track data structure and algorithm practice with spaced repetition.",
                skills_covered=[
                    "Data Structures",
                    "Algorithms",
                    "React",
                    "NodeJS",
                    "SQL",
                ],
                difficulty="Medium",
                estimated_hours=35,
                deliverables=["Problem tracker", "Practice analytics", "User accounts"],
            ),
            ProjectRecommendation(
                title="Computer Vision Quality Inspector",
                description="Train a vision model to classify defects or detect objects in images.",
                skills_covered=[
                    "Computer Vision",
                    "Deep Learning",
                    "Python",
                    "Data Visualization",
                ],
                difficulty="Hard",
                estimated_hours=45,
                deliverables=["Model notebook", "Inference script", "Demo gallery"],
            ),
            ProjectRecommendation(
                title="RAG Knowledge Assistant",
                description="Build a retrieval-augmented generation assistant over documents using embeddings and a vector database.",
                skills_covered=[
                    "Generative AI",
                    "NLP",
                    "Python",
                    "Machine Learning",
                    "REST APIs",
                ],
                difficulty="Hard",
                estimated_hours=50,
                deliverables=["RAG pipeline", "Vector index", "Chat interface"],
            ),
            ProjectRecommendation(
                title="Cloud-Native Job Portal",
                description="Build a job portal with search, recommendations, authentication, and cloud deployment.",
                skills_covered=["Python", "SQL", "REST APIs", "AWS", "Docker", "CI/CD"],
                difficulty="Hard",
                estimated_hours=60,
                deliverables=["Deployed app", "Search API", "CI pipeline"],
            ),
            ProjectRecommendation(
                title="Business Consulting Analytics Pack",
                description="Create an analytics pack with stakeholder requirements, KPI dashboard, and recommendation deck.",
                skills_covered=[
                    "Business Analysis",
                    "Consulting",
                    "Excel",
                    "Power BI",
                    "Communication",
                ],
                difficulty="Medium",
                estimated_hours=30,
                deliverables=["Requirements doc", "KPI dashboard", "Executive deck"],
            ),
        ]

    @staticmethod
    def _covers_any(project_skills: list[str], missing_set: set[str]) -> bool:
        """Check whether a project covers at least one missing skill."""
        return any(skill.lower() in missing_set for skill in project_skills)

    @staticmethod
    def _coverage_score(
        item: ProjectRecommendation, missing_set: set[str], focus_set: set[str]
    ) -> float:
        """Score recommendations by missing skill and focus-area coverage."""
        project_skills = {skill.lower() for skill in item.skills_covered}
        missing_coverage = len(project_skills & missing_set)
        focus_coverage = sum(
            1 for focus in focus_set if any(focus in skill for skill in project_skills)
        )
        difficulty_bonus = {"Easy": 0.0, "Medium": 0.5, "Hard": 1.0}.get(
            item.difficulty, 0.0
        )
        return (missing_coverage * 2.0) + focus_coverage + difficulty_bonus
