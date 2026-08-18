import io

import pandas as pd


def parse_csv(data: bytes) -> str:
    """Robust CSV parser: handles encodings, malformed rows, and empty files."""
    # 1) Decode with fallback encodings (Excel exports often use cp1252 / utf-8-sig)
    text = None
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            text = data.decode(enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if text is None:
        text = data.decode("utf-8", errors="ignore")

    if not text.strip():
        raise ValueError("CSV file is empty.")

    # 2) Parse, skipping malformed lines instead of crashing
    df = pd.read_csv(io.StringIO(text), on_bad_lines="skip")

    if df.empty:
        raise ValueError("CSV has no data rows.")

    # 3) Convert each row into readable text for embedding
    cols = [str(c) for c in df.columns]
    lines = []
    for _, row in df.iterrows():
        parts = [f"{c}: {row[c]}" for c in cols if pd.notna(row[c])]
        if parts:
            lines.append(" | ".join(parts))

    if not lines:
        raise ValueError("CSV rows contain no usable data.")

    return "\n".join(lines)