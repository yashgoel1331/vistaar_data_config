from __future__ import annotations

import copy
import logging
import os
from collections.abc import Mapping
from threading import Lock
from types import MappingProxyType
from typing import Any, Callable

from Utils.db import fetch_latest_row

logger = logging.getLogger(__name__)

_CONFIG_CACHE: dict[str, Any] = {}
# Latest version_number loaded per config_type (from Postgres), after each load_configs_to_memory.
_VERSION_META: dict[str, int] = {}
# Values are MappingProxyType (read-only mapping); safe to expose from get_index().
_INDEXES: dict[str, MappingProxyType] = {}
_LOCK = Lock()

_EMPTY_INDEX: MappingProxyType = MappingProxyType({})

EXPECTED_CONFIG_TYPES = {
    "glossary_terms",
    "ambiguous_terms",
    "en-gujarati_aliases",
    "english_aliases",
    "forbidden",
    "preferred",
    "schemes",
}


def _norm(s: str) -> str:
    return s.lower().strip()


def _readonly_record(d: dict[str, Any]) -> MappingProxyType:
    """Single record: keys fixed; use tuples for list fields so sequences are not appendable."""
    return MappingProxyType(d)


def _freeze_outer_index(raw: dict[str, Any]) -> MappingProxyType:
    """Read-only top-level mapping (no insert/delete/replace of keys)."""
    return MappingProxyType(dict(raw))


# ─── List-shaped snapshots: register (config_type, index_name, builder) ─────────
# Add a row here when a new config is stored as JSON array and needs an index.


def _index_ambiguous_terms_list(snapshot: list) -> dict[str, Any]:
    idx: dict[str, Any] = {}
    for entry in snapshot:
        if not isinstance(entry, dict):
            continue
        for term in entry.get("gu_terms", []):
            idx[_norm(term)] = entry
    return idx


# Builder receives list from DB; returns a plain dict[str, Any] (frozen later).
# First key in the tuple wins if multiple exist (e.g. legacy vs new config_type names).
LIST_SNAPSHOT_INDEXERS: list[
    tuple[str | tuple[str, ...], str, Callable[[list], dict[str, Any]]]
] = [
    (
        ("ambiguous_terms", "gujarati_ambiguous_terms_preferred", "ambiguity_terms"),
        "ambiguous_terms",
        _index_ambiguous_terms_list,
    ),
]


def _first_list_snapshot(*config_keys: str) -> list | None:
    """Return the first non-missing list snapshot for any of the given config_type keys."""
    for k in config_keys:
        snap = _CONFIG_CACHE.get(k)
        if isinstance(snap, list):
            return snap
    return None


def _build_list_indexes() -> dict[str, MappingProxyType]:
    """Index any registered list-shaped config types."""
    out: dict[str, MappingProxyType] = {}
    for config_key, index_name, builder in LIST_SNAPSHOT_INDEXERS:
        keys = config_key if isinstance(config_key, tuple) else (config_key,)
        snap = _first_list_snapshot(*keys)
        if snap is None:
            continue
        raw = builder(snap)
        out[index_name] = _freeze_outer_index(raw)
    return out


def _build_indexes() -> None:
    """Build O(1) reverse-lookup indexes from the raw cache."""

    # ── glossary_terms ──
    glossary = _CONFIG_CACHE.get("glossary_terms", {})
    glossary_gu: dict[str, Any] = {}
    glossary_translit: dict[str, Any] = {}

    if isinstance(glossary, dict):
        for en_key, entry in glossary.items():
            if isinstance(entry, dict):
                record = _readonly_record(
                    {
                        "en": en_key,
                        "gu": tuple(entry.get("gu", [])),
                        "transliteration": tuple(entry.get("transliteration", [])),
                    }
                )
                for gu in entry.get("gu", []):
                    glossary_gu[_norm(gu)] = record
                for tr in entry.get("transliteration", []):
                    glossary_translit[_norm(tr)] = record
            elif isinstance(entry, str):
                record = _readonly_record(
                    {"en": en_key, "gu": (entry,), "transliteration": ()}
                )
                glossary_gu[_norm(entry)] = record
            elif isinstance(entry, list):
                record = _readonly_record(
                    {
                        "en": en_key,
                        "gu": tuple(entry),
                        "transliteration": (),
                    }
                )
                for gu in entry:
                    glossary_gu[_norm(gu)] = record

    # ── en-gujarati_aliases ──
    en_gu = _CONFIG_CACHE.get("en-gujarati_aliases", {})
    en_gu_reverse: dict[str, Any] = {}
    if isinstance(en_gu, dict):
        for en_key, gu_list in en_gu.items():
            aliases = tuple(gu_list) if isinstance(gu_list, list) else gu_list
            record = _readonly_record({"canonical_en": en_key, "gu_aliases": aliases})
            if isinstance(gu_list, list):
                for gu in gu_list:
                    en_gu_reverse[_norm(gu)] = record

    # ── english_aliases ──
    en_aliases = _CONFIG_CACHE.get("english_aliases", {})
    en_aliases_reverse: dict[str, Any] = {}
    if isinstance(en_aliases, dict):
        for canonical, aliases in en_aliases.items():
            al = tuple(aliases) if isinstance(aliases, list) else aliases
            record = _readonly_record({"canonical": canonical, "aliases": al})
            if isinstance(aliases, list):
                for alias in aliases:
                    en_aliases_reverse[_norm(alias)] = record

    # ── forbidden (may be wrapped in a "forbidden" key) ──
    forbidden_raw = _CONFIG_CACHE.get("forbidden", {})
    if isinstance(forbidden_raw, dict) and "forbidden" in forbidden_raw:
        forbidden_data = forbidden_raw["forbidden"]
    else:
        forbidden_data = forbidden_raw
    forbidden_idx: dict[str, Any] = {}
    if isinstance(forbidden_data, dict):
        for term, replacement in forbidden_data.items():
            forbidden_idx[_norm(term)] = _readonly_record(
                {
                    "forbidden_term": term,
                    "replacement": replacement,
                }
            )

    # ── preferred (en→gu forward already in cache; build gu→en reverse) ──
    preferred = _CONFIG_CACHE.get("preferred", {})
    preferred_reverse: dict[str, Any] = {}
    if isinstance(preferred, dict):
        for en_key, gu_val in preferred.items():
            if isinstance(gu_val, str):
                preferred_reverse[_norm(gu_val)] = _readonly_record(
                    {"en": en_key, "gu": gu_val}
                )

    # ── schemes (abbreviation→full forward; full→abbreviation reverse) ──
    schemes = _CONFIG_CACHE.get("schemes", {})
    schemes_reverse: dict[str, Any] = {}
    if isinstance(schemes, dict):
        for abbr, full_name in schemes.items():
            if isinstance(full_name, str):
                schemes_reverse[_norm(full_name)] = _readonly_record(
                    {
                        "abbreviation": abbr,
                        "full_name": full_name,
                    }
                )

    _INDEXES.clear()
    _INDEXES["glossary_gu"] = _freeze_outer_index(glossary_gu)
    _INDEXES["glossary_translit"] = _freeze_outer_index(glossary_translit)
    _INDEXES.update(_build_list_indexes())
    _INDEXES["en_gu_reverse"] = _freeze_outer_index(en_gu_reverse)
    _INDEXES["en_aliases_reverse"] = _freeze_outer_index(en_aliases_reverse)
    _INDEXES["forbidden"] = _freeze_outer_index(forbidden_idx)
    _INDEXES["preferred_reverse"] = _freeze_outer_index(preferred_reverse)
    _INDEXES["schemes_reverse"] = _freeze_outer_index(schemes_reverse)


# ─── Load from Postgres ──────────────────────────────────────────────


def _fetch_latest_row_for_type(config_type: str) -> tuple[Any, int] | None:
    """Return (snapshot, version_number) for the highest version_number row for this config_type."""
    row = fetch_latest_row(config_type, columns=("snapshot", "version_number"))
    if row is None:
        return None
    snapshot = row["snapshot"]
    version_number = int(row["version_number"])
    if isinstance(snapshot, dict):
        snapshot = {k.lower().strip(): v for k, v in snapshot.items()}
    return snapshot, version_number


def load_configs_to_memory() -> dict[str, Any]:
    """
    Rebuild in-memory cache from Postgres: for each expected config_type, load the row
    with the largest version_number. Other config_types in the table are ignored.
    """
    latest_by_type: dict[str, Any] = {}
    version_meta: dict[str, int] = {}

    for ct in EXPECTED_CONFIG_TYPES:
        got = _fetch_latest_row_for_type(ct)
        if got is None:
            continue
        snapshot, vn = got
        latest_by_type[ct] = snapshot
        version_meta[ct] = vn

    missing = EXPECTED_CONFIG_TYPES - latest_by_type.keys()
    if missing:
        logger.warning("config_loader: no rows in config_versions for config types: %s", missing)

    with _LOCK:
        _CONFIG_CACHE.clear()
        _CONFIG_CACHE.update(latest_by_type)
        _VERSION_META.clear()
        _VERSION_META.update(version_meta)
        _build_indexes()

    logger.info(
        "config_loader: loaded %d config types (latest version per type). versions=%s",
        len(_CONFIG_CACHE),
        version_meta,
    )
    return dict(_CONFIG_CACHE)


# ─── Raw accessors ───────────────────────────────────────────────────


def get_config(config_type: str, default: Any = None) -> Any:
    return _CONFIG_CACHE.get(config_type, default)


def get_all_configs() -> dict[str, Any]:
    return dict(_CONFIG_CACHE)


def get_config_versions() -> dict[str, int]:
    """Latest version_number loaded per config_type (mirrors last successful load)."""
    return dict(_VERSION_META)


def get_configs_and_versions() -> dict[str, Any]:
    """Full snapshot map plus version_number per config_type."""
    return {"configs": dict(_CONFIG_CACHE), "versions": dict(_VERSION_META)}


def get_index(index_name: str) -> Mapping[str, Any]:
    """
    Read-only view of a reverse index. Top-level mapping cannot be mutated.
    Values are MappingProxyType records where applicable; list-like fields use tuples.
    """
    return _INDEXES.get(index_name, _EMPTY_INDEX)


def get_index_copy(index_name: str) -> dict[str, Any]:
    """
    Deep copy of an index for code that must mutate the result (e.g. tests).
    Prefer get_index() for normal reads.
    """
    idx = _INDEXES.get(index_name)
    if idx is None or len(idx) == 0:
        return {}
    return copy.deepcopy(dict(idx))


# ─── Quick smoke-test ────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    from Utils.db import init_db

    logging.basicConfig(level=logging.INFO)
    init_db()
    cache = load_configs_to_memory()
    print(f"\nLoaded {len(cache)} config types\n")
    for ct, snap in cache.items():
        preview = json.dumps(snap, ensure_ascii=False, indent=2)[:300]
        print(f"-- {ct} --\n{preview}\n")
