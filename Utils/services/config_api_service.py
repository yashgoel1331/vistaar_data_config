"""Business/service layer for Flask config APIs."""

from __future__ import annotations

import os
from typing import Any

from flask import jsonify

from Utils.aliases_patch import (
    apply_en_gu_patch,
    apply_en_gu_replace,
    apply_english_aliases_patch,
    apply_english_aliases_replace,
    merged_alias_count,
)
from Utils.ambiguity_patch import ambiguous_terms_list_len, apply_ambiguous_terms_patch
from Utils.config_loader import (
    get_all_configs,
    get_config,
    get_config_versions,
    get_configs_and_versions,
    load_configs_to_memory,
)
from Utils.config_publish import get_latest_version_number, parse_publish_body, publish_config_version
from Utils.config_search import (
    parse_limit,
    search_ambiguous_terms,
    search_en_gu,
    search_english_aliases,
    search_forbidden,
    search_glossary,
    search_preferred,
    search_schemes,
)
from Utils.constants import CONFIG_TYPE_MAP, ROLLBACK_ALLOWED_INPUT_TYPES


class ConfigAPIService:
    """Service methods for all config endpoints and payload handling."""

    def __init__(self, supabase_client):
        """Initialize service with the shared Supabase client."""
        self.supabase = supabase_client

    def _json_response(self, payload: dict | list):
        """Endpoint helper; normalizes list/dict payloads to Flask responses."""
        if isinstance(payload, list):
            return jsonify(payload), 200
        status = payload.pop("_http_status", 200)
        return jsonify(payload), status

    def _patch_triggered_by(self, req=None) -> str:
        """Endpoint helper; resolves triggered_by from header/env for writes."""
        return (
            (req.headers.get("X-Triggered-By") if req is not None else None)
            or os.getenv("USER")
            or os.getenv("USERNAME")
            or "patch"
        )

    def _resolve_config_type(self, raw: object) -> str | None:
        """Endpoint helper; maps user-facing config_type to DB config_type."""
        if not isinstance(raw, str):
            return None
        return CONFIG_TYPE_MAP.get(raw.strip().lower())

    def _find_existing_key(self, target: dict, input_key: str) -> str | None:
        """Endpoint helper; finds existing key with case-insensitive matching."""
        nk = str(input_key).lower().strip()
        for k in target.keys():
            if str(k).lower().strip() == nk:
                return str(k)
        return None

    def _parse_edit_entry(self, data: dict) -> tuple[str, object, str | None]:
        """Endpoint helper; parses edit entry payload and note from request JSON."""
        entry = data.get("entry")
        if entry is None:
            entry = data
        if not isinstance(entry, dict):
            raise ValueError('"entry" must be a JSON object')

        input_key = entry.get("key", entry.get("input_key", entry.get("term")))
        if not isinstance(input_key, str) or not input_key.strip():
            raise ValueError('Provide a non-empty "key" in body.entry')

        if "value" in entry:
            new_value = entry["value"]
        elif "new_value" in entry:
            new_value = entry["new_value"]
        elif "output" in entry:
            new_value = entry["output"]
        elif "replacement" in entry:
            new_value = entry["replacement"]
        else:
            raise ValueError('Provide "value" (or "new_value") in body.entry')

        return input_key, new_value, data.get("note")

    def _parse_delete_entry(self, data: dict) -> tuple[str, str | None]:
        """Endpoint helper; parses delete key entry and optional note."""
        entry = data.get("entry")
        if entry is None:
            entry = data
        if not isinstance(entry, dict):
            raise ValueError('"entry" must be a JSON object')

        input_key = entry.get("key", entry.get("input_key", entry.get("term")))
        if not isinstance(input_key, str) or not input_key.strip():
            raise ValueError('Provide a non-empty "key" in body.entry')
        return input_key, data.get("note")

    def _patch_or_delete_common_errors(self, config_type: str, msg: str):
        """Endpoint helper; standard 400 response with current version metadata."""
        return jsonify(
            {
                "error": msg,
                "version_number": get_latest_version_number(self.supabase, config_type),
                "version_unchanged": True,
            }
        ), 400

    def _fetch_snapshot_by_version(self, config_type: str, version: int):
        """Endpoint helper; fetches exact config snapshot by config_type+version."""
        resp = (
            self.supabase.table("config_versions")
            .select("snapshot, version_number")
            .eq("config_type", config_type)
            .eq("version_number", version)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            return None
        row = rows[0] if isinstance(rows[0], dict) else None
        if row is None:
            return None
        return row.get("snapshot")

    def post_config_version(self, config_type: str, req):
        """Endpoint: POST config route; input snapshot body; publishes new version."""
        data = req.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Expected JSON body"}), 400
        try:
            snapshot, note, triggered_by_body = parse_publish_body(data)
        except (TypeError, ValueError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, config_type),
                    "version_unchanged": True,
                }
            ), 400

        triggered_by = (
            triggered_by_body
            or req.headers.get("X-Triggered-By")
            or os.getenv("USER")
            or os.getenv("USERNAME")
            or "api"
        )

        try:
            result = publish_config_version(
                self.supabase,
                config_type,
                snapshot,
                triggered_by=triggered_by,
                note=note,
            )
        except (ValueError, TypeError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, config_type),
                    "version_unchanged": True,
                }
            ), 400
        except Exception as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, config_type),
                    "version_unchanged": True,
                }
            ), 500

        if result.get("skipped"):
            return jsonify(
                {
                    "ok": True,
                    **result,
                    "versions": get_config_versions(),
                    "version_unchanged": True,
                }
            ), 200

        load_configs_to_memory(self.supabase)
        return jsonify({"ok": True, **result, "versions": get_config_versions()}), 201

    def patch_ambiguous_terms(self, req):
        """Endpoint: PATCH /ambiguity; input {entry}; appends one validated ambiguous_terms item."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        if "entry" not in data:
            return jsonify({"error": '"entry" is required'}), 400
        try:
            result = apply_ambiguous_terms_patch(
                self.supabase,
                data.get("entry"),
                triggered_by=self._patch_triggered_by(req),
                note=data.get("note"),
                get_config=get_config,
            )
        except (TypeError, ValueError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, "ambiguous_terms"),
                    "version_unchanged": True,
                }
            ), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        if result.get("skipped"):
            load_configs_to_memory(self.supabase)
            return jsonify(
                {
                    "ok": True,
                    "message": "no database change",
                    "new_count": ambiguity_list_len(get_config),
                    "version": result.get("version_number"),
                    "versions": get_config_versions(),
                }
            ), 200

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "message": "ambiguous_terms entry added",
                "new_count": ambiguity_list_len(get_config),
                "version": result["version_number"],
                "versions": get_config_versions(),
            }
        ), 201

    def patch_aliases_en_gu(self, req):
        """Endpoint: PATCH /aliases/en-gu; input {entry}; appends aliases for canonical."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        try:
            result = apply_en_gu_patch(
                self.supabase,
                data.get("entry"),
                triggered_by=self._patch_triggered_by(req),
                note=data.get("note"),
                get_config=get_config,
            )
        except (TypeError, ValueError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, "en-gujarati_aliases"),
                    "version_unchanged": True,
                }
            ), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        if result.get("skipped"):
            load_configs_to_memory(self.supabase)
            return jsonify(
                {
                    "ok": True,
                    "message": "no database change",
                    "new_count": merged_alias_count(get_config, "en-gujarati_aliases"),
                    "version": result.get("version_number"),
                    "versions": get_config_versions(),
                }
            ), 200

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "message": "en-gu aliases updated",
                "new_count": merged_alias_count(get_config, "en-gujarati_aliases"),
                "version": result["version_number"],
                "versions": get_config_versions(),
            }
        ), 201

    def put_aliases_en_gu_replace(self, req):
        """Endpoint: PUT /aliases/en-gu; input {entry}; replaces list for canonical_en."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        try:
            result, edited_key, new_list = apply_en_gu_replace(
                self.supabase,
                data.get("entry"),
                triggered_by=self._patch_triggered_by(req),
                note=data.get("note"),
                get_config=get_config,
            )
        except (TypeError, ValueError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, "en-gujarati_aliases"),
                    "version_unchanged": True,
                }
            ), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        if result.get("skipped"):
            load_configs_to_memory(self.supabase)
            return jsonify(
                {
                    "ok": True,
                    "message": "no database change",
                    "entry": {edited_key: new_list},
                    "version_number": result.get("version_number"),
                    "version_unchanged": True,
                    "versions": get_config_versions(),
                }
            ), 200

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "entry": {edited_key: new_list},
                "version_number": result["version_number"],
                "versions": get_config_versions(),
            }
        ), 200

    def patch_aliases_english(self, req):
        """Endpoint: PATCH /aliases/english; input {entry}; appends aliases for canonical."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        try:
            result = apply_english_aliases_patch(
                self.supabase,
                data.get("entry"),
                triggered_by=self._patch_triggered_by(req),
                note=data.get("note"),
                get_config=get_config,
            )
        except (TypeError, ValueError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, "english_aliases"),
                    "version_unchanged": True,
                }
            ), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        if result.get("skipped"):
            load_configs_to_memory(self.supabase)
            return jsonify(
                {
                    "ok": True,
                    "message": "no database change",
                    "new_count": merged_alias_count(get_config, "english_aliases"),
                    "version": result.get("version_number"),
                    "versions": get_config_versions(),
                }
            ), 200

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "message": "english aliases updated",
                "new_count": merged_alias_count(get_config, "english_aliases"),
                "version": result["version_number"],
                "versions": get_config_versions(),
            }
        ), 201

    def put_aliases_english_replace(self, req):
        """Endpoint: PUT /aliases/english; input {entry}; replaces list for canonical."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        try:
            result, edited_key, new_list = apply_english_aliases_replace(
                self.supabase,
                data.get("entry"),
                triggered_by=self._patch_triggered_by(req),
                note=data.get("note"),
                get_config=get_config,
            )
        except (TypeError, ValueError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, "english_aliases"),
                    "version_unchanged": True,
                }
            ), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        if result.get("skipped"):
            load_configs_to_memory(self.supabase)
            return jsonify(
                {
                    "ok": True,
                    "message": "no database change",
                    "entry": {edited_key: new_list},
                    "version_number": result.get("version_number"),
                    "version_unchanged": True,
                    "versions": get_config_versions(),
                }
            ), 200

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "entry": {edited_key: new_list},
                "version_number": result["version_number"],
                "versions": get_config_versions(),
            }
        ), 200

    def delete_alias_key(self, config_type: str, req):
        """Endpoint: DELETE alias routes; input {entry.key}; deletes canonical key."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        try:
            input_key, note = self._parse_delete_entry(data)
        except (TypeError, ValueError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, config_type),
                    "version_unchanged": True,
                }
            ), 400

        snap = get_config(config_type)
        if not isinstance(snap, dict) or len(snap) == 0:
            return jsonify(
                {
                    "error": "key not present",
                    "version_number": get_latest_version_number(self.supabase, config_type),
                    "version_unchanged": True,
                    "versions": get_config_versions(),
                }
            ), 400

        full_snapshot = dict(snap)
        matched = self._find_existing_key(full_snapshot, input_key)
        if matched is None:
            return jsonify(
                {
                    "error": "key not present",
                    "version_number": get_latest_version_number(self.supabase, config_type),
                    "version_unchanged": True,
                    "versions": get_config_versions(),
                }
            ), 400

        del full_snapshot[matched]
        if len(full_snapshot) == 0:
            return jsonify(
                {
                    "error": "Cannot delete the last remaining key for this config type",
                    "version_number": get_latest_version_number(self.supabase, config_type),
                    "version_unchanged": True,
                    "versions": get_config_versions(),
                }
            ), 400

        try:
            result = publish_config_version(
                self.supabase,
                config_type,
                full_snapshot,
                triggered_by=self._patch_triggered_by(req),
                note=note,
                merge=False,
            )
        except (TypeError, ValueError) as e:
            return jsonify(
                {
                    "error": str(e),
                    "version_number": get_latest_version_number(self.supabase, config_type),
                    "version_unchanged": True,
                }
            ), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "message": f"{matched} deleted",
                "version_number": result["version_number"],
                "versions": get_config_versions(),
            }
        ), 200

    def patch_edit_map_config(self, config_type: str, req):
        """Endpoint: PATCH map configs; input {entry.key, entry.value}; edits existing key."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        try:
            input_key, new_value, note = self._parse_edit_entry(data)
        except (TypeError, ValueError) as e:
            return self._patch_or_delete_common_errors(config_type, str(e))

        snap = get_config(config_type)
        if not isinstance(snap, dict) or len(snap) == 0:
            return self._patch_or_delete_common_errors(
                config_type, f"No in-memory snapshot found for {config_type}"
            )

        full_snapshot = dict(snap)
        if config_type == "forbidden" and isinstance(full_snapshot.get("forbidden"), dict):
            inner = dict(full_snapshot["forbidden"])
            matched = self._find_existing_key(inner, input_key)
            if matched is None:
                return self._patch_or_delete_common_errors(config_type, f'key not found: "{input_key}"')
            if inner.get(matched) == new_value:
                return jsonify(
                    {
                        "ok": True,
                        "message": "no database change",
                        "key": matched,
                        "version_number": get_latest_version_number(self.supabase, config_type),
                        "version_unchanged": True,
                        "versions": get_config_versions(),
                    }
                ), 200
            inner[matched] = new_value
            full_snapshot["forbidden"] = inner
            edited_key = matched
        else:
            matched = self._find_existing_key(full_snapshot, input_key)
            if matched is None:
                return self._patch_or_delete_common_errors(config_type, f'key not found: "{input_key}"')
            if full_snapshot.get(matched) == new_value:
                return jsonify(
                    {
                        "ok": True,
                        "message": "no database change",
                        "key": matched,
                        "version_number": get_latest_version_number(self.supabase, config_type),
                        "version_unchanged": True,
                        "versions": get_config_versions(),
                    }
                ), 200
            full_snapshot[matched] = new_value
            edited_key = matched

        try:
            result = publish_config_version(
                self.supabase,
                config_type,
                full_snapshot,
                triggered_by=self._patch_triggered_by(req),
                note=note,
                merge=False,
            )
        except (TypeError, ValueError) as e:
            return self._patch_or_delete_common_errors(config_type, str(e))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "message": f"{edited_key} has been edited",
                "version_number": result["version_number"],
                "versions": get_config_versions(),
            }
        ), 200

    def delete_map_config_key(self, config_type: str, req):
        """Endpoint: DELETE map configs; input {entry.key}; deletes existing key."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        try:
            input_key, note = self._parse_delete_entry(data)
        except (TypeError, ValueError) as e:
            return self._patch_or_delete_common_errors(config_type, str(e))

        snap = get_config(config_type)
        if not isinstance(snap, dict) or len(snap) == 0:
            return self._patch_or_delete_common_errors(
                config_type, f"No in-memory snapshot found for {config_type}"
            )

        full_snapshot = dict(snap)
        if config_type == "forbidden" and isinstance(full_snapshot.get("forbidden"), dict):
            inner = dict(full_snapshot["forbidden"])
            matched = self._find_existing_key(inner, input_key)
            if matched is None:
                return self._patch_or_delete_common_errors(config_type, f'key not found: "{input_key}"')
            del inner[matched]
            if len(inner) == 0:
                return self._patch_or_delete_common_errors(
                    config_type, "Cannot delete the last remaining key for this config type"
                )
            full_snapshot["forbidden"] = inner
            deleted_key = matched
        else:
            matched = self._find_existing_key(full_snapshot, input_key)
            if matched is None:
                return self._patch_or_delete_common_errors(config_type, f'key not found: "{input_key}"')
            del full_snapshot[matched]
            if len(full_snapshot) == 0:
                return self._patch_or_delete_common_errors(
                    config_type, "Cannot delete the last remaining key for this config type"
                )
            deleted_key = matched

        try:
            result = publish_config_version(
                self.supabase,
                config_type,
                full_snapshot,
                triggered_by=self._patch_triggered_by(req),
                note=note,
                merge=False,
            )
        except (TypeError, ValueError) as e:
            return self._patch_or_delete_common_errors(config_type, str(e))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "message": f"{deleted_key} has been deleted",
                "version_number": result["version_number"],
                "versions": get_config_versions(),
            }
        ), 200

    def rollback_config_version(self, req):
        """Endpoint: POST /configs/rollback; input config_type+version; inserts rollback as new version."""
        data = req.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400

        requested_type = data.get("config_type")
        config_type = self._resolve_config_type(requested_type)
        if config_type is None:
            return jsonify(
                {"error": f"Invalid config_type. Allowed: {list(ROLLBACK_ALLOWED_INPUT_TYPES)}"}
            ), 400

        raw_version = data.get("version")
        if not isinstance(raw_version, int) or raw_version <= 0:
            return jsonify({"error": '"version" must be a positive integer'}), 400

        try:
            snapshot = self._fetch_snapshot_by_version(config_type, raw_version)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        if snapshot is None:
            return jsonify(
                {
                    "error": f"version {raw_version} not found for {config_type}",
                    "config_type": config_type,
                }
            ), 404

        note = data.get("note")
        if not isinstance(note, str) or not note.strip():
            note = f"rollback to version {raw_version}"

        try:
            result = publish_config_version(
                self.supabase,
                config_type,
                snapshot,
                triggered_by=self._patch_triggered_by(req),
                note=note,
                merge=False,
                force_insert=True,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "ok": True,
                "rolled_back_to": raw_version,
                "new_version": result.get("version_number"),
                "config_type": config_type,
                "versions": get_config_versions(),
            }
        ), 200

    def list_versions_for_config(self, req):
        """Endpoint: GET /configs/versions; input query config_type; returns all versions."""
        requested_type = req.args.get("config_type")
        config_type = self._resolve_config_type(requested_type)
        if config_type is None:
            return jsonify(
                {"error": f"Invalid config_type. Allowed: {list(ROLLBACK_ALLOWED_INPUT_TYPES)}"}
            ), 400

        try:
            resp = (
                self.supabase.table("config_versions")
                .select("version_number, triggered_by, note")
                .eq("config_type", config_type)
                .order("version_number", desc=True)
                .execute()
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        rows = resp.data or []
        out = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            out.append(
                {
                    "version_number": r.get("version_number"),
                    "triggered_by": r.get("triggered_by"),
                    "note": r.get("note"),
                }
            )
        return jsonify({"config_type": config_type, "versions": out}), 200

    def all_configs(self, req):
        """Endpoint: GET /configs; input optional ?format=flat; returns cached config dictionary."""
        if req.args.get("format") == "flat":
            return jsonify(get_all_configs())
        return jsonify(get_configs_and_versions())

    def reload_configs(self):
        """Endpoint: POST /configs/reload; no input body required; reloads all config types."""
        cache = load_configs_to_memory(self.supabase)
        return jsonify(
            {
                "message": f"Reloaded {len(cache)} config types from latest version rows.",
                "versions": get_config_versions(),
            }
        )

    def search_glossary_endpoint(self, req):
        """Endpoint: GET /glossary; input term/limit query; returns glossary search results."""
        term = req.args.get("term", "").strip()
        limit = parse_limit(req.args.get("limit"))
        return self._json_response(search_glossary(term or None, limit))

    def search_ambiguous_terms_endpoint(self, req):
        """Endpoint: GET /ambiguity; input term/limit query; returns ambiguous_terms search results."""
        term = req.args.get("term", "").strip()
        limit = parse_limit(req.args.get("limit"))
        return self._json_response(search_ambiguous_terms(term or None, limit))

    def search_en_gu_endpoint(self, req):
        """Endpoint: GET /aliases/en-gu; input term/limit query; returns alias search results."""
        term = req.args.get("term", "").strip()
        limit = parse_limit(req.args.get("limit"))
        return self._json_response(search_en_gu(term or None, limit))

    def search_english_aliases_endpoint(self, req):
        """Endpoint: GET /aliases/english; input term/limit query; returns alias search results."""
        term = req.args.get("term", "").strip()
        limit = parse_limit(req.args.get("limit"))
        return self._json_response(search_english_aliases(term or None, limit))

    def search_forbidden_endpoint(self, req):
        """Endpoint: GET /forbidden; input term/limit query; returns forbidden search results."""
        term = req.args.get("term", "").strip()
        limit = parse_limit(req.args.get("limit"))
        return self._json_response(search_forbidden(term or None, limit))

    def search_preferred_endpoint(self, req):
        """Endpoint: GET /preferred; input term/limit query; returns preferred search results."""
        term = req.args.get("term", "").strip()
        limit = parse_limit(req.args.get("limit"))
        return self._json_response(search_preferred(term or None, limit))

    def search_schemes_endpoint(self, req):
        """Endpoint: GET /schemes; input term/limit query; returns schemes search results."""
        term = req.args.get("term", "").strip()
        limit = parse_limit(req.args.get("limit"))
        return self._json_response(search_schemes(term or None, limit))
