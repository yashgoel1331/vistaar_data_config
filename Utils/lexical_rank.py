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
    """Word tokens; falls back to whitespace chunks if \\w misses script edge cases."""
    n = normalize_text(value)
    if not n:
        return []
    primary = TOKEN_RE.findall(n)
    if primary:
        return primary
    return [p for p in n.split() if p]


def token_overlap_score(query: str, text: str) -> float:
    q_tokens = set(tokenize(query))
    t_tokens = set(tokenize(text))
    if not q_tokens or not t_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)


def lexical_overlap_score(query: str, text: str) -> float:
    """Fraction of query tokens that appear in text [0, 1]."""
    return token_overlap_score(query, text)


def _soft_token_match_score(query: str, text: str) -> float:
    """
    Weaker match when exact token overlap is 0: each query token may match as a
    substring of the blob, or as a prefix/suffix of a text token (e.g. mil → milk).
    """
    qn = normalize_text(query)
    bn = normalize_text(text)
    if not qn or not bn:
        return 0.0

    q_tokens = tokenize(query)
    if not q_tokens:
        q_tokens = [qn]

    t_tokens = tokenize(text)
    t_list = list(dict.fromkeys(t_tokens)) if t_tokens else []

    hits = 0
    for qt in q_tokens:
        if not qt:
            continue
        if qt in bn:
            hits += 1
            continue
        matched = False
        for tt in t_list:
            if len(qt) >= 2 and len(tt) >= 2:
                if tt.startswith(qt) or qt.startswith(tt):
                    matched = True
                    break
        if matched:
            hits += 1

    if not hits:
        return 0.0
    return 0.2 + 0.65 * (hits / len(q_tokens))


def lexical_rank_score(query: str, text: str) -> float:
    """
    Combined score: normalized full substring of query in text wins;
    then exact token overlap; then soft substring/prefix between tokens.
    Returns roughly [0, ~1.01].
    """
    qn = normalize_text(query)
    bn = normalize_text(text)
    if not qn:
        return 0.0
    if qn in bn:
        return 1.0 + min(0.01, len(qn) / max(len(bn), 1) * 0.01)
    base = token_overlap_score(query, text)
    if base > 0:
        return base
    soft = _soft_token_match_score(query, text)
    if soft > 0:
        return soft
    return 0.0
