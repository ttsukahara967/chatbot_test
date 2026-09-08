def build_prompt(query: str, contexts: list[str]) -> str:
    if not contexts:
        return f"質問: {query}\n回答:"

    context_block = "\n".join(f"- {c}" for c in contexts)
    return (
        "以下の参考情報を踏まえて、質問に答えてください。\n\n"
        f"参考情報:\n{context_block}\n\n"
        f"質問: {query}\n"
        "回答:"
    )
