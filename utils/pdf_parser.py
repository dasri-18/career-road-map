"""PDF resume parsing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from PyPDF2 import PdfReader
except (
    ImportError
) as exc:  # pragma: no cover - dependency is declared in requirements.txt
    PdfReader = None  # type: ignore[assignment]
    PDF_IMPORT_ERROR = exc
else:
    PDF_IMPORT_ERROR = None

from .models import ResumeProfile
from .skill_extractor import SkillExtractor


class PDFResumeParser:
    """Extract structured information from PDF resumes."""

    def __init__(self, skill_extractor: Optional[SkillExtractor] = None) -> None:
        self.skill_extractor = skill_extractor or SkillExtractor()

    def extract_text(self, pdf_path: str | Path) -> str:
        """Extract plain text from a PDF resume.

        Raises:
            FileNotFoundError: When the PDF path does not exist.
            ValueError: When the file is not a PDF or PyPDF2 is unavailable.
        """
        if PDF_IMPORT_ERROR is not None:
            raise ValueError(
                "PyPDF2 is required for PDF parsing. Install requirements first."
            ) from PDF_IMPORT_ERROR

        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF resumes are supported.")

        try:
            reader = PdfReader(str(path))
            pages = []
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                pages.append(f"\n--- Page {page_number} ---\n{text}")
            return "\n".join(pages).strip()
        except Exception as exc:  # noqa: BLE001 - preserve a user-facing parsing error.
            raise ValueError(f"Unable to parse PDF resume: {exc}") from exc

    def parse_file(self, pdf_path: str | Path) -> ResumeProfile:
        """Parse a PDF resume into a structured profile."""
        text = self.extract_text(pdf_path)
        return self.parse_text(text)

    def parse_text(self, text: str) -> ResumeProfile:
        """Parse raw resume text into a structured profile."""
        return self.skill_extractor.extract_resume_profile(text)
