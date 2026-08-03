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
        results = self.store.search(question, top_k=top_k)
        context_blocks: list[str] = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            source = metadata.get("source_url") or metadata.get("source")
            source_line = f"\nNguồn: {source}" if source else ""
            context_blocks.append(
                f"[Ngữ cảnh {index}]{source_line}\n{result.get('content', '')}"
            )

        context = "\n\n".join(context_blocks) or "(Không tìm thấy ngữ cảnh liên quan.)"
        prompt = (
            "Bạn là trợ lý hỏi đáp cho một cơ sở tri thức. "
            "Chỉ sử dụng thông tin trong phần NGỮ CẢNH để trả lời. "
            "Nếu ngữ cảnh không đủ, hãy nói rõ rằng không tìm thấy đủ thông tin; không suy đoán.\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI:\n{question}\n\n"
            "TRẢ LỜI:"
        )
        return self.llm_fn(prompt)
