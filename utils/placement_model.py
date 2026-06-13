"""Placement probability and interview readiness prediction wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from .config import DEFAULT_MODEL_PATH
from .models import ReadinessReport
from .readiness_calculator import ReadinessCalculator


class PlacementPredictor:
    """Load and use the serialized ML placement predictor."""

    FEATURE_COLUMNS = [
        "experience_years",
        "project_count",
        "certification_count",
        "skill_match_score",
        "project_relevance_score",
        "company_fit_score",
    ]

    def __init__(self, model_path: str | Path = DEFAULT_MODEL_PATH) -> None:
        self.model_path = Path(model_path)
        self.model: dict[str, Any] | None = None
        self.calculator = ReadinessCalculator()

    def load(self) -> None:
        """Load the serialized model bundle if available."""
        if not self.model_path.exists():
            self.model = None
            return
        try:
            self.model = joblib.load(self.model_path)
        except Exception:  # noqa: BLE001 - fallback keeps the app usable.
            self.model = None

    def predict(self, feature_values: dict[str, float]) -> tuple[float, float]:
        """Predict placement probability and interview readiness.

        The serialized model contains classifier and regressor pipelines. If the model
        file is missing, a deterministic heuristic fallback is used.
        """
        self.load()
        if self.model is None:
            return self._heuristic_predict(feature_values)

        feature_vector = [
            [float(feature_values.get(column, 0.0)) for column in self.FEATURE_COLUMNS]
        ]
        try:
            placement_classifier = self.model.get("placement_classifier")
            readiness_classifier = self.model.get("readiness_classifier")
            placement_regressor = self.model.get("placement_regressor")

            placement_probability = 0.0
            if placement_classifier is not None:
                placement_probability = float(
                    placement_classifier.predict_proba(feature_vector)[0][1]
                )
            elif placement_regressor is not None:
                placement_probability = float(
                    placement_regressor.predict(feature_vector)[0]
                )

            interview_readiness = 0.0
            if readiness_classifier is not None:
                interview_readiness = float(
                    readiness_classifier.predict_proba(feature_vector)[0][1] * 100.0
                )
            else:
                interview_readiness = self._heuristic_interview(feature_values)

            return self._clamp(placement_probability), self._clamp(interview_readiness)
        except (
            Exception
        ):  # noqa: BLE001 - keep production app resilient to model issues.
            return self._heuristic_predict(feature_values)

    def predict_from_report(
        self,
        report: ReadinessReport,
        project_count: int,
        certification_count: int,
        experience_years: float,
    ) -> tuple[float, float]:
        """Predict from a readiness report and resume signals."""
        return self.predict(
            {
                "experience_years": experience_years,
                "project_count": project_count,
                "certification_count": certification_count,
                "skill_match_score": report.technical_readiness_score,
                "project_relevance_score": report.project_readiness_score,
                "company_fit_score": 0.0,
            }
        )

    def _heuristic_predict(
        self, feature_values: dict[str, float]
    ) -> tuple[float, float]:
        """Fallback prediction when the serialized model is unavailable."""
        technical_score = float(feature_values.get("skill_match_score", 0.0))
        project_score = float(feature_values.get("project_relevance_score", 0.0))
        certification_score = min(
            100.0, float(feature_values.get("certification_count", 0.0)) * 30.0
        )
        experience_score = min(
            100.0, float(feature_values.get("experience_years", 0.0)) * 20.0
        )
        company_fit_score = float(feature_values.get("company_fit_score", 0.0))
        placement, interview = self.calculator.heuristic_prediction(
            technical_score=technical_score,
            project_score=project_score,
            certification_score=certification_score,
            experience_score=experience_score,
            company_fit_score=company_fit_score,
        )
        return placement, interview

    @staticmethod
    def _heuristic_interview(feature_values: dict[str, float]) -> float:
        """Fallback interview readiness score."""
        technical_score = float(feature_values.get("skill_match_score", 0.0))
        project_score = float(feature_values.get("project_relevance_score", 0.0))
        experience_score = min(
            100.0, float(feature_values.get("experience_years", 0.0)) * 20.0
        )
        company_fit_score = float(feature_values.get("company_fit_score", 0.0))
        return (
            (0.45 * technical_score)
            + (0.30 * project_score)
            + (0.15 * experience_score)
            + (0.10 * company_fit_score)
        )

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a prediction to the 0-100 range."""
        return float(max(0.0, min(100.0, value)))
