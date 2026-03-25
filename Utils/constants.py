"""Shared constants for config API naming and validation."""

from __future__ import annotations

DB_CONFIG_TYPES = (
    "glossary_terms",
    "ambiguous_terms",
    "en-gujarati_aliases",
    "english_aliases",
    "forbidden",
    "preferred",
    "schemes",
)

CONFIG_TYPE_MAP = {
    "glossary": "glossary_terms",
    "glossary_terms": "glossary_terms",
    "ambiguity": "ambiguous_terms",
    "ambiguous_terms": "ambiguous_terms",
    "en-gujarati_aliases": "en-gujarati_aliases",
    "english_aliases": "english_aliases",
    "forbidden": "forbidden",
    "preferred": "preferred",
    "schemes": "schemes",
}

ROLLBACK_ALLOWED_INPUT_TYPES = (
    "glossary",
    "ambiguity",
    "en-gujarati_aliases",
    "english_aliases",
    "forbidden",
    "preferred",
    "schemes",
)
