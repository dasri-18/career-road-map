"""Personalized learning roadmap generator."""

from __future__ import annotations

from .models import RoadmapItem


class RoadmapGenerator:
    """Generate 30, 60, and 90 day learning plans for missing skills."""

    CATEGORY_ORDER = {
        "Computer Science Fundamentals": 1,
        "Programming Language": 2,
        "Backend": 3,
        "Frontend": 4,
        "Database": 5,
        "AI / ML": 6,
        "Cloud / DevOps": 7,
        "Data": 8,
        "Data Science": 9,
        "Engineering Practice": 10,
        "DevOps / Collaboration": 11,
        "Professional Skills": 12,
        "Business / Product": 13,
        "Security": 14,
        "Emerging Technology": 15,
        "Mobile": 16,
        "Design": 17,
        "Quality": 18,
        "Data Engineering": 19,
        "Business Tools": 20,
        "Enterprise": 21,
        "Hardware": 22,
        "Domain Knowledge": 23,
        "Marketing": 24,
    }

    PRACTICE_LIBRARY = {
        "Python": (
            "Complete 30 Python exercises covering functions, classes, decorators, and file handling.",
            "Build a CLI data-processing utility.",
        ),
        "Java": (
            "Solve object-oriented design problems and practice Spring Boot REST APIs.",
            "Build a REST API with validation and persistence.",
        ),
        "C++": (
            "Practice memory management, STL containers, and complexity analysis problems.",
            "Implement common data structures from scratch.",
        ),
        "JavaScript": (
            "Build interactive DOM projects and complete asynchronous JavaScript exercises.",
            "Create a browser-based task manager.",
        ),
        "React": (
            "Build reusable components, manage state, and call APIs from React.",
            "Create a responsive dashboard with charts.",
        ),
        "NodeJS": (
            "Build Express routes, middleware, authentication, and database integrations.",
            "Create a secure REST API with JWT auth.",
        ),
        "SQL": (
            "Practice joins, indexing, window functions, and query optimization.",
            "Design a normalized database and write analytics queries.",
        ),
        "Machine Learning": (
            "Train classification and regression models, evaluate metrics, and tune hyperparameters.",
            "Build an end-to-end supervised learning project.",
        ),
        "Deep Learning": (
            "Implement neural networks, CNNs, and transfer learning workflows.",
            "Fine-tune a pre-trained model for a real dataset.",
        ),
        "NLP": (
            "Practice tokenization, embeddings, transformers, and evaluation metrics.",
            "Build a text classifier or sentiment analysis system.",
        ),
        "Computer Vision": (
            "Train image classifiers, object detectors, and augmentation pipelines.",
            "Build an image classification or detection app.",
        ),
        "Generative AI": (
            "Learn prompting, RAG, embeddings, vector databases, and LLM evaluation.",
            "Build a retrieval-augmented chatbot.",
        ),
        "Data Structures": (
            "Solve array, linked list, tree, graph, heap, and hash map problems daily.",
            "Complete 50 curated DSA problems.",
        ),
        "Algorithms": (
            "Practice sorting, searching, recursion, dynamic programming, and greedy algorithms.",
            "Complete 40 algorithm problems with explanations.",
        ),
        "Cloud Computing": (
            "Learn cloud service models, networking, security, and serverless basics.",
            "Deploy a small app to a cloud provider.",
        ),
        "AWS": (
            "Use EC2, S3, Lambda, IAM, and CloudWatch through hands-on labs.",
            "Deploy a serverless API on AWS.",
        ),
        "Azure": (
            "Use Azure App Service, Functions, Storage, and Azure DevOps.",
            "Deploy an Azure Functions API.",
        ),
        "Git": (
            "Practice branching, rebasing, pull requests, and conflict resolution.",
            "Maintain a clean GitHub project history.",
        ),
        "Docker": (
            "Containerize apps, write Dockerfiles, and use Docker Compose.",
            "Containerize a full-stack application.",
        ),
        "Kubernetes": (
            "Learn pods, deployments, services, ingress, and Helm charts.",
            "Deploy a microservice app to Kubernetes.",
        ),
        "Data Analysis": (
            "Use pandas and numpy to clean, transform, and analyze datasets.",
            "Create an exploratory data analysis notebook.",
        ),
        "Data Visualization": (
            "Build interactive charts and dashboards with Plotly or Power BI.",
            "Create a dashboard with actionable insights.",
        ),
        "System Design": (
            "Study scalability, caching, queues, databases, and API design tradeoffs.",
            "Design a URL shortener or notification system.",
        ),
        "MLOps": (
            "Track experiments, package models, deploy APIs, and monitor drift.",
            "Deploy a model with MLflow and FastAPI.",
        ),
        "Testing": (
            "Write unit, integration, and end-to-end tests for real applications.",
            "Add pytest coverage to a project.",
        ),
        "REST APIs": (
            "Design REST resources, status codes, pagination, auth, and documentation.",
            "Build and document a production-style API.",
        ),
        "Communication": (
            "Practice explaining projects, tradeoffs, and metrics clearly.",
            "Record a 3-minute project walkthrough.",
        ),
        "Problem Solving": (
            "Solve structured problems and write concise reasoning for each answer.",
            "Complete daily interview-style problems.",
        ),
        "Agile": (
            "Practice user stories, sprint planning, retrospectives, and estimation.",
            "Run a mini sprint for a portfolio project.",
        ),
    }

    def generate(
        self,
        missing_skills: list[str],
        skill_details: dict[str, dict[str, str]] | None = None,
        duration_days: int = 90,
    ) -> list[RoadmapItem]:
        """Generate a prioritized roadmap for missing skills."""
        skill_details = skill_details or {}
        if not missing_skills:
            return [
                RoadmapItem(
                    day_range=f"Days 1-{min(duration_days, 30)}",
                    skill="Portfolio Strengthening",
                    objective="Improve depth and interview storytelling for existing skills.",
                    recommended_practice="Refine two projects, add tests, and publish documentation.",
                    estimated_hours=8,
                    deliverable="Polished portfolio project with README and deployment link.",
                    priority="Medium",
                )
            ]

        ordered_skills = sorted(
            missing_skills,
            key=lambda skill: (
                self.CATEGORY_ORDER.get(
                    skill_details.get(skill, {}).get("category", "Professional Skills"),
                    99,
                ),
                skill,
            ),
        )
        plan: list[RoadmapItem] = []
        day = 1
        for index, skill in enumerate(ordered_skills, start=1):
            if day > duration_days:
                break
            remaining_days = max(1, duration_days - day + 1)
            days_for_skill = self._days_for_skill(
                skill, remaining_days, len(ordered_skills) - index + 1
            )
            practice, deliverable = self.PRACTICE_LIBRARY.get(
                skill, self._default_practice(skill)
            )
            plan.append(
                RoadmapItem(
                    day_range=f"Days {day}-{min(duration_days, day + days_for_skill - 1)}",
                    skill=skill,
                    objective=self._objective(skill, skill_details),
                    recommended_practice=practice,
                    estimated_hours=self._hours(skill),
                    deliverable=deliverable,
                    priority=self._priority(index),
                )
            )
            day += days_for_skill
        return plan

    def generate_multi_duration(
        self,
        missing_skills: list[str],
        skill_details: dict[str, dict[str, str]] | None = None,
    ) -> dict[str, list[RoadmapItem]]:
        """Generate 30, 60, and 90 day roadmap variants."""
        return {
            "30 day roadmap": self.generate(
                missing_skills, skill_details, duration_days=30
            ),
            "60 day roadmap": self.generate(
                missing_skills, skill_details, duration_days=60
            ),
            "90 day roadmap": self.generate(
                missing_skills, skill_details, duration_days=90
            ),
        }

    @staticmethod
    def _days_for_skill(skill: str, remaining_days: int, remaining_skills: int) -> int:
        """Allocate more days to complex technical skills."""
        base = max(1, remaining_days // remaining_skills)
        if skill in {
            "Machine Learning",
            "Deep Learning",
            "Generative AI",
            "System Design",
            "Cloud Computing",
            "AWS",
            "Azure",
            "Data Structures",
            "Algorithms",
        }:
            return min(remaining_days, max(base + 2, 4))
        if skill in {
            "Python",
            "Java",
            "C++",
            "SQL",
            "React",
            "NodeJS",
            "Docker",
            "Kubernetes",
        }:
            return min(remaining_days, max(base + 1, 3))
        return min(remaining_days, base)

    @staticmethod
    def _objective(skill: str, skill_details: dict[str, dict[str, str]]) -> str:
        """Create a learning objective for a skill."""
        category = skill_details.get(skill, {}).get("category", "Professional Skill")
        return f"Build practical {category.lower()} capability in {skill} through guided practice and a portfolio artifact."

    @staticmethod
    def _hours(skill: str) -> int:
        """Estimate completion time in hours."""
        high_hours = {
            "Machine Learning",
            "Deep Learning",
            "Generative AI",
            "System Design",
            "Cloud Computing",
            "AWS",
            "Azure",
            "Kubernetes",
        }
        medium_hours = {
            "Python",
            "Java",
            "C++",
            "SQL",
            "React",
            "NodeJS",
            "Docker",
            "Data Structures",
            "Algorithms",
            "MLOps",
            "Computer Vision",
            "NLP",
        }
        if skill in high_hours:
            return 24
        if skill in medium_hours:
            return 16
        return 10

    @staticmethod
    def _priority(index: int) -> str:
        """Return priority label based on roadmap position."""
        if index == 1:
            return "Critical"
        if index <= 3:
            return "High"
        return "Medium"

    @staticmethod
    def _default_practice(skill: str) -> tuple[str, str]:
        """Default practice and deliverable for skills not in the practice library."""
        return (
            f"Study {skill} fundamentals, complete hands-on exercises, and document mistakes.",
            f"Create a small {skill} project artifact with screenshots and source code.",
        )
