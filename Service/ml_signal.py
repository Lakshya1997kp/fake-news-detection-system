import os
import re
import pickle
import threading

_lock       = threading.Lock()
_model      = None
_vectorizer = None

_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, "fake_news_model.pkl")
_VEC_PATH   = os.path.join(_BASE_DIR, "vectorizer.pkl")


def _load_artifacts():
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        with _lock:
            if _model is None or _vectorizer is None:
                with open(_MODEL_PATH, "rb") as f:
                    _model = pickle.load(f)
                with open(_VEC_PATH, "rb") as f:
                    _vectorizer = pickle.load(f)
    return _model, _vectorizer


def _is_meaningful_text(text: str) -> bool:
    words = re.findall(r'[a-zA-Z]{3,}', text)
    return len(words) >= 10


def ml_signal(text: str) -> dict:
    if not _is_meaningful_text(text):
        return {"label": "UNCERTAIN", "score": 0.5}

    model, vectorizer = _load_artifacts()

    features   = vectorizer.transform([text])
    prediction = int(model.predict(features)[0])
    proba      = model.predict_proba(features)[0]

    label_map = {0: "FAKE", 1: "REAL"}
    label     = label_map.get(prediction, "UNCERTAIN")

    if label == "UNCERTAIN":
        return {"label": "UNCERTAIN", "score": 0.5}

    score = float(proba[prediction])

    return {
        "label": label,
        "score": round(score, 4),
    }