"""Central path configuration for the project."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATABASE_DIR = PROJECT_ROOT / "database"
RESUMES_DIR = PROJECT_ROOT / "resumes"
ASSETS_DIR = PROJECT_ROOT / "assets"
COMPANY_DATA_DIR = PROJECT_ROOT / "company_data"
TRAINING_DIR = PROJECT_ROOT / "training"

DEFAULT_DB_PATH = DATABASE_DIR / "career_roadmap.db"
DEFAULT_MODEL_PATH = MODELS_DIR / "placement_predictor.pkl"


def ensure_directories() -> None:
    """Create runtime directories if they are missing."""
    for directory in [
        DATA_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        DATABASE_DIR,
        RESUMES_DIR,
        ASSETS_DIR,
        COMPANY_DATA_DIR,
        TRAINING_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
