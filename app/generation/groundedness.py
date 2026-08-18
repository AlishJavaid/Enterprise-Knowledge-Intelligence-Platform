import re


def _tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"\w+", s.lower()) if len(t) > 3}


def check_groundedness(answer: str, contexts) -> tuple[float, bool]:
    """
    Baseline hallucination heuristic: token overlap between answer and context.
    Swap in an NLI / entailment model for stricter guarantees.
    Returns (confidence, hallucinated_flag).
    """
    if not contexts:
        return 0.0, True

    ctx_tokens: set[str] = set()
    for c in contexts:
        ctx_tokens |= _tokens(c.content)

    ans_tokens = _tokens(answer)
    if not ans_tokens:
        return 0.0, True

    overlap = len(ans_tokens & ctx_tokens) / len(ans_tokens)
    return round(overlap, 4), overlap < 0.3