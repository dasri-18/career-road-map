"""Skill extraction and resume information detection engine."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

try:
    from nltk.tokenize import RegexpTokenizer
except (
    ImportError
):  # pragma: no cover - NLTK is optional at runtime but declared in requirements.
    RegexpTokenizer = None  # type: ignore[assignment]

from .models import ResumeProfile


@dataclass(frozen=True)
class SkillDefinition:
    """Definition used to identify a canonical skill in resume text."""

    canonical_name: str
    category: str
    keywords: tuple[str, ...]
    aliases: tuple[str, ...] = ()


class SkillExtractor:
    """Extract skills, education, projects, certifications, and experience from resumes."""

    def __init__(self, skill_database: Iterable[SkillDefinition] | None = None) -> None:
        self.skill_database = (
            list(skill_database) if skill_database else self._build_skill_database()
        )
        self._patterns = self._compile_patterns()

    def _build_skill_database(self) -> list[SkillDefinition]:
        """Create a broad domain skill database for student and professional resumes."""
        raw_skills: dict[str, tuple[str, tuple[str, ...]]] = {
            "Python": (
                "Programming Language",
                ("python", "django", "flask", "fastapi"),
            ),
            "Java": (
                "Programming Language",
                ("java", "spring boot", "springboot", "j2ee"),
            ),
            "C++": ("Programming Language", ("c++", "cpp", "qt")),
            "C": (
                "Programming Language",
                (
                    " c ",
                    "embedded c",
                ),
            ),
            "JavaScript": (
                "Programming Language",
                ("javascript", "js", "typescript", "ts"),
            ),
            "HTML": ("Frontend", ("html", "html5")),
            "CSS": ("Frontend", ("css", "scss", "sass", "tailwind")),
            "React": (
                "Frontend",
                ("react", "reactjs", "react.js", "redux", "next.js", "nextjs"),
            ),
            "Angular": ("Frontend", ("angular", "angularjs")),
            "Vue": ("Frontend", ("vue", "vuejs", "vue.js")),
            "NodeJS": (
                "Backend",
                ("nodejs", "node.js", "node js", "express", "expressjs"),
            ),
            "SQL": (
                "Database",
                ("sql", "mysql", "postgresql", "postgres", "sqlite", "mariadb"),
            ),
            "NoSQL": (
                "Database",
                ("nosql", "mongodb", "redis", "cassandra", "dynamodb"),
            ),
            "Machine Learning": (
                "AI / ML",
                (
                    "machine learning",
                    "ml",
                    "sklearn",
                    "scikit-learn",
                    "random forest",
                    "xgboost",
                ),
            ),
            "Deep Learning": (
                "AI / ML",
                (
                    "deep learning",
                    "tensorflow",
                    "pytorch",
                    "keras",
                    "neural network",
                    "cnn",
                    "rnn",
                    "transformer",
                ),
            ),
            "NLP": (
                "AI / ML",
                (
                    "nlp",
                    "natural language processing",
                    "sentiment analysis",
                    "named entity recognition",
                    "text classification",
                    "spaCy",
                    "spacy",
                ),
            ),
            "Computer Vision": (
                "AI / ML",
                (
                    "computer vision",
                    "opencv",
                    "image classification",
                    "object detection",
                    "yolo",
                ),
            ),
            "Generative AI": (
                "AI / ML",
                (
                    "generative ai",
                    "llm",
                    "large language model",
                    "prompt engineering",
                    "rag",
                    "retrieval augmented generation",
                    "langchain",
                    "openai",
                    "gpt",
                ),
            ),
            "Data Structures": (
                "Computer Science Fundamentals",
                (
                    "data structures",
                    "arrays",
                    "linked list",
                    "trees",
                    "graphs",
                    "hash map",
                    "heap",
                    "stack",
                    "queue",
                ),
            ),
            "Algorithms": (
                "Computer Science Fundamentals",
                (
                    "algorithms",
                    "dynamic programming",
                    "greedy",
                    "sorting",
                    "searching",
                    "big o",
                    "complexity",
                ),
            ),
            "System Design": (
                "Engineering Practice",
                (
                    "system design",
                    "distributed systems",
                    "scalability",
                    "microservices",
                    "load balancing",
                    "api design",
                ),
            ),
            "Cloud Computing": (
                "Cloud / DevOps",
                (
                    "cloud computing",
                    "cloud",
                    "serverless",
                    "iac",
                    "infrastructure as code",
                ),
            ),
            "AWS": (
                "Cloud / DevOps",
                (
                    "aws",
                    "amazon web services",
                    "ec2",
                    "s3",
                    "lambda",
                    "rds",
                    "iam",
                    "cloudwatch",
                ),
            ),
            "Azure": (
                "Cloud / DevOps",
                ("azure", "microsoft azure", "azure functions", "azure devops"),
            ),
            "GCP": (
                "Cloud / DevOps",
                ("gcp", "google cloud", "bigquery", "cloud run", "vertex ai"),
            ),
            "Git": (
                "DevOps / Collaboration",
                ("git", "github", "gitlab", "bitbucket", "version control"),
            ),
            "Docker": ("Cloud / DevOps", ("docker", "containerization", "containers")),
            "Kubernetes": ("Cloud / DevOps", ("kubernetes", "k8s", "helm")),
            "CI/CD": (
                "Cloud / DevOps",
                (
                    "ci/cd",
                    "continuous integration",
                    "continuous deployment",
                    "jenkins",
                    "github actions",
                    "gitlab ci",
                ),
            ),
            "Linux": (
                "Operating Systems",
                ("linux", "ubuntu", "bash", "shell scripting"),
            ),
            "Data Analysis": (
                "Data",
                (
                    "data analysis",
                    "exploratory data analysis",
                    "eda",
                    "pandas",
                    "numpy",
                    "matplotlib",
                    "seaborn",
                ),
            ),
            "Data Visualization": (
                "Data",
                ("data visualization", "plotly", "tableau", "power bi", "dashboards"),
            ),
            "Statistics": (
                "Data Science",
                (
                    "statistics",
                    "probability",
                    "hypothesis testing",
                    "regression",
                    "bayesian",
                ),
            ),
            "MLOps": (
                "AI / ML",
                (
                    "mlops",
                    "model deployment",
                    "mlflow",
                    "model monitoring",
                    "feature store",
                ),
            ),
            "Agile": (
                "Engineering Practice",
                ("agile", "scrum", "kanban", "sprint", "jira"),
            ),
            "Communication": (
                "Professional Skills",
                (
                    "communication",
                    "presentation",
                    "stakeholder management",
                    "documentation",
                ),
            ),
            "Problem Solving": (
                "Professional Skills",
                ("problem solving", "analytical thinking", "critical thinking"),
            ),
            "Leadership": (
                "Professional Skills",
                ("leadership", "team lead", "mentoring"),
            ),
            "Product Management": (
                "Business / Product",
                ("product management", "roadmap", "user stories", "stakeholders"),
            ),
            "Cybersecurity": (
                "Security",
                (
                    "cybersecurity",
                    "security",
                    "penetration testing",
                    "owasp",
                    "network security",
                ),
            ),
            "Blockchain": (
                "Emerging Technology",
                ("blockchain", "solidity", "web3", "smart contracts"),
            ),
            "IoT": (
                "Emerging Technology",
                ("iot", "internet of things", "arduino", "raspberry pi", "mqtt"),
            ),
            "Mobile Development": (
                "Mobile",
                (
                    "mobile development",
                    "android",
                    "ios",
                    "flutter",
                    "react native",
                    "kotlin",
                    "swift",
                ),
            ),
            "UI/UX Design": (
                "Design",
                ("ui/ux", "ux", "figma", "wireframing", "prototyping", "user research"),
            ),
            "REST APIs": (
                "Backend",
                ("rest api", "rest apis", "api", "http", "graphql"),
            ),
            "Testing": (
                "Quality",
                (
                    "testing",
                    "unit testing",
                    "integration testing",
                    "pytest",
                    "selenium",
                    "automation testing",
                ),
            ),
            "ETL": (
                "Data Engineering",
                ("etl", "data pipeline", "airflow", "spark", "data warehouse", "dbt"),
            ),
            "Excel": ("Business Tools", ("excel", "ms excel", "vba", "pivot table")),
            "SAP": ("Enterprise", ("sap", "sap mm", "sap sd", "sap fico")),
            "Salesforce": ("Enterprise", ("salesforce", "crm", "apex", "lightning")),
            "Power BI": ("Data Visualization", ("power bi", "dax", "powerbi")),
            "Tableau": ("Data Visualization", ("tableau", "tableau desktop")),
            ".NET": ("Backend", (".net", "c#", "asp.net", "dotnet")),
            "PHP": ("Backend", ("php", "laravel", "wordpress")),
            "Ruby": ("Backend", ("ruby", "ruby on rails", "rails")),
            "Go": ("Programming Language", ("golang", "go language")),
            "Rust": ("Programming Language", ("rust", "rustlang")),
            "Scala": ("Programming Language", ("scala", "spark scala")),
            "R": ("Data Science", ("r programming", "r language")),
            "MATLAB": ("Data Science", ("matlab", "simulink")),
            "Embedded Systems": (
                "Hardware",
                ("embedded systems", "microcontrollers", "rtos", "firmware"),
            ),
            "Robotics": ("Hardware", ("robotics", "ros", "robot operating system")),
            "Business Analysis": (
                "Business / Product",
                ("business analysis", "requirements gathering", "process mapping"),
            ),
            "Consulting": (
                "Business / Product",
                ("consulting", "strategy", "client management"),
            ),
            "Finance": (
                "Domain Knowledge",
                ("finance", "financial modeling", "risk analysis", "investment"),
            ),
            "Healthcare Analytics": (
                "Domain Knowledge",
                ("healthcare analytics", "clinical data", "medical imaging"),
            ),
            "Digital Marketing": (
                "Marketing",
                ("digital marketing", "seo", "sem", "google analytics", "campaigns"),
            ),
        }
        return [
            SkillDefinition(
                canonical_name=name, category=category, keywords=keywords, aliases=()
            )
            for name, (category, keywords) in raw_skills.items()
        ]

    def _compile_patterns(self) -> dict[str, re.Pattern[str]]:
        """Compile regular expressions for each canonical skill."""
        patterns: dict[str, re.Pattern[str]] = {}
        for definition in self.skill_database:
            keyword_patterns = []
            for keyword in (*definition.keywords, *definition.aliases):
                normalized = self.normalize_text(keyword)
                if definition.canonical_name == "C++":
                    keyword_patterns.append(r"\bC\+\+")
                elif definition.canonical_name == "C":
                    keyword_patterns.append(r"\bC\b")
                elif definition.canonical_name == "NodeJS":
                    keyword_patterns.append(r"\bNode\.?JS\b|\bNode\s*JS\b")
                elif definition.canonical_name == "CI/CD":
                    keyword_patterns.append(
                        r"\bCI\s*/\s*CD\b|\bcontinuous integration\b|\bcontinuous deployment\b"
                    )
                elif definition.canonical_name == ".NET":
                    keyword_patterns.append(r"\.NET\b|\bC#\b|\bASP\.NET\b|\bdotnet\b")
                elif definition.canonical_name == "Go":
                    keyword_patterns.append(r"\bGolang\b|\bGo language\b")
                elif definition.canonical_name == "REST APIs":
                    keyword_patterns.append(
                        r"\bREST\s*APIs?\b|\bAPI design\b|\bGraphQL\b"
                    )
                elif definition.canonical_name == "Power BI":
                    keyword_patterns.append(r"\bPower\s*BI\b|\bDAX\b")
                elif definition.canonical_name == "UI/UX Design":
                    keyword_patterns.append(
                        r"\bUI\s*/\s*UX\b|\bUX\b|\bFigma\b|\bwireframing\b|\bprototyping\b"
                    )
                else:
                    escaped = re.escape(normalized)
                    keyword_patterns.append(rf"\b{escaped}\b")
            patterns[definition.canonical_name] = re.compile(
                "|".join(keyword_patterns), re.IGNORECASE
            )
        return patterns

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize resume text for deterministic matching."""
        normalized = text.lower().replace("+", " plus ")
        normalized = re.sub(r"\bnode\s*js\b", "nodejs", normalized)
        normalized = re.sub(r"\.net", " dotnet ", normalized)
        normalized = re.sub(r"[^a-z0-9#\.\+\s/-]+", " ", normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    def extract_skills(self, text: str) -> list[str]:
        """Return canonical skills detected in resume text."""
        normalized = self.normalize_text(text)
        detected: list[str] = []
        for definition in self.skill_database:
            pattern = self._patterns[definition.canonical_name]
            if pattern.search(normalized):
                detected.append(definition.canonical_name)
        return detected

    def extract_skill_details(self, text: str) -> dict[str, dict[str, str]]:
        """Return detected skills with category and supporting evidence."""
        normalized = self.normalize_text(text)
        details: dict[str, dict[str, str]] = {}
        for definition in self.skill_database:
            pattern = self._patterns[definition.canonical_name]
            match = pattern.search(normalized)
            if not match:
                continue
            evidence = self._extract_evidence(text, match.group(0))
            details[definition.canonical_name] = {
                "category": definition.category,
                "evidence": evidence,
            }
        return details

    def detect_education(self, text: str) -> list[str]:
        """Detect education degrees, institutions, and fields from resume text."""
        normalized = self.normalize_text(text)
        education: list[str] = []
        degree_patterns = [
            r"\b(?:b\.?tech|b\.?e\.?|b\.?sc|b\.?com|b\.?ba|b\.?des)\b[^.\n]{0,120}",
            r"\b(?:m\.?tech|m\.?e\.?|m\.?sc|m\.?com|m\.?ba|m\.?des|mba|pgdm|pgdba)\b[^.\n]{0,120}",
            r"\bph\.?d\.?\b[^.\n]{0,120}",
            r"\bdiploma\b[^.\n]{0,120}",
            r"\bpolytechnic\b[^.\n]{0,120}",
        ]
        for pattern in degree_patterns:
            for match in re.finditer(pattern, normalized, re.IGNORECASE):
                education.append(match.group(0).strip())
        return list(dict.fromkeys(education))[:8]

    def detect_projects(self, text: str) -> list[str]:
        """Detect project titles or project-like lines from resume text."""
        normalized = self.normalize_text(text)
        section_match = re.search(
            r"(?:projects|academic projects|key projects|selected projects)(.*?)(?:certifications?|education|experience|skills|achievements|$)",
            normalized,
            flags=re.IGNORECASE | re.DOTALL,
        )
        project_text = section_match.group(1) if section_match else normalized
        project_lines = []
        for raw_line in re.split(r"\n|•|-|\d+\.", project_text):
            line = raw_line.strip()
            if len(line) < 12 or len(line) > 220:
                continue
            if re.search(
                r"\b(system|application|platform|model|engine|dashboard|website|web app|chatbot|classifier|detector|recommender|tool|prototype|solution|analysis)\b",
                line,
                re.IGNORECASE,
            ):
                project_lines.append(line[:180])
        return list(dict.fromkeys(project_lines))[:8]

    def detect_certifications(self, text: str) -> list[str]:
        """Detect known certifications and certification section entries."""
        normalized = self.normalize_text(text)
        known = [
            "AWS Certified Solutions Architect",
            "AWS Certified Cloud Practitioner",
            "Microsoft Azure Fundamentals",
            "Azure Administrator",
            "Google Cloud Professional",
            "TensorFlow Developer Certificate",
            "Machine Learning Specialization",
            "Deep Learning Specialization",
            "Data Science Professional Certificate",
            "Cisco CCNA",
            "Certified Kubernetes Administrator",
            "Docker Certified Associate",
            "Scrum Master",
            "ISTQB",
            "Salesforce Administrator",
            "Power BI Data Analyst",
            "Tableau Desktop Specialist",
            "Oracle Certified Professional",
            "Microsoft Certified: Azure AI Engineer",
        ]
        certifications: list[str] = []
        for cert in known:
            if re.search(
                rf"\b{re.escape(self.normalize_text(cert))}\b",
                normalized,
                re.IGNORECASE,
            ):
                certifications.append(cert)
        section_match = re.search(
            r"certifications?(.*?)(?:projects|education|experience|skills|achievements|$)",
            normalized,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if section_match:
            for raw_line in re.split(r"\n|•|-", section_match.group(1)):
                line = raw_line.strip()
                if 8 <= len(line) <= 140 and line.lower() not in {
                    "certifications",
                    "certification",
                }:
                    certifications.append(line)
        return list(dict.fromkeys(certifications))[:10]

    def detect_experience_years(self, text: str) -> float:
        """Estimate years of experience from resume text."""
        normalized = self.normalize_text(text)
        patterns = [
            r"\b(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)\b",
            r"\b(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*of\s*experience\b",
            r"\bexperience\s*[:\-]\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)\b",
        ]
        matches: list[float] = []
        for pattern in patterns:
            matches.extend(
                float(match)
                for match in re.findall(pattern, normalized, flags=re.IGNORECASE)
            )
        return max(matches) if matches else 0.0

    def extract_resume_profile(self, text: str) -> ResumeProfile:
        """Extract all supported resume entities into a dataclass."""
        return ResumeProfile(
            skills=self.extract_skills(text),
            education=self.detect_education(text),
            projects=self.detect_projects(text),
            certifications=self.detect_certifications(text),
            experience_years=self.detect_experience_years(text),
            raw_text=text,
        )

    @staticmethod
    def _extract_evidence(text: str, keyword: str) -> str:
        """Return a short sentence around a detected keyword."""
        normalized_keyword = re.escape(keyword.lower())
        sentences = re.split(r"(?<=[.!?])\s+|\n", text)
        for sentence in sentences:
            if re.search(normalized_keyword, sentence, re.IGNORECASE):
                return sentence.strip()[:240]
        return keyword
