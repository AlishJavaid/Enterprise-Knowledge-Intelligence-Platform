def rerank(query: str, passages: list[str], top_k: int) -> list[tuple[int, float]]:
    """
    Lightweight Reranker: Skips the heavy Cross-Encoder to save RAM.
    Relies on the Reciprocal Rank Fusion (RRF) scores from the hybrid retriever.
    """
    return [(i, 1.0 / (i + 1)) for i in range(min(top_k, len(passages)))]