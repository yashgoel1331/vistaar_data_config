"""
Safe append-only PATCH for ambiguity_terms (list of rule objects).
"""
from __future__ import annotations

from typing import Any, Callable

from Utils.config_publish import publish_config_version

_AMBIGUOUS_TERMS_KEYS = ("ambiguous_terms", "gujarati_ambiguous_terms_preferred", "ambiguity_terms")


def _norm_gu_term(s: str) -> str:
    return str(s).lower().strip()


def validate_ambiguous_terms_entry(entry: Any) -> dict[str, Any]:
    """
    Validate and return a normalized ambiguous_terms entry:
    { "gu_terms": [...], "type": "hardcode"|"ask", "rule": str, optional "context": ... }
    """
    if not isinstance(entry, dict):
        raise ValueError("entry must be an object")
    if "gu_terms" not in entry:
        raise ValueError('missing "gu_terms"')
    raw_terms = entry["gu_terms"]
    if not isinstance(raw_terms, list) or len(raw_terms) == 0:
        raise ValueError('"gu_terms" must be a non-empty list')
    gu_terms: list[str] = []
    seen_local: set[str] = set()
    for t in raw_terms:
        if not isinstance(t, str):
            raise ValueError("each gu_term must be a string")
        nt = _norm_gu_term(t)
        if not nt:
            raise ValueError("gu_term must not be empty")
        if nt in seen_local:
            raise ValueError(f"duplicate gu_term in entry: {t!r}")
        seen_local.add(nt)
        gu_terms.append(nt)

    if "type" not in entry:
        raise ValueError('missing "type"')
    t = entry["type"]
    if t not in ("hardcode", "ask"):
        raise ValueError('"type" must be "hardcode" or "ask"')

    if "rule" not in entry:
        raise ValueError('missing "rule"')
    rule = entry["rule"]
    if not isinstance(rule, str) or not rule.strip():
        raise ValueError("rule must be a non-empty string")

    out: dict[str, Any] = {
        "gu_terms": gu_terms,
        "type": t,
        "rule": rule.strip(),
    }
    if "context" in entry and entry["context"] is not None:
        out["context"] = entry["context"]
    return out


def _current_ambiguous_terms_list(get_config: Callable[[str], Any]) -> list:
    for k in _AMBIGUOUS_TERMS_KEYS:
        v = get_config(k)
        if isinstance(v, list):
            return list(v)
    return []


def _all_normalized_gu_terms_from_snapshot(current: list) -> set[str]:
    out: set[str] = set()
    for item in current:
        if not isinstance(item, dict):
            continue
        for t in item.get("gu_terms", []):
            if isinstance(t, str) and t.strip():
                out.add(_norm_gu_term(t))
    return out


def ambiguous_terms_list_len(get_config: Callable[[str], Any]) -> int:
    for k in _AMBIGUOUS_TERMS_KEYS:
        v = get_config(k)
        if isinstance(v, list):
            return len(v)
    return 0


def apply_ambiguous_terms_patch(
    entry: dict[str, Any],
    *,
    triggered_by: str,
    note: str | None,
    get_config: Callable[[str], Any],
) -> dict[str, Any]:
    """
    Append one validated entry. Publishes the full list from memory plus the new row
    (merge=False) so prior rows are kept even if the latest DB snapshot is missing or
    the wrong JSON shape.
    """
    validated = validate_ambiguous_terms_entry(entry)
    current = _current_ambiguous_terms_list(get_config)
    existing = _all_normalized_gu_terms_from_snapshot(current)
    for t in validated["gu_terms"]:
        if t in existing:
            raise ValueError(f"gu_term already exists: {t}")

    new_list = list(current) + [validated]
    return publish_config_version(
        "ambiguous_terms",
        new_list,
        triggered_by=triggered_by,
        note=note,
        merge=False,
    )
