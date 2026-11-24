from difflib import SequenceMatcher


def transcript_accuracy(reference: str, hypothesis: str) -> float:
    if not reference.strip():
        return 0.0
    ratio = SequenceMatcher(
        None,
        reference.lower().strip(),
        hypothesis.lower().strip(),
    ).ratio()
    return round(ratio * 100, 2)


def bounded_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)
