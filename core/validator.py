import math
import re


_COMPACT_CODE_PATTERN = re.compile(r"^[A-Z0-9]{12}$")
_GROUPED_CODE_PATTERN = re.compile(
    r"^([A-Z0-9]{4})\s*-\s*([A-Z0-9]{4})\s*-\s*([A-Z0-9]{4})$"
)


def validate_candidate(text, confidence, minimum_confidence):
    if (
        not isinstance(text, str)
        or not isinstance(confidence, (int, float))
        or not math.isfinite(confidence)
        or confidence < minimum_confidence
    ):
        return None
    candidate = text.strip().upper()
    if _COMPACT_CODE_PATTERN.fullmatch(candidate):
        return candidate
    grouped_match = _GROUPED_CODE_PATTERN.fullmatch(candidate)
    if grouped_match:
        return "".join(grouped_match.groups())
    return None
