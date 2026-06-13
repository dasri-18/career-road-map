"""SQLite persistence layer for profiles, resumes, analyses, and reports."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import DEFAULT_DB_PATH
from .models import ReadinessReport, ResumeProfile, SkillMatchResult


class SQLiteRepository:
    """Persist user activity and generated reports in SQLite."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_schema()

    def connect(self) -> sqlite3.Connection:
        """Open a SQLite connection with row access enabled."""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_schema(self) -> None:
        """Create all application tables if they do not exist."""
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    target_role TEXT,
                    education_level TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS resume_uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_profile_id INTEGER,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    extracted_text TEXT,
                    uploaded_at TEXT NOT NULL,
                    FOREIGN KEY(user_profile_id) REFERENCES user_profiles(id)
                );

                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_profile_id INTEGER,
                    resume_upload_id INTEGER,
                    company_name TEXT NOT NULL,
                    target_role TEXT,
                    matching_skills TEXT NOT NULL,
                    missing_required_skills TEXT NOT NULL,
                    missing_preferred_skills TEXT NOT NULL,
                    skill_match_score REAL NOT NULL,
                    skill_gap_percentage REAL NOT NULL,
                    company_fit_score REAL NOT NULL,
                    analyzed_at TEXT NOT NULL,
                    FOREIGN KEY(user_profile_id) REFERENCES user_profiles(id),
                    FOREIGN KEY(resume_upload_id) REFERENCES resume_uploads(id)
                );

                CREATE TABLE IF NOT EXISTS readiness_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER NOT NULL,
                    overall_readiness_score REAL NOT NULL,
                    technical_readiness_score REAL NOT NULL,
                    project_readiness_score REAL NOT NULL,
                    certification_score REAL NOT NULL,
                    experience_score REAL NOT NULL,
                    placement_probability REAL NOT NULL,
                    interview_readiness REAL NOT NULL,
                    readiness_level TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    report_path TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(analysis_id) REFERENCES analysis_history(id)
                );
                """
            )

    def save_user_profile(
        self,
        name: str,
        email: str | None = None,
        target_role: str | None = None,
        education_level: str | None = None,
    ) -> int:
        """Save or retrieve a user profile and return its id."""
        with self.connect() as connection:
            row = connection.execute(
                "SELECT id FROM user_profiles WHERE lower(name)=lower(?) AND COALESCE(email, '')=COALESCE(?, '')",
                (name, email),
            ).fetchone()
            if row:
                profile_id = int(row["id"])
                connection.execute(
                    "UPDATE user_profiles SET target_role=?, education_level=? WHERE id=?",
                    (target_role, education_level, profile_id),
                )
                return profile_id
            cursor = connection.execute(
                "INSERT INTO user_profiles(name, email, target_role, education_level, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, email, target_role, education_level, self._now()),
            )
            return int(cursor.lastrowid)

    def save_resume_upload(
        self,
        user_profile_id: int,
        file_name: str,
        file_path: str,
        extracted_text: str | None = None,
    ) -> int:
        """Save an uploaded resume record."""
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO resume_uploads(user_profile_id, file_name, file_path, extracted_text, uploaded_at) VALUES (?, ?, ?, ?, ?)",
                (user_profile_id, file_name, file_path, extracted_text, self._now()),
            )
            return int(cursor.lastrowid)

    def save_skill_analysis(
        self,
        user_profile_id: int,
        resume_upload_id: int | None,
        company_name: str,
        target_role: str | None,
        skill_match: SkillMatchResult,
    ) -> int:
        """Save skill gap analysis history."""
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO analysis_history(
                    user_profile_id, resume_upload_id, company_name, target_role,
                    matching_skills, missing_required_skills, missing_preferred_skills,
                    skill_match_score, skill_gap_percentage, company_fit_score, analyzed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_profile_id,
                    resume_upload_id,
                    company_name,
                    target_role,
                    json.dumps(skill_match.matching_skills),
                    json.dumps(skill_match.missing_required_skills),
                    json.dumps(skill_match.missing_preferred_skills),
                    skill_match.skill_match_score,
                    skill_match.skill_gap_percentage,
                    skill_match.company_fit_score,
                    self._now(),
                ),
            )
            return int(cursor.lastrowid)

    def save_readiness_report(
        self, analysis_id: int, report: ReadinessReport, report_path: str | None = None
    ) -> int:
        """Save a generated readiness report."""
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO readiness_reports(
                    analysis_id, overall_readiness_score, technical_readiness_score,
                    project_readiness_score, certification_score, experience_score,
                    placement_probability, interview_readiness, readiness_level,
                    summary, report_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    report.overall_readiness_score,
                    report.technical_readiness_score,
                    report.project_readiness_score,
                    report.certification_score,
                    report.experience_score,
                    report.placement_probability,
                    report.interview_readiness,
                    report.readiness_level,
                    report.summary,
                    report_path,
                    self._now(),
                ),
            )
            return int(cursor.lastrowid)

    def save_resume_profile(self, user_profile_id: int, profile: ResumeProfile) -> None:
        """Store extracted resume profile metadata as a convenience JSON payload."""
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS resume_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_profile_id INTEGER NOT NULL,
                    skills TEXT NOT NULL,
                    education TEXT NOT NULL,
                    projects TEXT NOT NULL,
                    certifications TEXT NOT NULL,
                    experience_years REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_profile_id) REFERENCES user_profiles(id)
                )
                """
            )
            connection.execute(
                "INSERT INTO resume_profiles(user_profile_id, skills, education, projects, certifications, experience_years, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    user_profile_id,
                    json.dumps(profile.skills),
                    json.dumps(profile.education),
                    json.dumps(profile.projects),
                    json.dumps(profile.certifications),
                    profile.experience_years,
                    self._now(),
                ),
            )

    def get_analysis_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Return recent analysis history."""
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM analysis_history ORDER BY analyzed_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_latest_reports(self, limit: int = 5) -> list[dict[str, Any]]:
        """Return recent readiness reports."""
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM readiness_reports ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _now() -> str:
        """Return an ISO UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()
