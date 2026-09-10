def build_messages(query: str, contexts: list[str]) -> list[dict]:
    if contexts:
        context_block = "\n".join(f"- {c}" for c in contexts)
        system_content = (
            "あなたは社内向けの質問応答アシスタントです。"
            "以下の参考情報に基づいて、質問に簡潔かつ正確に答えてください。"
            "参考情報に答えがない場合は、分からない旨を伝えてください。\n\n"
            f"参考情報:\n{context_block}"
        )
    else:
        system_content = "あなたは質問応答アシスタントです。質問に簡潔に答えてください。"

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": query},
    ]
