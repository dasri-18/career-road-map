"""Generate downloadable PDF and text reports for career readiness analysis."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from .config import REPORTS_DIR

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except ImportError as exc:  # pragma: no cover
    REPORTLAB_IMPORT_ERROR = exc
    colors = None  # type: ignore[assignment]
    letter = None  # type: ignore[assignment]
    getSampleStyleSheet = None  # type: ignore[assignment]
    Paragraph = None  # type: ignore[assignment]
    SimpleDocTemplate = None  # type: ignore[assignment]
    Spacer = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]
    TableStyle = None  # type: ignore[assignment]
else:
    REPORTLAB_IMPORT_ERROR = None


class ReportGenerator:
    """Create PDF and text-based reports for analysis results."""

    def __init__(self, reports_dir: str | Path = REPORTS_DIR) -> None:
        self.reportlab_error = REPORTLAB_IMPORT_ERROR
        if self.reportlab_error is not None:
            return
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def create_pdf(
        self,
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
        """Create a PDF report from analysis results."""
        if self.reportlab_error is not None:
            raise RuntimeError(
                "ReportLab is required to generate PDF reports. Install it in the active Python environment."
            ) from self.reportlab_error
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("AI Career Roadmap Generator Report", styles["Title"]),
            Spacer(1, 12),
        ]

        story.append(Paragraph(f"Candidate: {candidate_name}", styles["Heading2"]))
        story.append(Paragraph(f"Email: {email or 'N/A'}", styles["Normal"]))
        story.append(
            Paragraph(f"Target Role: {target_role or 'N/A'}", styles["Normal"])
        )
        story.append(Paragraph(f"Target Company: {company_name}", styles["Normal"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Readiness Summary", styles["Heading3"]))
        story.append(Paragraph(readiness_report.summary, styles["Normal"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Readiness Scores", styles["Heading3"]))
        story.append(self._build_scores_table(readiness_report))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Skill Match", styles["Heading3"]))
        story.append(self._build_skill_table(skill_match))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Learning Roadmap", styles["Heading3"]))
        for label, items in roadmap.items():
            story.append(Paragraph(label.title(), styles["Heading4"]))
            for item in items:
                story.append(
                    Paragraph(f"{item.day_range}: {item.skill}", styles["Bullet"])
                )
                story.append(Paragraph(item.objective, styles["Normal"]))
                story.append(
                    Paragraph(
                        f"Practice: {item.recommended_practice}", styles["Normal"]
                    )
                )
                story.append(
                    Paragraph(f"Deliverable: {item.deliverable}", styles["Normal"])
                )
                story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Project Recommendations", styles["Heading3"]))
        for project in recommendations:
            story.append(Paragraph(project.title, styles["Heading4"]))
            story.append(Paragraph(project.description, styles["Normal"]))
            story.append(
                Paragraph(
                    f"Skills covered: {', '.join(project.skills_covered)}",
                    styles["Normal"],
                )
            )
            story.append(
                Paragraph(
                    f"Estimated hours: {project.estimated_hours}", styles["Normal"]
                )
            )
            story.append(Spacer(1, 6))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    @staticmethod
    def _build_scores_table(report: Any) -> Table:
        """Create a table for readiness scores."""
        data = [
            ["Metric", "Value"],
            ["Overall readiness", f"{report.overall_readiness_score:.1f}%"],
            ["Technical readiness", f"{report.technical_readiness_score:.1f}%"],
            ["Project readiness", f"{report.project_readiness_score:.1f}%"],
            ["Certification score", f"{report.certification_score:.1f}%"],
            ["Experience score", f"{report.experience_score:.1f}%"],
            ["Placement probability", f"{report.placement_probability:.1f}%"],
            ["Interview readiness", f"{report.interview_readiness:.1f}%"],
            ["Readiness level", report.readiness_level],
        ]
        table = Table(data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4B8BBE")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ]
            )
        )
        return table

    @staticmethod
    def _build_skill_table(skill_match: Any) -> Table:
        """Create a table for skill matching results."""
        data = [
            ["Category", "Skills"],
            ["Matching skills", ", ".join(skill_match.matching_skills) or "None"],
            [
                "Missing required skills",
                ", ".join(skill_match.missing_required_skills) or "None",
            ],
            [
                "Missing preferred skills",
                ", ".join(skill_match.missing_preferred_skills) or "None",
            ],
            ["Skill gap", f"{skill_match.skill_gap_percentage:.1f}%"],
            ["Company fit", f"{skill_match.company_fit_score:.1f}%"],
        ]
        table = Table(data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4B8BBE")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ]
            )
        )
        return table
