import re
import requests

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "FakeNewsDetector/1.0 (lakshya.study02@gmail.com)"
}


def _extract_entities(text: str):
    """
    Extracts (subject, claimed_value) pairs from common claim patterns.
    Examples:
        "PM of India is Rahul Gandhi"  → ("Prime Minister of India", "Rahul Gandhi")
        "India has 50 states"          → ("States of India", "50")
    """
    patterns = [
        # "X of Y is Z"
        (r'(?i)((?:prime minister|president|ceo|capital|population|founder|chairman|governor|chief minister)\s+of\s+[\w\s]+?)\s+is\s+([\w\s]+)',
         lambda m: (m.group(1).strip(), m.group(2).strip())),

        # "Y has N X"
        (r'(?i)([\w\s]+?)\s+has\s+(\d+)\s+([\w\s]+)',
         lambda m: (f"{m.group(3).strip()} of {m.group(1).strip()}", m.group(2).strip())),

        # "X is the PM/president of Y"
        (r'(?i)([\w\s]+?)\s+is\s+the\s+(prime minister|president|ceo|capital|governor|chief minister)\s+of\s+([\w\s]+)',
         lambda m: (f"{m.group(2).strip()} of {m.group(3).strip()}", m.group(1).strip())),
    ]

    for pattern, extractor in patterns:
        match = re.search(pattern, text)
        if match:
            return extractor(match)

    # fallback — just use first sentence as search query
    return (text.split(".")[0].strip()[:100], None)


def _fetch_wikipedia_intro(query: str) -> tuple[str | None, str | None]:
    """
    Searches Wikipedia for query and returns (title, intro_text).
    """
    try:
        search_resp = requests.get(
            WIKIPEDIA_API,
            params={
                "action":   "query",
                "list":     "search",
                "srsearch": query,
                "srlimit":  1,
                "format":   "json",
            },
            headers=HEADERS,
            timeout=5,
        )
        search_resp.raise_for_status()
        results = search_resp.json().get("query", {}).get("search", [])
    except Exception:
        return None, None

    if not results:
        return None, None

    page_id = results[0].get("pageid")
    title   = results[0].get("title")

    if not page_id:
        return None, None

    try:
        extract_resp = requests.get(
            WIKIPEDIA_API,
            params={
                "action":      "query",
                "prop":        "extracts",
                "exintro":     True,
                "explaintext": True,
                "pageids":     page_id,
                "format":      "json",
            },
            headers=HEADERS,
            timeout=5,
        )
        extract_resp.raise_for_status()
        pages   = extract_resp.json().get("query", {}).get("pages", {})
        extract = pages.get(str(page_id), {}).get("extract", "").strip()
    except Exception:
        return title, None

    return title, extract


def _title_is_relevant(title: str, subject: str) -> bool:
    """
    Checks if the Wikipedia article title is relevant to the subject we searched for.
    """
    title_lower   = title.lower()
    subject_lower = subject.lower()

    stopwords = {"of", "the", "a", "an", "is", "in", "and", "for"}
    subject_words = [w for w in subject_lower.split() if w not in stopwords and len(w) > 2]

    matched = [w for w in subject_words if w in title_lower]
    return len(matched) / max(len(subject_words), 1) >= 0.5


def _check_claim(claimed_value: str, wiki_extract: str) -> float:
    """
    Checks if the claimed value appears in the Wikipedia extract.
    Returns a fake_prob between 0.0 and 1.0.
    """
    if not claimed_value or not wiki_extract:
        return 0.5

    claimed_lower  = claimed_value.lower().strip()
    extract_lower  = wiki_extract.lower()

    # direct match → very credible
    if claimed_lower in extract_lower:
        return 0.1

    # partial word match (e.g. "Rahul" from "Rahul Gandhi")
    claimed_words  = [w for w in claimed_lower.split() if len(w) > 3]
    matched_words  = [w for w in claimed_words if w in extract_lower]

    if not claimed_words:
        return 0.5

    match_ratio = len(matched_words) / len(claimed_words)

    if match_ratio >= 0.8:
        return 0.15   # strong partial match → likely real
    elif match_ratio >= 0.5:
        return 0.4    # weak match → uncertain
    else:
        return 0.75   # claim words not found in article → likely fake


def wikipedia_signal(text: str) -> dict:
    """
    Returns:
        {
            "found":      bool,
            "matched":    str | None,
            "summary":    str | None,
            "credible":   bool | None,
            "fake_prob":  float,
        }
    """
    subject, claimed_value = _extract_entities(text)
    print(f"[Wikipedia] subject: {subject!r}, claimed: {claimed_value!r}")

    title, extract = _fetch_wikipedia_intro(subject)
    print(f"[Wikipedia] matched article: {title!r}")

    # validate title is actually relevant to subject
    if title and not _title_is_relevant(title, subject):
        print(f"[Wikipedia] title not relevant to subject, discarding")
        return _not_found()

    if not extract:
        return _not_found()

    fake_prob = _check_claim(claimed_value, extract)
    print(f"[Wikipedia] fake_prob: {fake_prob}")

    return {
        "found":     True,
        "matched":   title,
        "summary":   extract[:300],
        "credible":  fake_prob < 0.5,
        "fake_prob": fake_prob,
    }


def _not_found() -> dict:
    return {
        "found":     False,
        "matched":   None,
        "summary":   None,
        "credible":  None,
        "fake_prob": 0.5,
    }