def split_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[dict]:
    """Sliding-window chunking with sentence-boundary snapping."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start, n = 0, len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            window = text[start:end]
            cut = max(window.rfind("."), window.rfind("!"), window.rfind("?"), window.rfind("\n"))
            if cut > chunk_size // 2:
                end = start + cut + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append({"content": piece, "char_start": start, "char_end": end})
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks