"""
Insert new config_versions rows with monotonically increasing version_number per config_type.
"""
from __future__ import annotations

import json
from typing import Any

from supabase import Client

# POST: reject overlapping keys with DB + duplicate values (glossary, forbidden, preferred, schemes).
STRICT_UNIQUE_KEYS_AND_VALUES = frozenset(
    {
        "glossary_terms",
        "forbidden",
        "preferred",
        "schemes",
    }
)

# Must match DB CHECK constraint on config_versions.config_type and config_loader usage.
def parse_publish_body(data: Any) -> tuple[Any, str | None, str | None]:
    """
    Returns (snapshot, note, triggered_by).
    Body must be a JSON object with required key \"snapshot\".
    """
    if not isinstance(data, dict):
        raise TypeError('Body must be a JSON object with a "snapshot" field')
    if "snapshot" not in data:
        raise ValueError('Missing required field "snapshot"')
    return data["snapshot"], data.get("note"), data.get("triggered_by")


def _validate_snapshot(snapshot: Any) -> None:
    if snapshot is None:
        raise ValueError('"snapshot" must not be null')
    if not isinstance(snapshot, (dict, list)):
        raise TypeError('"snapshot" must be a JSON object or array')
    if isinstance(snapshot, dict) and len(snapshot) == 0:
        raise ValueError('"snapshot" must not be empty')
    if isinstance(snapshot, list) and len(snapshot) == 0:
        raise ValueError('"snapshot" must not be empty')


def _norm_key(k: Any) -> str:
    return str(k).lower().strip()


def _serialize_value(v: Any) -> str:
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def _forbidden_inner_map(d: dict[str, Any]) -> dict[str, Any]:
    """Inner term -> replacement map (handles {\"forbidden\": {...}} or flat dict)."""
    if "forbidden" in d and isinstance(d["forbidden"], dict):
        return d["forbidden"]
    return d


def _strict_maps_for_type(config_type: str, root: dict[str, Any]) -> dict[str, Any]:
    """Return the dict whose keys we treat as unique identifiers for this config type."""
    if config_type == "forbidden":
        return _forbidden_inner_map(root)
    return root


def _validate_no_duplicate_keys_or_values_strict(
    config_type: str,
    previous: Any,
    incoming: dict[str, Any],
) -> None:
    """
    - Incoming must not reuse any key that already exists in previous (normalized key).
    - Incoming must not contain duplicate values (same serialized value for two keys).
    - Incoming values must not match any existing value in previous (different key).
    """
    prev_map = _strict_maps_for_type(config_type, previous) if isinstance(previous, dict) else {}
    inc_map = _strict_maps_for_type(config_type, incoming)

    if not isinstance(inc_map, dict):
        raise TypeError("snapshot must be a JSON object for this config type")

    prev_keys_norm = {_norm_key(k) for k in prev_map}
    prev_vals = {_serialize_value(v) for v in prev_map.values()}

    seen_values: dict[str, str] = {}
    for raw_k, v in inc_map.items():
        nk = _norm_key(raw_k)
        if nk in prev_keys_norm:
            raise ValueError(f'This key already exists: "{raw_k}"')

        ser = _serialize_value(v)
        if ser in seen_values:
            raise ValueError(
                f"Duplicate value: same as key {seen_values[ser]!r} and {raw_k!r}"
            )
        seen_values[ser] = raw_k

        if ser in prev_vals:
            raise ValueError(f"Value already exists in stored config (conflicts with new key {raw_k!r})")


def _canonical_snapshot_json(obj: Any) -> str:
    """Stable string for comparing two snapshots (key order normalized)."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def snapshots_are_equal(a: Any, b: Any) -> bool:
    """True if snapshots are semantically the same for version bump purposes."""
    try:
        return _canonical_snapshot_json(a) == _canonical_snapshot_json(b)
    except (TypeError, ValueError):
        return False


def _merge_snapshots(existing: Any, incoming: Any) -> Any:
    """Deep-merge dicts (incoming keys win); concatenate lists; if types differ, use incoming."""
    if existing is None:
        return incoming
    if isinstance(existing, dict) and isinstance(incoming, dict):
        out = dict(existing)
        for k, v in incoming.items():
            if k in out:
                out[k] = _merge_snapshots(out[k], v)
            else:
                out[k] = v
        return out
    if isinstance(existing, list) and isinstance(incoming, list):
        return list(existing) + list(incoming)
    return incoming


def _fetch_latest_snapshot(supabase: Client, config_type: str) -> Any | None:
    resp = (
        supabase.table("config_versions")
        .select("snapshot")
        .eq("config_type", config_type)
        .order("version_number", desc=True)
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        return None
    return rows[0].get("snapshot")


ALLOWED_CONFIG_TYPES = frozenset(
    {
        "glossary_terms",
        "ambiguous_terms",
        "en-gujarati_aliases",
        "english_aliases",
        "forbidden",
        "preferred",
        "schemes",
    }
)


MAX_VERSIONS_PER_CONFIG_TYPE = 100


def get_latest_version_number(supabase: Client, config_type: str) -> int | None:
    """Highest version_number in DB for this config_type, or None if no row exists."""
    resp = (
        supabase.table("config_versions")
        .select("version_number")
        .eq("config_type", config_type)
        .order("version_number", desc=True)
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        return None
    return int(rows[0]["version_number"])


def _next_version_number(supabase: Client, config_type: str) -> int:
    v = get_latest_version_number(supabase, config_type)
    return 1 if v is None else v + 1


def _enforce_version_retention_limit(
    supabase: Client, config_type: str, *, keep_latest: int = MAX_VERSIONS_PER_CONFIG_TYPE
) -> None:
    """
    Keep only the latest N versions for a config_type.
    Deletes older rows by version_number if the cap is exceeded.
    """
    if keep_latest <= 0:
        raise ValueError("keep_latest must be > 0")

    resp = (
        supabase.table("config_versions")
        .select("version_number")
        .eq("config_type", config_type)
        .order("version_number", desc=True)
        .execute()
    )
    rows = resp.data or []
    if len(rows) <= keep_latest:
        return

    old_versions: list[int] = []
    for row in rows[keep_latest:]:
        if isinstance(row, dict) and row.get("version_number") is not None:
            old_versions.append(int(row["version_number"]))

    if not old_versions:
        return

    (
        supabase.table("config_versions")
        .delete()
        .eq("config_type", config_type)
        .in_("version_number", old_versions)
        .execute()
    )


def publish_config_version(
    supabase: Client,
    config_type: str,
    snapshot: Any,
    *,
    triggered_by: str,
    note: str | None,
    merge: bool = True,
    force_insert: bool = False,
) -> dict[str, Any]:
    """
    Insert a new row: version_number = previous max + 1 for this config_type.

    When merge=True (default): merges incoming snapshot with the latest stored snapshot
    (dict deep-merge, list concat). For glossary_terms, forbidden, preferred, schemes:
    incoming keys must be new; no duplicate values.

    When merge=False: inserts ``snapshot`` as the full body (PATCH paths that already
    merged in memory). Skips strict duplicate-key validation, which only applies to
    partial POST payloads.

    All validation runs before _next_version_number or insert — on error, DB version is unchanged.
    """
    if config_type not in ALLOWED_CONFIG_TYPES:
        raise ValueError(f"Invalid config_type: {config_type!r}")
    _validate_snapshot(snapshot)

    previous = _fetch_latest_snapshot(supabase, config_type)
    if merge and config_type in STRICT_UNIQUE_KEYS_AND_VALUES and isinstance(snapshot, dict):
        _validate_no_duplicate_keys_or_values_strict(config_type, previous, snapshot)

    merged = _merge_snapshots(previous, snapshot) if merge else snapshot

    # If nothing actually changed vs latest row, do not insert (unless caller explicitly forces insert).
    if not force_insert and previous is not None and snapshots_are_equal(merged, previous):
        v = get_latest_version_number(supabase, config_type)
        return {
            "config_type": config_type,
            "version_number": v,
            "row": None,
            "skipped": True,
            "message": "No changes; merged snapshot matches the latest stored version.",
        }

    version_number = _next_version_number(supabase, config_type)
    row = {
        "config_type": config_type,
        "version_number": version_number,
        "snapshot": merged,
        "triggered_by": triggered_by,
        "note": note,
    }
    # Python client: do not chain .select() after .insert(); use .execute() only.
    resp = supabase.table("config_versions").insert(row).execute()
    inserted = None
    if resp.data is not None:
        inserted = resp.data[0] if isinstance(resp.data, list) and len(resp.data) else resp.data
    _enforce_version_retention_limit(supabase, config_type)

    return {
        "config_type": config_type,
        "version_number": version_number,
        "row": inserted,
        "skipped": False,
    }
