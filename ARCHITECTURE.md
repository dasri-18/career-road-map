# AI Career Roadmap Generator Architecture

## Overview

This project uses a modular design to separate core concerns:

- `app.py`: Streamlit UI layer and orchestration.
- `utils/`: reusable business logic and data handling.
- `company_data/`: JSON-driven company requirements.
- `database/`: SQLite persistence layer.
- `training/`: model training script and sample dataset.
- `models/`: serialized ML artifacts.
- `reports/`: generated PDF output.
- `resumes/`: stored uploaded resumes.

## Component Diagram

1. User uploads a resume PDF via Streamlit.
2. `PDFResumeParser` uses `PyPDF2` to extract text.
3. `SkillExtractor` analyzes the text for skills, education, projects, certifications, and experience.
4. `CompanyRequirementRepository` loads company requirements from JSON.
5. `SkillGapAnalyzer` compares resume skills to company expectations.
6. `ReadinessCalculator` creates a readiness report from match data.
7. `RoadmapGenerator` builds personalized learning plans.
8. `ProjectRecommendationEngine` recommends projects for missing skills.
9. `PlacementPredictor` loads a serialized model or fallback heuristic to estimate placement probability.
10. `ReportGenerator` exports a polished PDF report.
11. `SQLiteRepository` persists user profiles, uploads, analyses, and reports.

## Data Flow

- Input: resume PDF, user profile, company selection.
- Processing: text extraction, NLP skill parsing, TF-IDF analyses, roadmap generation.
- Output: dashboard visualizations, reports, and database history.

## Training

- `training/train_model.py` trains both classification and regression pipelines from `data/sample_dataset.csv`.
- The serialized model is saved to `models/placement_predictor.pkl`.

## Deployment

- Run the app with `streamlit run app.py`.
- Ensure `requirements.txt` is installed and required NLTK/spaCy assets are available.

## Extensibility

- Add new company profiles to `company_data/` as JSON objects.
- Update `SkillExtractor` with additional skill aliases.
- Extend the `RoadmapGenerator` practice library for new skills.
- Add new visualization pages under `pages/` and `tests/`.
