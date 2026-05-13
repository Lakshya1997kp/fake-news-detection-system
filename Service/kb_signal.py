import re
import json
import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_KB_PATH  = os.path.join(_BASE_DIR, "facts_kb.json")

_kb = None


def _load_kb() -> dict:
    global _kb
    if _kb is None:
        with open(_KB_PATH, "r", encoding="utf-8") as f:
            _kb = json.load(f)
    return _kb


def _normalise(text: str) -> str:
    return text.lower().strip()


def _extract_claim(text: str) -> tuple[str | None, str | None]:
    """
    Tries to extract (subject, claimed_value) from the text.
    Examples:
        "PM of India is Rahul Gandhi"       → ("prime minister of india", "rahul gandhi")
        "India has 50 states"               → ("states in india", "50")
        "The capital of France is Berlin"   → ("capital of france", "berlin")
        "Narendra Modi is the PM of India"  → ("prime minister of india", "narendra modi")
        "CEO of Google is Sundar Pichai"    → ("ceo of google", "sundar pichai")
    """
    text_lower = _normalise(text)

    # pattern 1: "capital/pm/president of X is Y"
    m = re.search(
        r'((?:prime minister|president|ceo|capital|founder|currency|national \w+|chief minister|governor|chancellor|secretary general)\s+of\s+[\w\s]+?)\s+is\s+([\w\s]+)',
        text_lower
    )
    if m:
        return m.group(1).strip(), m.group(2).strip().split(".")[0].strip()

    # pattern 2: "X is the pm/president/capital of Y"
    m = re.search(
        r'([\w\s]+?)\s+is\s+the\s+(prime minister|president|ceo|capital|founder|chancellor|governor)\s+of\s+([\w\s]+)',
        text_lower
    )
    if m:
        subject = f"{m.group(2).strip()} of {m.group(3).strip().split('.')[0].strip()}"
        return subject, m.group(1).strip()

    # pattern 3: "X has N states/planets/countries etc."
    m = re.search(
        r'([\w\s]+?)\s+has\s+(\d+)\s+([\w\s]+)',
        text_lower
    )
    if m:
        subject = f"{m.group(3).strip()} in {m.group(1).strip()}"
        return subject, m.group(2).strip()

    # pattern 4: "pm/president of X is Y" (short form)
    m = re.search(
        r'\b(pm|ceo)\s+of\s+([\w\s]+?)\s+is\s+([\w\s]+)',
        text_lower
    )
    if m:
        role_map = {"pm": "prime minister"}
        role     = role_map.get(m.group(1), m.group(1))
        subject  = f"{role} of {m.group(2).strip()}"
        return subject, m.group(3).strip().split(".")[0].strip()

    return None, None


def kb_signal(text: str) -> dict:
    """
    Checks the input text against the local facts knowledge base.

    Returns:
        {
            "found":        bool,
            "subject":      str | None,
            "claimed":      str | None,
            "actual":       str | None,
            "match":        bool | None,   True = claim matches KB
            "fake_prob":    float,
        }
    """
    kb = _load_kb()

    subject, claimed = _extract_claim(text)
    print(f"[KB] subject: {subject!r}, claimed: {claimed!r}")

    if not subject or not claimed:
        return _not_found()

    # try exact subject match first
    actual = kb.get(subject)

    # if not found, try partial subject match
    if actual is None:
        for key in kb:
            if key in subject or subject in key:
                actual = kb[key]
                subject = key
                break

    if actual is None:
        print(f"[KB] subject not in knowledge base")
        return _not_found()

    print(f"[KB] actual: {actual!r}, claimed: {claimed!r}")

    actual_lower  = _normalise(actual)
    claimed_lower = _normalise(claimed)

    # exact match
    if claimed_lower == actual_lower or claimed_lower in actual_lower or actual_lower in claimed_lower:
        return {
            "found":     True,
            "subject":   subject,
            "claimed":   claimed,
            "actual":    actual,
            "match":     True,
            "fake_prob": 0.05,   # claim matches KB → very likely real
        }

    # partial word match
    actual_words  = set(actual_lower.split())
    claimed_words = set(claimed_lower.split())
    common        = actual_words & claimed_words

    if common and len(common) / max(len(actual_words), len(claimed_words)) > 0.5:
        return {
            "found":     True,
            "subject":   subject,
            "claimed":   claimed,
            "actual":    actual,
            "match":     True,
            "fake_prob": 0.15,   # partial match → likely real
        }

    # no match → claim contradicts KB
    return {
        "found":     True,
        "subject":   subject,
        "claimed":   claimed,
        "actual":    actual,
        "match":     False,
        "fake_prob": 0.95,   # claim contradicts KB → very likely fake
    }


def _not_found() -> dict:
    return {
        "found":     False,
        "subject":   None,
        "claimed":   None,
        "actual":    None,
        "match":     None,
        "fake_prob": 0.5,    # not in KB → neutral
    }