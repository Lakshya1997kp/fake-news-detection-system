import os
import requests
 
 
FACT_CHECK_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
 
 
def factcheck_signal(text: str) -> dict:
    """
    Returns:
        {
            "found":  bool,
            "label":  str | None,   e.g. "False", "Mostly False", "True"
            "source": str | None,   publisher name
        }
    """
    api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
 
    # ── stub: key not configured yet ──────────────────────────────────────────
    if not api_key:
        return {"found": False, "label": None, "source": None}
 
    query = text[:100].strip()
 
    try:
        resp = requests.get(
            FACT_CHECK_URL,
            params={"key": api_key, "query": query},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        # network error, quota exceeded, etc. — degrade gracefully
        return {"found": False, "label": None, "source": None}
 
    claims = data.get("claims", [])
    if not claims:
        return {"found": False, "label": None, "source": None}
 
    # take the first (most relevant) claim's first review
    first_claim  = claims[0]
    reviews      = first_claim.get("claimReview", [])
    if not reviews:
        return {"found": False, "label": None, "source": None}
 
    review  = reviews[0]
    label   = review.get("textualRating")           # e.g. "False", "Mostly True"
    source  = review.get("publisher", {}).get("name")
 
    return {"found": True, "label": label, "source": source}