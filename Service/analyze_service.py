from Service.ml_signal        import ml_signal
from Service.factcheck_signal import factcheck_signal
from Service.wikipedia_signal import wikipedia_signal
from Service.kb_signal        import kb_signal

ML_WEIGHT        = 0.35
WIKIPEDIA_WEIGHT = 0.30
FACTCHECK_WEIGHT = 0.25
KB_WEIGHT        = 0.10

RATING_TO_FAKE_PROB = {
    "true":          0.05,
    "mostly true":   0.15,
    "half true":     0.45,
    "mixture":       0.50,
    "mostly false":  0.75,
    "false":         0.95,
    "pants on fire": 1.00,
}


def _factcheck_to_fake_prob(fc: dict) -> float | None:
    if not fc["found"] or not fc["label"]:
        return None

    normalised = fc["label"].lower().strip()
    for key, prob in RATING_TO_FAKE_PROB.items():
        if key in normalised:
            return prob

    return 0.5


def _resolve_conflict(ml_fake_prob: float, wiki_fake_prob: float, fc_fake_prob: float | None, kb_fake_prob: float | None) -> float:
    """
    If ML strongly disagrees with other signals, cap its influence
    instead of letting it dominate.
    """
    ml_says_real   = ml_fake_prob < 0.4
    wiki_says_fake = wiki_fake_prob > 0.6
    fc_says_fake   = fc_fake_prob is not None and fc_fake_prob > 0.6
    kb_says_fake   = kb_fake_prob is not None and kb_fake_prob > 0.6

    if ml_says_real and wiki_says_fake:
        ml_fake_prob = max(ml_fake_prob, 0.45)

    if ml_says_real and fc_says_fake:
        ml_fake_prob = max(ml_fake_prob, 0.45)

    if ml_says_real and kb_says_fake:
        # KB is a hard fact match — if KB says fake, cap ML more aggressively
        ml_fake_prob = max(ml_fake_prob, 0.55)

    return ml_fake_prob


def analyze_text(text: str) -> dict:
    """
    Runs ML model + Wikipedia + Google Fact Check + Knowledge Base signals
    and combines them into a final verdict.

    Returns:
        {
            "label":      "REAL" | "FAKE" | "UNCERTAIN",
            "confidence": float (0-1),
            "ml_model":   { "label": ..., "score": ... },
            "wikipedia":  { "found": ..., "matched": ..., "summary": ..., "credible": ..., "fake_prob": ... },
            "fact_check": { "found": ..., "label": ..., "source": ... },
            "knowledge_base": { "found": ..., "subject": ..., "claimed": ..., "actual": ..., "match": ..., "fake_prob": ... },
        }
    """
    ml   = ml_signal(text)
    wiki = wikipedia_signal(text)
    fc   = factcheck_signal(text)
    kb   = kb_signal(text)

    # ── UNCERTAIN guard ───────────────────────────────────────────────────────
    if ml["label"] == "UNCERTAIN":
        return {
            "label":          "UNCERTAIN",
            "confidence":     0.5,
            "ml_model":       ml,
            "wikipedia":      wiki,
            "fact_check":     fc,
            "knowledge_base": kb,
        }

    # ── convert each signal to a fake probability ─────────────────────────────
    ml_fake_prob   = ml["score"] if ml["label"] == "FAKE" else 1.0 - ml["score"]
    wiki_fake_prob = wiki["fake_prob"]
    fc_fake_prob   = _factcheck_to_fake_prob(fc)
    kb_fake_prob   = kb["fake_prob"] if kb["found"] else None

    # ── conflict resolution before combining ──────────────────────────────────
    ml_fake_prob = _resolve_conflict(ml_fake_prob, wiki_fake_prob, fc_fake_prob, kb_fake_prob)

    # ── weighted combination ──────────────────────────────────────────────────
    # only include signals that actually found something (kb and fc)
    # if they found nothing → redistribute their weight proportionally

    active_weights = {
        "ml":   ML_WEIGHT,
        "wiki": WIKIPEDIA_WEIGHT,
    }
    active_probs = {
        "ml":   ml_fake_prob,
        "wiki": wiki_fake_prob,
    }

    if fc_fake_prob is not None:
        active_weights["fc"] = FACTCHECK_WEIGHT
        active_probs["fc"]   = fc_fake_prob

    if kb_fake_prob is not None:
        active_weights["kb"] = KB_WEIGHT
        active_probs["kb"]   = kb_fake_prob

    # normalise weights so they always sum to 1.0
    total_weight       = sum(active_weights.values())
    combined_fake_prob = sum(
        active_probs[k] * (active_weights[k] / total_weight)
        for k in active_weights
    )

    # ── derive final label + confidence ───────────────────────────────────────
    if combined_fake_prob >= 0.5:
        label      = "FAKE"
        confidence = combined_fake_prob
    else:
        label      = "REAL"
        confidence = 1.0 - combined_fake_prob

    return {
        "label":          label,
        "confidence":     round(confidence, 4),
        "ml_model":       ml,
        "wikipedia":      wiki,
        "fact_check":     fc,
        "knowledge_base": kb,
    }