import joblib
import os
from pathlib import Path
from typing import Optional


_MODEL: Optional[object] = None
_VECT: Optional[object] = None


def _resolve_paths():
    candidates = [
        Path("ml/category_model.pkl"),
        Path(__file__).resolve().parent / "category_model.pkl",
        Path.cwd() / "ml" / "category_model.pkl",
    ]
    candidates_vec = [
        Path("ml/vectorizer.pkl"),
        Path(__file__).resolve().parent / "vectorizer.pkl",
        Path.cwd() / "ml" / "vectorizer.pkl",
    ]
    model_path = next((str(p) for p in candidates if p.exists()), None)
    vect_path = next((str(p) for p in candidates_vec if p.exists()), None)
    return model_path, vect_path


def _ensure_model_loaded() -> None:
    global _MODEL, _VECT
    if _MODEL is not None and _VECT is not None:
        return
    model_path, vect_path = _resolve_paths()
    if model_path and vect_path:
        try:
            _MODEL = joblib.load(model_path)
            _VECT = joblib.load(vect_path)
            return
        except Exception:
            _MODEL = None
            _VECT = None


def predict_category(note: str) -> str:
    _ensure_model_loaded()
    if _MODEL is not None and _VECT is not None:
        try:
            X = _VECT.transform([note or ""])
            return str(_MODEL.predict(X)[0])
        except Exception:
            pass

    # Fallback heuristic if model files are missing
    text = (note or "").lower()
    if any(k in text for k in ["restaurant", "food", "meal", "dinner", "lunch", "grocer"]):
        return "Food"
    if any(k in text for k in ["uber", "taxi", "flight", "bus", "train", "fuel", "gas"]):
        return "Travel"
    if any(k in text for k in ["electric", "water", "internet", "rent", "bill", "utility"]):
        return "Bills"
    if any(k in text for k in ["amazon", "mall", "shopping", "clothes", "shoes"]):
        return "Shopping"
    return "Other"
