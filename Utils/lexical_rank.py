"""
Token-overlap and substring-aware ranking for in-memory text search.
Shared by agents/search.py (Marqo reranking) and Utils/config_search.py (config cache).
No heavy dependencies (no marqo).
"""
from __future__ import annotations

import re
from typing import List

TOKEN_RE = re.compile(r"[\w\-]+", re.UNICODE)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def tokenize(value: str) -> List[str]:
    return TOKEN_RE.findall(normalize_text(value))


def token_overlap_score(query: str, text: str) -> float:
    q_tokens = set(tokenize(query))
    t_tokens = set(tokenize(text))
    if not q_tokens or not t_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)


def lexical_overlap_score(query: str, text: str) -> float:
    """Fraction of query tokens that appear in text [0, 1]."""
    return token_overlap_score(query, text)


def lexical_rank_score(query: str, text: str) -> float:
    """
    Combined score: normalized full substring of query in text wins;
    otherwise token overlap. Returns roughly [0, ~1.01].
    """
    qn = normalize_text(query)
    bn = normalize_text(text)
    if not qn:
        return 0.0
    if qn in bn:
        return 1.0 + min(0.01, len(qn) / max(len(bn), 1) * 0.01)
    return token_overlap_score(query, text)
