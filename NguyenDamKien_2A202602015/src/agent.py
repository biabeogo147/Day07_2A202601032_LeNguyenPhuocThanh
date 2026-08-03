from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        retrieved = self.store.search(question, top_k=top_k)
        context_items = []
        for idx, item in enumerate(retrieved, start=1):
            context_items.append(f"Chunk {idx}: {item.get('content', '')}")

        prompt = (
            "You are a helpful assistant. Answer the question using the following context. "
            "If the answer is not contained in the context, say you don't know.\n\n"
            f"Context:\n{chr(10).join(context_items)}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
