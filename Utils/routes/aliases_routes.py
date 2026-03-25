"""Alias route definitions with no inline business logic."""

from __future__ import annotations

from flask import Blueprint, request

from Utils.services.config_api_service import ConfigAPIService

aliases_bp = Blueprint("aliases_routes", __name__)
_service: ConfigAPIService | None = None


def init_aliases_routes(service: ConfigAPIService) -> Blueprint:
    """Endpoint wiring; attaches service instance and returns aliases blueprint."""
    global _service
    _service = service
    return aliases_bp


# {
#   "entry": {
#     "canonical_en": "test",
#     "gu_aliases":["test"]
#   }
# }
#
# {
#   "entry": {
#     "key": "artificial insemination"
#   }
# } for delete method
#
#patch being used to add a new value
@aliases_bp.route("/aliases/en-gu", methods=["GET", "PATCH", "PUT", "DELETE"])
def en_gu_aliases():
    """Endpoint: /aliases/en-gu; input query/body per method; delegates to alias service logic."""
    if request.method == "PATCH":
        return _service.patch_aliases_en_gu(request)
    if request.method == "PUT":
        return _service.put_aliases_en_gu_replace(request)
    if request.method == "DELETE":
        return _service.delete_alias_key("en-gujarati_aliases", request)
    return _service.search_en_gu_endpoint(request)


# {
#   "entry": {
#     "canonical": "udder",
#     "aliases":["xyaauu"]
#   }
# }
#patch being used to add a new value
@aliases_bp.route("/aliases/english", methods=["GET", "PATCH", "PUT", "DELETE"])
def english_aliases():
    """Endpoint: /aliases/english; input query/body per method; delegates to alias service logic."""
    if request.method == "PATCH":
        return _service.patch_aliases_english(request)
    if request.method == "PUT":
        return _service.put_aliases_english_replace(request)
    if request.method == "DELETE":
        return _service.delete_alias_key("english_aliases", request)
    return _service.search_english_aliases_endpoint(request)
