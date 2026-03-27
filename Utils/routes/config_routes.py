"""Core config route definitions with no inline business logic."""

from __future__ import annotations

from flask import Blueprint, request

from Utils.services.config_api_service import ConfigAPIService

config_bp = Blueprint("config_routes", __name__)
_service: ConfigAPIService | None = None


def init_config_routes(service: ConfigAPIService) -> Blueprint:
    """Endpoint wiring; attaches service instance and returns config blueprint."""
    global _service
    _service = service
    return config_bp


@config_bp.route("/glossary", methods=["GET", "POST", "PATCH", "DELETE"])
def glossary():
    """Endpoint: /glossary; input query/body by method; delegates glossary CRUD to service."""
    if request.method == "POST":
        return _service.post_config_version("glossary_terms", request)
    if request.method == "PATCH":
        return _service.patch_edit_map_config("glossary_terms", request)
    if request.method == "DELETE":
        return _service.delete_map_config_key("glossary_terms", request)
    return _service.search_glossary_endpoint(request)


#right now to update a row in ambiguous_terms, we can just get and add a new term, or we can add a full snapshot
#which is a list of objects
#
#patch being used to add a new value
@config_bp.route("/ambiguity", methods=["GET", "PATCH"])
def ambiguous_terms():
    """Endpoint: /ambiguity; input query for GET, entry body for PATCH; delegates to service."""
    if request.method == "PATCH":
        return _service.patch_ambiguous_terms(request)
    return _service.search_ambiguous_terms_endpoint(request)


@config_bp.route("/forbidden", methods=["GET", "POST", "PATCH", "DELETE"])
def forbidden():
    """Endpoint: /forbidden; input query/body by method; delegates forbidden CRUD to service."""
    if request.method == "POST":
        return _service.post_config_version("forbidden", request)
    if request.method == "PATCH":
        return _service.patch_edit_map_config("forbidden", request)
    if request.method == "DELETE":
        return _service.delete_map_config_key("forbidden", request)
    return _service.search_forbidden_endpoint(request)


@config_bp.route("/preferred", methods=["GET", "POST", "PATCH", "DELETE"])
def preferred():
    """Endpoint: /preferred; input query/body by method; delegates preferred CRUD to service."""
    if request.method == "POST":
        return _service.post_config_version("preferred", request)
    if request.method == "PATCH":
        return _service.patch_edit_map_config("preferred", request)
    if request.method == "DELETE":
        return _service.delete_map_config_key("preferred", request)
    return _service.search_preferred_endpoint(request)


@config_bp.route("/schemes", methods=["GET", "POST", "PATCH", "DELETE"])
def schemes():
    """Endpoint: /schemes; input query/body by method; delegates schemes CRUD to service."""
    if request.method == "POST":
        return _service.post_config_version("schemes", request)
    if request.method == "PATCH":
        return _service.patch_edit_map_config("schemes", request)
    if request.method == "DELETE":
        return _service.delete_map_config_key("schemes", request)
    return _service.search_schemes_endpoint(request)


# ─── Full cache / reload ───────────────────────────────────────────────────
@config_bp.route("/configs", methods=["GET"])
def all_configs():
    """Endpoint: /configs; input optional format query; returns cached configs/versions."""
    return _service.all_configs(request)


@config_bp.route("/configs/rollback", methods=["POST"])
def rollback_config():
    """Endpoint: /configs/rollback; input config_type+version JSON; creates rollback version."""
    return _service.rollback_config_version(request)


@config_bp.route("/configs/versions", methods=["GET"])
def config_versions_by_type():
    """Endpoint: /configs/versions; input config_type query; returns all version metadata."""
    return _service.list_versions_for_config(request)


@config_bp.route("/configs/reload", methods=["POST"])
def reload_configs():
    """Endpoint: /configs/reload; no input body; reloads in-memory dictionary from DB."""
    return _service.reload_configs()
