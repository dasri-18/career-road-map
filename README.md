# AI Career Roadmap Generator

AI Career Roadmap Generator is a production-ready Python application that helps students evaluate their career readiness for a target company and generates a personalized learning roadmap.

## Features

- Upload and parse PDF resumes
- Extract skills, education, projects, certifications, and experience
- Compare resume skills against company requirements
- Generate missing skills, matching skills, and skill gap percentage
- Predict readiness scores and placement probability
- Create 30-day, 60-day, and 90-day learning roadmaps
- Recommend relevant projects based on missing skills
- Store user profiles and analysis history in SQLite
- Export PDF reports
- Streamlit dashboard with visual analytics

## Project Structure

```
career-roadmap-generator/
├── app.py
├── requirements.txt
├── README.md
├── data/
├── models/
├── reports/
├── database/
├── resumes/
├── assets/
├── utils/
├── pages/
├── company_data/
├── training/
├── tests/
```

## Installation

1. Create and activate a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate       # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download NLTK data:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

4. Optionally install the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

## Running the App

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

On Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL displayed in your terminal.

## Example Usage and Exporting Reports

1. Open the app in your browser after running `streamlit run app.py`.
2. Upload a PDF resume and choose a target company.
3. Fill in your name, email, target role, and education level.
4. Click `Analyze career readiness`.
5. Review the dashboard charts, readiness scores, and recommended roadmap.
6. Click `Download PDF report` to export a desktop-ready report.

## Data and Training

- `data/sample_dataset.csv`: sample placement readiness training data
- `training/train_model.py`: script to train and persist a placement predictor model
- `models/placement_predictor.pkl`: serialized model used by the app

## Architecture

- `app.py`: Streamlit frontend and orchestration
- `utils/`: reusable components and services
- `company_data/`: structured JSON company requirements
- `database/`: SQLite persistence
- `reports/`: generated PDF reports
- `resumes/`: uploaded resumes
- `training/`: training dataset and scripts
- `tests/`: unit tests

## Retraining the Model

```bash
python training/train_model.py
```

This generates or refreshes `models/placement_predictor.pkl`.

## Developer Setup

To install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests with:

```bash
python -m pytest tests -q
```

Format code with `black` and lint with `ruff` after installing dependencies.

## Notes

- The app is designed for resume PDF upload and company matching.
- Custom company options are supported through the Streamlit interface.
- The database file `database/career_roadmap.db` is created automatically.
