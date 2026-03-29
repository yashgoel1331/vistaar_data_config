"""
Lexical ranking over in-memory config snapshots using agents.search.lexical_rank_score.
Exact index hits first; otherwise candidates ranked by substring + token overlap.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from Utils.config_loader import get_config, get_index
from Utils.lexical_rank import lexical_rank_score


def _norm(s: str) -> str:
    return s.lower().strip()


def _ci_map_key(d: dict, term: str) -> Any:
    """Return the actual dict key whose normalized string form matches _norm(term), or None."""
    nk = _norm(term)
    for k in d.keys():
        if _norm(str(k)) == nk:
            return k
    return None


def parse_limit(raw: str | None, default: int = 50, cap: int = 200) -> int:
    try:
        n = int(raw) if raw is not None else default
    except (TypeError, ValueError):
        n = default
    return max(1, min(n, cap))


def glossary_entry_to_api(en_term: str, entry: Any) -> dict[str, Any]:
    if isinstance(entry, (dict, Mapping)):
        gu = entry.get("gu", ())
        tr = entry.get("transliteration", ())
        return {
            "en": en_term,
            "gu": list(gu) if gu is not None else [],
            "transliteration": list(tr) if tr is not None else [],
        }
    if isinstance(entry, str):
        return {"en": en_term, "gu": [entry], "transliteration": []}
    if isinstance(entry, list):
        return {"en": en_term, "gu": entry, "transliteration": []}
    return {"en": en_term, "gu": [], "transliteration": []}


def _glossary_blob(en_key: str, entry: Any) -> str:
    if isinstance(entry, (dict, Mapping)):
        parts = [en_key]
        parts.extend(str(x) for x in entry.get("gu", []) or [])
        parts.extend(str(x) for x in entry.get("transliteration", []) or [])
        return " ".join(parts)
    if isinstance(entry, str):
        return f"{en_key} {entry}"
    if isinstance(entry, list):
        return f"{en_key} {' '.join(str(x) for x in entry)}"
    return en_key


def ambiguous_terms_snapshot() -> list:
    for k in (
        "ambiguous_terms",
        "gujarati_ambiguous_terms_preferred",
        "ambiguity_terms",
    ):
        v = get_config(k)
        if isinstance(v, list):
            return v
    return []


# ─── Glossary ────────────────────────────────────────────────────────


def search_glossary(term: str | None, limit: int) -> dict[str, Any]:
    glossary_data = get_config("glossary_terms", {}) or {}
    if not term:
        items = list(glossary_data.items())[:50]
        return {
            "count": len(glossary_data),
            "returned": len(items),
            "data": [glossary_entry_to_api(k, v) for k, v in items],
        }

    key = _norm(term)
    idx_gu = get_index("glossary_gu")
    idx_tr = get_index("glossary_translit")

    gk = _ci_map_key(glossary_data, term)
    if gk is not None:
        return {
            "query": term,
            "match_type": "exact_en",
            "data": glossary_entry_to_api(str(gk), glossary_data[gk]),
        }

    hit = idx_gu.get(key)
    if hit:
        en = hit.get("en", key) if hasattr(hit, "get") else key
        return {
            "query": term,
            "match_type": "exact_gu",
            "data": glossary_entry_to_api(str(en), hit),
        }

    hit = idx_tr.get(key)
    if hit:
        en = hit.get("en", key) if hasattr(hit, "get") else key
        return {
            "query": term,
            "match_type": "exact_translit",
            "data": glossary_entry_to_api(str(en), hit),
        }

    ranked: list[tuple[float, str, Any]] = []
    for en_key, entry in glossary_data.items():
        blob = _glossary_blob(en_key, entry)
        sc = lexical_rank_score(term, blob)
        if sc > 0:
            ranked.append((sc, en_key, entry))
    ranked.sort(key=lambda x: x[0], reverse=True)
    out = []
    for sc, en_key, entry in ranked[:limit]:
        row = glossary_entry_to_api(en_key, entry)
        row["_lexical_score"] = round(sc, 6)
        out.append(row)

    if not out:
        return {"query": term, "error": "Term not found", "_http_status": 404}

    return {
        "query": term,
        "match_type": "ranked",
        "limit": limit,
        "count": len(out),
        "data": out,
    }


# ─── Ambiguity ─────────────────────────────────────────────────────────


def search_ambiguous_terms(term: str | None, limit: int) -> dict[str, Any]:
    data = ambiguous_terms_snapshot()
    if not term:
        return {"count": len(data), "data": data}

    key = _norm(term)
    hit = get_index("ambiguous_terms").get(key)
    if hit:
        return {"query": term, "match_type": "exact", "data": hit}

    ranked: list[tuple[float, dict]] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        parts = list(entry.get("gu_terms", []))
        if entry.get("rule"):
            parts.append(str(entry["rule"]))
        if entry.get("context"):
            parts.append(str(entry["context"]))
        blob = " ".join(str(p) for p in parts)
        sc = lexical_rank_score(term, blob)
        if sc > 0:
            ranked.append((sc, entry))
    ranked.sort(key=lambda x: x[0], reverse=True)
    out = []
    for sc, entry in ranked[:limit]:
        e = dict(entry)
        e["_lexical_score"] = round(sc, 6)
        out.append(e)

    if not out:
        return {"query": term, "error": "Term not found in ambiguity rules", "_http_status": 404}

    return {
        "query": term,
        "match_type": "ranked",
        "limit": limit,
        "count": len(out),
        "data": out,
    }


# ─── en-gu aliases ─────────────────────────────────────────────────


def search_en_gu(term: str | None, limit: int) -> dict[str, Any]:
    en_gu = get_config("en-gujarati_aliases", {}) or {}
    if not isinstance(en_gu, dict):
        en_gu = {}
    if not term:
        return en_gu

    key = _norm(term)
    ck = _ci_map_key(en_gu, term)
    if ck is not None:
        return {
            "query": term,
            "match_type": "exact_en",
            "data": {"canonical_en": str(ck), "gu_aliases": en_gu[ck]},
        }

    hit = get_index("en_gu_reverse").get(key)
    if hit:
        return {"query": term, "match_type": "exact_gu", "data": dict(hit)}

    ranked: list[tuple[float, dict]] = []
    for en_key, gu_list in en_gu.items():
        parts = [str(en_key)]
        if isinstance(gu_list, list):
            parts.extend(str(x) for x in gu_list)
        blob = " ".join(parts)
        sc = lexical_rank_score(term, blob)
        if sc > 0:
            ranked.append((sc, {"canonical_en": str(en_key), "gu_aliases": gu_list}))
    ranked.sort(key=lambda x: x[0], reverse=True)
    out = []
    for sc, row in ranked[:limit]:
        row = dict(row)
        row["_lexical_score"] = round(sc, 6)
        out.append(row)

    if not out:
        return {"query": term, "error": "Term not found in en-gu aliases", "_http_status": 404}

    return {
        "query": term,
        "match_type": "ranked",
        "limit": limit,
        "count": len(out),
        "data": out,
    }


# ─── English aliases ─────────────────────────────────────────────────


def search_english_aliases(term: str | None, limit: int) -> dict[str, Any]:
    en_aliases = get_config("english_aliases", {}) or {}
    if not isinstance(en_aliases, dict):
        en_aliases = {}
    if not term:
        return en_aliases

    key = _norm(term)
    ck = _ci_map_key(en_aliases, term)
    if ck is not None:
        return {
            "query": term,
            "match_type": "exact_canonical",
            "data": {"canonical": str(ck), "aliases": en_aliases[ck]},
        }

    hit = get_index("en_aliases_reverse").get(key)
    if hit:
        return {"query": term, "match_type": "exact_alias", "data": dict(hit)}

    ranked: list[tuple[float, dict]] = []
    for canonical, aliases in en_aliases.items():
        parts = [str(canonical)]
        if isinstance(aliases, list):
            parts.extend(str(a) for a in aliases)
        blob = " ".join(parts)
        sc = lexical_rank_score(term, blob)
        if sc > 0:
            ranked.append((sc, {"canonical": str(canonical), "aliases": aliases}))
    ranked.sort(key=lambda x: x[0], reverse=True)
    out = []
    for sc, row in ranked[:limit]:
        row = dict(row)
        row["_lexical_score"] = round(sc, 6)
        out.append(row)

    if not out:
        return {"query": term, "error": "Term not found in english aliases", "_http_status": 404}

    return {
        "query": term,
        "match_type": "ranked",
        "limit": limit,
        "count": len(out),
        "data": out,
    }


# ─── Forbidden ───────────────────────────────────────────────────────


def _forbidden_flat() -> dict[str, Any]:
    raw = get_config("forbidden", {}) or {}
    if isinstance(raw, dict) and "forbidden" in raw and isinstance(raw["forbidden"], dict):
        return raw["forbidden"]
    return raw if isinstance(raw, dict) else {}


def search_forbidden(term: str | None, limit: int) -> dict[str, Any]:
    flat = _forbidden_flat()
    if not isinstance(flat, dict):
        flat = {}
    if not term:
        return get_config("forbidden", {}) or {}

    key = _norm(term)
    hit = get_index("forbidden").get(key)
    if hit:
        return {"query": term, "match_type": "exact", "data": dict(hit)}

    ranked: list[tuple[float, dict]] = []
    for fterm, replacement in flat.items():
        blob = f"{fterm} {replacement!s}"
        sc = lexical_rank_score(term, blob)
        if sc > 0:
            ranked.append(
                (
                    sc,
                    {"forbidden_term": fterm, "replacement": replacement},
                )
            )
    ranked.sort(key=lambda x: x[0], reverse=True)
    out = []
    for sc, row in ranked[:limit]:
        row = dict(row)
        row["_lexical_score"] = round(sc, 6)
        out.append(row)

    if not out:
        return {"query": term, "error": "Term not found in forbidden list", "_http_status": 404}

    return {
        "query": term,
        "match_type": "ranked",
        "limit": limit,
        "count": len(out),
        "data": out,
    }


# ─── Preferred ───────────────────────────────────────────────────────


def search_preferred(term: str | None, limit: int) -> dict[str, Any]:
    preferred = get_config("preferred", {}) or {}
    if not isinstance(preferred, dict):
        preferred = {}
    if not term:
        return preferred

    key = _norm(term)
    pk = _ci_map_key(preferred, term)
    if pk is not None:
        return {
            "query": term,
            "match_type": "exact_en",
            "data": {"en": str(pk), "gu": preferred[pk]},
        }

    hit = get_index("preferred_reverse").get(key)
    if hit:
        return {"query": term, "match_type": "exact_gu", "data": dict(hit)}

    ranked: list[tuple[float, dict]] = []
    for en_key, gu_val in preferred.items():
        blob = f"{en_key} {gu_val}"
        sc = lexical_rank_score(term, blob)
        if sc > 0:
            ranked.append((sc, {"en": str(en_key), "gu": gu_val}))
    ranked.sort(key=lambda x: x[0], reverse=True)
    out = []
    for sc, row in ranked[:limit]:
        row = dict(row)
        row["_lexical_score"] = round(sc, 6)
        out.append(row)

    if not out:
        return {"query": term, "error": "Term not found in preferred terms", "_http_status": 404}

    return {
        "query": term,
        "match_type": "ranked",
        "limit": limit,
        "count": len(out),
        "data": out,
    }


# ─── Schemes ─────────────────────────────────────────────────────────


def search_schemes(term: str | None, limit: int) -> dict[str, Any]:
    schemes = get_config("schemes", {}) or {}
    if not isinstance(schemes, dict):
        schemes = {}
    if not term:
        return schemes

    key = _norm(term)
    sk = _ci_map_key(schemes, term)
    if sk is not None:
        return {
            "query": term,
            "match_type": "exact_abbr",
            "data": {"abbreviation": str(sk), "full_name": schemes[sk]},
        }

    hit = get_index("schemes_reverse").get(key)
    if hit:
        return {"query": term, "match_type": "exact_name", "data": dict(hit)}

    ranked: list[tuple[float, dict]] = []
    for abbr, full_name in schemes.items():
        blob = f"{abbr} {full_name}"
        sc = lexical_rank_score(term, blob)
        if sc > 0:
            ranked.append(
                (sc, {"abbreviation": str(abbr), "full_name": full_name}),
            )
    ranked.sort(key=lambda x: x[0], reverse=True)
    out = []
    for sc, row in ranked[:limit]:
        row = dict(row)
        row["_lexical_score"] = round(sc, 6)
        out.append(row)

    if not out:
        return {"query": term, "error": "Term not found in schemes", "_http_status": 404}

    return {
        "query": term,
        "match_type": "ranked",
        "limit": limit,
        "count": len(out),
        "data": out,
    }
