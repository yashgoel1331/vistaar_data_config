"""Flask app bootstrap for modular routes/services config backend."""

from __future__ import annotations

import os

from flask import Flask
from flask_cors import CORS
from supabase import create_client

from Utils.config_loader import load_configs_to_memory
from Utils.routes.aliases_routes import init_aliases_routes
from Utils.routes.config_routes import init_config_routes
from Utils.services.config_api_service import ConfigAPIService
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ddpmzibgajndovcnuicm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
load_configs_to_memory(supabase)

service = ConfigAPIService(supabase)
app.register_blueprint(init_config_routes(service))
app.register_blueprint(init_aliases_routes(service))

if __name__ == "__main__":
    app.run(debug=True)
"""Flask app bootstrap for modular routes/services config backend."""


import os

from flask import Flask
from supabase import create_client

from Utils.config_loader import load_configs_to_memory
from Utils.routes.aliases_routes import init_aliases_routes
from Utils.routes.config_routes import init_config_routes
from Utils.services.config_api_service import ConfigAPIService

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ddpmzibgajndovcnuicm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
load_configs_to_memory(supabase)

service = ConfigAPIService(supabase)
app.register_blueprint(init_config_routes(service))
app.register_blueprint(init_aliases_routes(service))

if __name__ == "__main__":
    app.run(debug=True)
"""Flask app bootstrap for modular routes/services config backend."""

import os

from flask import Flask
from supabase import create_client

from Utils.config_loader import load_configs_to_memory
from Utils.routes.aliases_routes import init_aliases_routes
from Utils.routes.config_routes import init_config_routes
from Utils.services.config_api_service import ConfigAPIService

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ddpmzibgajndovcnuicm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
load_configs_to_memory(supabase)

service = ConfigAPIService(supabase)
app.register_blueprint(init_config_routes(service))
app.register_blueprint(init_aliases_routes(service))

if __name__ == "__main__":
    app.run(debug=True)
import os

from flask import Flask, jsonify, request
from supabase import create_client

from Utils.config_loader import (
    load_configs_to_memory,
    get_all_configs,
    get_config,
    get_config_versions,
    get_configs_and_versions,
)
from Utils.config_publish import (
    get_latest_version_number,
    parse_publish_body,
    publish_config_version,
)
from Utils.ambiguity_patch import apply_ambiguous_terms_patch, ambiguous_terms_list_len
from Utils.aliases_patch import (
    apply_en_gu_patch,
    apply_english_aliases_patch,
    apply_en_gu_replace,
    apply_english_aliases_replace,
    merged_alias_count,
)
from Utils.config_search import (
    parse_limit,
    search_glossary,
    search_ambiguous_terms,
    search_en_gu,
    search_english_aliases,
    search_forbidden,
    search_preferred,
    search_schemes,
)

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ddpmzibgajndovcnuicm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
load_configs_to_memory(supabase)

CONFIG_TYPE_MAP = {
    "glossary": "glossary_terms",
    "ambiguous_terms": "ambiguous_terms",
    "en-gujarati_aliases": "en-gujarati_aliases",
    "english_aliases": "english_aliases",
    "forbidden": "forbidden",
    "preferred": "preferred",
    "schemes": "schemes",
}

ROLLBACK_ALLOWED_INPUT_TYPES = (
    "glossary",
    "ambiguous_terms",
    "en-gujarati_aliases",
    "english_aliases",
    "forbidden",
    "preferred",
    "schemes",
)


def _json_response(payload: dict | list):
    if isinstance(payload, list):
        return jsonify(payload), 200
    status = payload.pop("_http_status", 200)
    return jsonify(payload), status


def _post_config_version(config_type: str):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Expected JSON body"}), 400
    try:
        snapshot, note, triggered_by_body = parse_publish_body(data)
    except (TypeError, ValueError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, config_type),
                "version_unchanged": True,
            }
        ), 400

    triggered_by = (
        triggered_by_body
        or request.headers.get("X-Triggered-By")
        or os.getenv("USER")
        or os.getenv("USERNAME")
        or "api"
    )

    try:
        result = publish_config_version(
            supabase,
            config_type,
            snapshot,
            triggered_by=triggered_by,
            note=note,
        )
    except (ValueError, TypeError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, config_type),
                "version_unchanged": True,
            }
        ), 400
    except Exception as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, config_type),
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

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            **result,
            "versions": get_config_versions(),
        }
    ), 201


def _patch_triggered_by():
    return (
        request.headers.get("X-Triggered-By")
        or os.getenv("USER")
        or os.getenv("USERNAME")
        or "patch"
    )


def _resolve_config_type(raw: object) -> str | None:
    if not isinstance(raw, str):
        return None
    return CONFIG_TYPE_MAP.get(raw.strip().lower())


def _fetch_snapshot_by_version(supabase_client, config_type: str, version: int):
    resp = (
        supabase_client.table("config_versions")
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


def _rollback_config_version():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400

    requested_type = data.get("config_type")
    config_type = _resolve_config_type(requested_type)
    if config_type is None:
        return jsonify(
            {
                "error": f"Invalid config_type. Allowed: {list(ROLLBACK_ALLOWED_INPUT_TYPES)}"
            }
        ), 400

    raw_version = data.get("version")
    if not isinstance(raw_version, int) or raw_version <= 0:
        return jsonify({"error": '"version" must be a positive integer'}), 400

    try:
        snapshot = _fetch_snapshot_by_version(supabase, config_type, raw_version)
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
            supabase,
            config_type,
            snapshot,
            triggered_by=_patch_triggered_by(),
            note=note,
            merge=False,
            force_insert=True,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "rolled_back_to": raw_version,
            "new_version": result.get("version_number"),
            "config_type": config_type,
            "versions": get_config_versions(),
        }
    ), 200


def _list_versions_for_config():
    requested_type = request.args.get("config_type")
    config_type = _resolve_config_type(requested_type)
    if config_type is None:
        return jsonify(
            {
                "error": f"Invalid config_type. Allowed: {list(ROLLBACK_ALLOWED_INPUT_TYPES)}"
            }
        ), 400

    try:
        resp = (
            supabase.table("config_versions")
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


def _patch_ambiguous_terms():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400
    if "entry" not in data:
        return jsonify({"error": '"entry" is required'}), 400
    entry = data.get("entry")
    try:
        result = apply_ambiguous_terms_patch(
            supabase,
            entry,
            triggered_by=_patch_triggered_by(),
            note=data.get("note"),
            get_config=get_config,
        )
    except (TypeError, ValueError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, "ambiguous_terms"),
                "version_unchanged": True,
            }
        ), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if result.get("skipped"):
        load_configs_to_memory(supabase)
        return jsonify(
            {
                "ok": True,
                "message": "no database change",
                "new_count": ambiguous_terms_list_len(get_config),
                "version": result.get("version_number"),
                "versions": get_config_versions(),
            }
        ), 200

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "message": "ambiguous_terms entry added",
            "new_count": ambiguous_terms_list_len(get_config),
            "version": result["version_number"],
            "versions": get_config_versions(),
        }
    ), 201


def _patch_aliases_en_gu():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400
    try:
        result = apply_en_gu_patch(
            supabase,
            data.get("entry"),
            triggered_by=_patch_triggered_by(),
            note=data.get("note"),
            get_config=get_config,
        )
    except (TypeError, ValueError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, "en-gujarati_aliases"),
                "version_unchanged": True,
            }
        ), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if result.get("skipped"):
        load_configs_to_memory(supabase)
        return jsonify(
            {
                "ok": True,
                "message": "no database change",
                "new_count": merged_alias_count(get_config, "en-gujarati_aliases"),
                "version": result.get("version_number"),
                "versions": get_config_versions(),
            }
        ), 200

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "message": "en-gu aliases updated",
            "new_count": merged_alias_count(get_config, "en-gujarati_aliases"),
            "version": result["version_number"],
            "versions": get_config_versions(),
        }
    ), 201


def _put_aliases_en_gu_replace():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400
    try:
        result, edited_key, new_list = apply_en_gu_replace(
            supabase,
            data.get("entry"),
            triggered_by=_patch_triggered_by(),
            note=data.get("note"),
            get_config=get_config,
        )
    except (TypeError, ValueError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, "en-gujarati_aliases"),
                "version_unchanged": True,
            }
        ), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if result.get("skipped"):
        load_configs_to_memory(supabase)
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

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "entry": {edited_key: new_list},
            "version_number": result["version_number"],
            "versions": get_config_versions(),
        }
    ), 200


def _patch_aliases_english():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400
    try:
        result = apply_english_aliases_patch(
            supabase,
            data.get("entry"),
            triggered_by=_patch_triggered_by(),
            note=data.get("note"),
            get_config=get_config,
        )
    except (TypeError, ValueError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, "english_aliases"),
                "version_unchanged": True,
            }
        ), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if result.get("skipped"):
        load_configs_to_memory(supabase)
        return jsonify(
            {
                "ok": True,
                "message": "no database change",
                "new_count": merged_alias_count(get_config, "english_aliases"),
                "version": result.get("version_number"),
                "versions": get_config_versions(),
            }
        ), 200

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "message": "english aliases updated",
            "new_count": merged_alias_count(get_config, "english_aliases"),
            "version": result["version_number"],
            "versions": get_config_versions(),
        }
    ), 201


def _put_aliases_english_replace():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400
    try:
        result, edited_key, new_list = apply_english_aliases_replace(
            supabase,
            data.get("entry"),
            triggered_by=_patch_triggered_by(),
            note=data.get("note"),
            get_config=get_config,
        )
    except (TypeError, ValueError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, "english_aliases"),
                "version_unchanged": True,
            }
        ), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if result.get("skipped"):
        load_configs_to_memory(supabase)
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

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "entry": {edited_key: new_list},
            "version_number": result["version_number"],
            "versions": get_config_versions(),
        }
    ), 200


def _norm_key(s: str) -> str:
    return str(s).lower().strip()


def _find_existing_key(target: dict, input_key: str) -> str | None:
    nk = _norm_key(input_key)
    for k in target.keys():
        if _norm_key(str(k)) == nk:
            return str(k)
    return None


def _parse_edit_entry(data: dict) -> tuple[str, object, str | None]:
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


def _parse_delete_entry(data: dict) -> tuple[str, str | None]:
    entry = data.get("entry")
    if entry is None:
        entry = data
    if not isinstance(entry, dict):
        raise ValueError('"entry" must be a JSON object')

    input_key = entry.get("key", entry.get("input_key", entry.get("term")))
    if not isinstance(input_key, str) or not input_key.strip():
        raise ValueError('Provide a non-empty "key" in body.entry')
    return input_key, data.get("note")


def _delete_alias_key(config_type: str):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400

    try:
        input_key, note = _parse_delete_entry(data)
    except (TypeError, ValueError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, config_type),
                "version_unchanged": True,
            }
        ), 400

    snap = get_config(config_type)
    if not isinstance(snap, dict) or len(snap) == 0:
        return jsonify(
            {
                "error": "key not present",
                "version_number": get_latest_version_number(supabase, config_type),
                "version_unchanged": True,
                "versions": get_config_versions(),
            }
        ), 400

    full_snapshot = dict(snap)
    matched = _find_existing_key(full_snapshot, input_key)
    if matched is None:
        return jsonify(
            {
                "error": "key not present",
                "version_number": get_latest_version_number(supabase, config_type),
                "version_unchanged": True,
                "versions": get_config_versions(),
            }
        ), 400

    del full_snapshot[matched]
    if len(full_snapshot) == 0:
        return jsonify(
            {
                "error": "Cannot delete the last remaining key for this config type",
                "version_number": get_latest_version_number(supabase, config_type),
                "version_unchanged": True,
                "versions": get_config_versions(),
            }
        ), 400

    try:
        result = publish_config_version(
            supabase,
            config_type,
            full_snapshot,
            triggered_by=_patch_triggered_by(),
            note=note,
            merge=False,
        )
    except (TypeError, ValueError) as e:
        return jsonify(
            {
                "error": str(e),
                "version_number": get_latest_version_number(supabase, config_type),
                "version_unchanged": True,
            }
        ), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "message": f"{matched} deleted",
            "version_number": result["version_number"],
            "versions": get_config_versions(),
        }
    ), 200


def _patch_or_delete_common_errors(config_type: str, msg: str):
    return jsonify(
        {
            "error": msg,
            "version_number": get_latest_version_number(supabase, config_type),
            "version_unchanged": True,
        }
    ), 400


def _patch_edit_map_config(config_type: str):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400

    try:
        input_key, new_value, note = _parse_edit_entry(data)
    except (TypeError, ValueError) as e:
        return _patch_or_delete_common_errors(config_type, str(e))

    snap = get_config(config_type)
    if not isinstance(snap, dict) or len(snap) == 0:
        return _patch_or_delete_common_errors(
            config_type, f"No in-memory snapshot found for {config_type}"
        )

    full_snapshot = dict(snap)
    if config_type == "forbidden" and isinstance(full_snapshot.get("forbidden"), dict):
        inner = dict(full_snapshot["forbidden"])
        matched = _find_existing_key(inner, input_key)
        if matched is None:
            return _patch_or_delete_common_errors(config_type, f'key not found: "{input_key}"')
        if inner.get(matched) == new_value:
            return jsonify(
                {
                    "ok": True,
                    "message": "no database change",
                    "key": matched,
                    "version_number": get_latest_version_number(supabase, config_type),
                    "version_unchanged": True,
                    "versions": get_config_versions(),
                }
            ), 200
        inner[matched] = new_value
        full_snapshot["forbidden"] = inner
        edited_key = matched
    else:
        matched = _find_existing_key(full_snapshot, input_key)
        if matched is None:
            return _patch_or_delete_common_errors(config_type, f'key not found: "{input_key}"')
        if full_snapshot.get(matched) == new_value:
            return jsonify(
                {
                    "ok": True,
                    "message": "no database change",
                    "key": matched,
                    "version_number": get_latest_version_number(supabase, config_type),
                    "version_unchanged": True,
                    "versions": get_config_versions(),
                }
            ), 200
        full_snapshot[matched] = new_value
        edited_key = matched

    try:
        result = publish_config_version(
            supabase,
            config_type,
            full_snapshot,
            triggered_by=_patch_triggered_by(),
            note=note,
            merge=False,
        )
    except (TypeError, ValueError) as e:
        return _patch_or_delete_common_errors(config_type, str(e))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "message": f"{edited_key} has been edited",
            "version_number": result["version_number"],
            "versions": get_config_versions(),
        }
    ), 200


def _delete_map_config_key(config_type: str):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400

    try:
        input_key, note = _parse_delete_entry(data)
    except (TypeError, ValueError) as e:
        return _patch_or_delete_common_errors(config_type, str(e))

    snap = get_config(config_type)
    if not isinstance(snap, dict) or len(snap) == 0:
        return _patch_or_delete_common_errors(
            config_type, f"No in-memory snapshot found for {config_type}"
        )

    full_snapshot = dict(snap)
    if config_type == "forbidden" and isinstance(full_snapshot.get("forbidden"), dict):
        inner = dict(full_snapshot["forbidden"])
        matched = _find_existing_key(inner, input_key)
        if matched is None:
            return _patch_or_delete_common_errors(config_type, f'key not found: "{input_key}"')
        del inner[matched]
        if len(inner) == 0:
            return _patch_or_delete_common_errors(
                config_type, "Cannot delete the last remaining key for this config type"
            )
        full_snapshot["forbidden"] = inner
        deleted_key = matched
    else:
        matched = _find_existing_key(full_snapshot, input_key)
        if matched is None:
            return _patch_or_delete_common_errors(config_type, f'key not found: "{input_key}"')
        del full_snapshot[matched]
        if len(full_snapshot) == 0:
            return _patch_or_delete_common_errors(
                config_type, "Cannot delete the last remaining key for this config type"
            )
        deleted_key = matched

    try:
        result = publish_config_version(
            supabase,
            config_type,
            full_snapshot,
            triggered_by=_patch_triggered_by(),
            note=note,
            merge=False,
        )
    except (TypeError, ValueError) as e:
        return _patch_or_delete_common_errors(config_type, str(e))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    load_configs_to_memory(supabase)
    return jsonify(
        {
            "ok": True,
            "message": f"{deleted_key} has been deleted",
            "version_number": result["version_number"],
            "versions": get_config_versions(),
        }
    ), 200


# ─── Config routes: GET search; POST only glossary, forbidden, preferred, schemes ───


@app.route("/glossary", methods=["GET", "POST", "PATCH", "DELETE"])
def glossary():
    if request.method == "POST":
        return _post_config_version("glossary_terms")
    if request.method == "PATCH":
        return _patch_edit_map_config("glossary_terms")
    if request.method == "DELETE":
        return _delete_map_config_key("glossary_terms")
    term = request.args.get("term", "").strip()
    limit = parse_limit(request.args.get("limit"))
    return _json_response(search_glossary(term or None, limit))

#right now to update a row in ambiguous_terms, we can just get and add a new term, or we can add a full snapshot
#which is a list of objects

#patch being used to add a new value
@app.route("/ambiguity", methods=["GET", "PATCH"])
def ambiguous_terms():
    if request.method == "PATCH":
        return _patch_ambiguous_terms()
    term = request.args.get("term", "").strip()
    limit = parse_limit(request.args.get("limit"))
    return _json_response(search_ambiguous_terms(term or None, limit))

# {
#   "entry": {
#     "canonical_en": "test",
#     "gu_aliases":["test"]
#   }
# }

# {
#   "entry": {
#     "key": "artificial insemination"
#   }
# } for delete method

#patch being used to add a new value
@app.route("/aliases/en-gu", methods=["GET", "PATCH", "PUT", "DELETE"])
def en_gu_aliases():
    if request.method == "PATCH":
        return _patch_aliases_en_gu()
    if request.method == "PUT":
        return _put_aliases_en_gu_replace()
    if request.method == "DELETE":
        return _delete_alias_key("en-gujarati_aliases")
    term = request.args.get("term", "").strip()
    limit = parse_limit(request.args.get("limit"))
    return _json_response(search_en_gu(term or None, limit))

# {
#   "entry": {
#     "canonical": "udder",
#     "aliases":["xyaauu"]
#   }
# }
#patch being used to add a new value
@app.route("/aliases/english", methods=["GET", "PATCH", "PUT", "DELETE"])
def english_aliases():
    if request.method == "PATCH":
        return _patch_aliases_english()
    if request.method == "PUT":
        return _put_aliases_english_replace()
    if request.method == "DELETE":
        return _delete_alias_key("english_aliases")
    term = request.args.get("term", "").strip()
    limit = parse_limit(request.args.get("limit"))
    return _json_response(search_english_aliases(term or None, limit))


@app.route("/forbidden", methods=["GET", "POST", "PATCH", "DELETE"])
def forbidden():
    if request.method == "POST":
        return _post_config_version("forbidden")
    if request.method == "PATCH":
        return _patch_edit_map_config("forbidden")
    if request.method == "DELETE":
        return _delete_map_config_key("forbidden")
    term = request.args.get("term", "").strip()
    limit = parse_limit(request.args.get("limit"))
    return _json_response(search_forbidden(term or None, limit))


@app.route("/preferred", methods=["GET", "POST", "PATCH", "DELETE"])
def preferred():
    if request.method == "POST":
        return _post_config_version("preferred")
    if request.method == "PATCH":
        return _patch_edit_map_config("preferred")
    if request.method == "DELETE":
        return _delete_map_config_key("preferred")
    term = request.args.get("term", "").strip()
    limit = parse_limit(request.args.get("limit"))
    return _json_response(search_preferred(term or None, limit))


@app.route("/schemes", methods=["GET", "POST", "PATCH", "DELETE"])
def schemes():
    if request.method == "POST":
        return _post_config_version("schemes")
    if request.method == "PATCH":
        return _patch_edit_map_config("schemes")
    if request.method == "DELETE":
        return _delete_map_config_key("schemes")
    term = request.args.get("term", "").strip()
    limit = parse_limit(request.args.get("limit"))
    return _json_response(search_schemes(term or None, limit))


# ─── Full cache / reload ───────────────────────────────────────────────────


@app.route("/configs", methods=["GET"])
def all_configs():
    """Default: `configs` + `versions` (latest row per type). Use ?format=flat for snapshots only."""
    if request.args.get("format") == "flat":
        return jsonify(get_all_configs())
    return jsonify(get_configs_and_versions())


# ROLLBACK_ALLOWED_INPUT_TYPES = (
#     "glossary",
#     "ambiguous_terms",
#     "en-gujarati_aliases",
#     "english_aliases",
#     "forbidden",
#     "preferred",
#     "schemes",
# )

@app.route("/configs/rollback", methods=["POST"])
def rollback_config():
    return _rollback_config_version()

#returns a config with all versions
@app.route("/configs/versions", methods=["GET"])
def config_versions_by_type():
    return _list_versions_for_config()


@app.route("/configs/reload", methods=["POST"])
def reload_configs():
    cache = load_configs_to_memory(supabase)
    return jsonify(
        {
            "message": f"Reloaded {len(cache)} config types from latest version rows.",
            "versions": get_config_versions(),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)


