SYSTEM_PROMPT = (
    "You are an enterprise knowledge assistant. Answer strictly using the provided context. "
    "Cite sources with [n] notation matching the numbered snippets. If the answer is not in "
    "the context, say you don't know. Be concise and factual."
)


def build_rag_prompt(query: str, contexts, history=None) -> str:
    ctx = "\n\n".join(
        f"[{i + 1}] (Source: {c.document_title}, chunk {c.chunk_index})\n{c.content}"
        for i, c in enumerate(contexts)
    )
    hist = ""
    if history:
        turns = "\n".join(f"{m.role}: {m.content}" for m in history[-6:])
        hist = f"Conversation so far:\n{turns}\n\n"
    return f"{hist}Context:\n{ctx}\n\nQuestion: {query}\n\nAnswer (cite sources with [n]):"