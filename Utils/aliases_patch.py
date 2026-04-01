"""
Safe PATCH append for en-gujarati_aliases and english_aliases (dict of str -> list[str]).
"""
from __future__ import annotations

from typing import Any, Callable

from Utils.config_publish import publish_config_version


def _norm_key(s: str) -> str:
    return str(s).lower().strip()


def validate_en_gu_patch(body: dict[str, Any]) -> tuple[str, list[str]]:
    if "canonical_en" not in body:
        raise ValueError('missing "canonical_en"')
    if "gu_aliases" not in body:
        raise ValueError('missing "gu_aliases"')
    ck = body["canonical_en"]
    if not isinstance(ck, str) or not ck.strip():
        raise ValueError("canonical_en must be a non-empty string")
    aliases = body["gu_aliases"]
    if not isinstance(aliases, list) or len(aliases) == 0:
        raise ValueError("gu_aliases must be a non-empty list")
    out: list[str] = []
    seen: set[str] = set()
    for a in aliases:
        if not isinstance(a, str) or not a.strip():
            raise ValueError("each gu_alias must be a non-empty string")
        n = a.strip()
        if n in seen:
            raise ValueError(f"duplicate alias in request: {a!r}")
        seen.add(n)
        out.append(n)
    return _norm_key(ck), out


def validate_english_aliases_patch(body: dict[str, Any]) -> tuple[str, list[str]]:
    if "canonical" not in body:
        raise ValueError('missing "canonical"')
    if "aliases" not in body:
        raise ValueError('missing "aliases"')
    ck = body["canonical"]
    if not isinstance(ck, str) or not ck.strip():
        raise ValueError('"canonical" must be a non-empty string')
    aliases = body["aliases"]
    if not isinstance(aliases, list) or len(aliases) == 0:
        raise ValueError('"aliases" must be a non-empty list')
    out: list[str] = []
    seen: set[str] = set()
    for a in aliases:
        if not isinstance(a, str) or not a.strip():
            raise ValueError("each alias must be a non-empty string")
        n = _norm_key(a)
        if not n:
            raise ValueError("alias must not be empty")
        if n in seen:
            raise ValueError(f"duplicate alias in request: {a!r}")
        seen.add(n)
        out.append(a.strip())
    return _norm_key(ck), out


def _copy_alias_snapshot(snap: dict[str, Any]) -> dict[str, Any]:
    """Shallow copy with list values copied so we can mutate safely."""
    out: dict[str, Any] = {}
    for k, v in snap.items():
        if isinstance(v, list):
            out[str(k)] = list(v)
        else:
            out[str(k)] = v
    return out


def _find_canonical_key(snap: dict[str, Any], canonical_norm: str) -> str | None:
    for k in snap:
        if _norm_key(str(k)) == canonical_norm:
            return str(k)
    return None


def _existing_alias_set_for_key(
    snap: dict[str, Any], canonical_norm: str, *, value_norm: Callable[[str], str]
) -> set[str]:
    if not isinstance(snap, dict):
        return set()
    for k, v in snap.items():
        if _norm_key(str(k)) != canonical_norm:
            continue
        if not isinstance(v, list):
            return set()
        return {value_norm(str(x)) for x in v if isinstance(x, str) and x.strip()}
    return set()


def apply_en_gu_patch(
    body: dict[str, Any],
    *,
    triggered_by: str,
    note: str | None,
    get_config: Callable[[str], Any],
) -> dict[str, Any]:
    canonical_norm, new_aliases = validate_en_gu_patch(body)
    snap = get_config("en-gujarati_aliases")
    if not isinstance(snap, dict):
        snap = {}
    existing_vals = _existing_alias_set_for_key(snap, canonical_norm, value_norm=lambda s: s.strip())
    for a in new_aliases:
        if a.strip() in existing_vals or a in existing_vals:
            raise ValueError(f"gu_alias already exists for this canonical: {a!r}")
    full = _copy_alias_snapshot(snap)
    match = _find_canonical_key(full, canonical_norm)
    if match is None:
        raise ValueError(f'canonical_en does not exist: "{canonical_norm}"')
    old = full[match] if isinstance(full[match], list) else []
    full[match] = list(old) + list(new_aliases)
    return publish_config_version(
        "en-gujarati_aliases",
        full,
        triggered_by=triggered_by,
        note=note,
        merge=False,
    )


def apply_en_gu_replace(
    body: dict[str, Any],
    *,
    triggered_by: str,
    note: str | None,
    get_config: Callable[[str], Any],
) -> tuple[dict[str, Any], str, list[str]]:
    """
    Replace the entire alias list for an existing canonical_en.
    Returns (publish_result, edited_key, new_list).
    """
    canonical_norm, new_aliases = validate_en_gu_patch(body)
    snap = get_config("en-gujarati_aliases")
    if not isinstance(snap, dict):
        snap = {}
    full = _copy_alias_snapshot(snap)
    match = _find_canonical_key(full, canonical_norm)
    if match is None:
        raise ValueError(f'canonical_en does not exist: "{canonical_norm}"')
    full[match] = list(new_aliases)
    result = publish_config_version(
        "en-gujarati_aliases",
        full,
        triggered_by=triggered_by,
        note=note,
        merge=False,
    )
    return result, match, list(new_aliases)


def apply_english_aliases_patch(
    body: dict[str, Any],
    *,
    triggered_by: str,
    note: str | None,
    get_config: Callable[[str], Any],
) -> dict[str, Any]:
    canonical_norm, new_aliases = validate_english_aliases_patch(body)
    snap = get_config("english_aliases")
    if not isinstance(snap, dict):
        snap = {}
    existing_vals = _existing_alias_set_for_key(
        snap, canonical_norm, value_norm=_norm_key
    )
    for a in new_aliases:
        if _norm_key(a) in existing_vals:
            raise ValueError(f"alias already exists for this canonical: {a!r}")
    full = _copy_alias_snapshot(snap)
    match = _find_canonical_key(full, canonical_norm)
    if match is None:
        raise ValueError(f'canonical does not exist: "{canonical_norm}"')
    old = full[match] if isinstance(full[match], list) else []
    full[match] = list(old) + list(new_aliases)
    return publish_config_version(
        "english_aliases",
        full,
        triggered_by=triggered_by,
        note=note,
        merge=False,
    )


def apply_english_aliases_replace(
    body: dict[str, Any],
    *,
    triggered_by: str,
    note: str | None,
    get_config: Callable[[str], Any],
) -> tuple[dict[str, Any], str, list[str]]:
    """
    Replace the entire alias list for an existing canonical.
    Returns (publish_result, edited_key, new_list).
    """
    canonical_norm, new_aliases = validate_english_aliases_patch(body)
    snap = get_config("english_aliases")
    if not isinstance(snap, dict):
        snap = {}
    full = _copy_alias_snapshot(snap)
    match = _find_canonical_key(full, canonical_norm)
    if match is None:
        raise ValueError(f'canonical does not exist: "{canonical_norm}"')
    full[match] = list(new_aliases)
    result = publish_config_version(
        "english_aliases",
        full,
        triggered_by=triggered_by,
        note=note,
        merge=False,
    )
    return result, match, list(new_aliases)


def merged_dict_len_after_publish(get_config: Callable[[str], Any], config_key: str) -> int:
    s = get_config(config_key)
    if isinstance(s, dict):
        return len(s)
    return 0


def merged_alias_count(get_config: Callable[[str], Any], config_key: str) -> int:
    s = get_config(config_key)
    if not isinstance(s, dict):
        return 0
    n = 0
    for v in s.values():
        if isinstance(v, list):
            n += len(v)
    return n
