from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
STUDENT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = STUDENT_ROOT / "src"

for path in [str(ROOT), str(STUDENT_ROOT), str(SRC_ROOT)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from src.agent import KnowledgeBaseAgent
from src.chunking import SentenceChunker
from src.embeddings import GeminiEmbedder
from src.models import Document
from src.store import EmbeddingStore

TEXT_EXTENSIONS = {".md", ".txt"}
DATA_DIR = ROOT / "data" / "shopee_customer_support"
DEFAULT_QUESTIONS = [
    "Shopee có hỗ trợ đổi hàng không? Nếu hàng có vấn đề thì người mua phải làm gì?",
    "Thời hạn gửi yêu cầu trả hàng/hoàn tiền trên Shopee là bao lâu?",
    "Người mua cần gửi yêu cầu trả hàng bằng cách nào trên ứng dụng Shopee?",
    "Người bán phải chịu phí vận chuyển hoàn trả trong trường hợp nào?",
    "Có những phương thức gửi hàng hoàn trả nào và chi phí ra sao?",
]


def load_documents(data_dir: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8")
        metadata = {"source": str(path)}
        documents.append(Document(id=path.stem, content=text, metadata=metadata))
    return documents


def build_store(data_dir: Path, chunker: SentenceChunker) -> EmbeddingStore:
    docs = load_documents(data_dir)
    chunk_docs: list[Document] = []
    for doc in docs:
        for index, piece in enumerate(chunker.chunk(doc.content)):
            chunk_meta = dict(doc.metadata)
            chunk_meta["doc_id"] = doc.id
            chunk_meta["chunk_index"] = index
            chunk_docs.append(
                Document(id=f"{doc.id}::chunk_{index}", content=piece, metadata=chunk_meta)
            )

    store = EmbeddingStore(collection_name="demo_shopee", embedding_fn=GeminiEmbedder())
    store.add_documents(chunk_docs)
    return store


def call_gemini_llm(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return f"[DEMO LLM] Không có API key. Đang dùng phản hồi mẫu cho prompt: {prompt[:200]}"

    try:
        import requests

        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]
        return "[DEMO LLM] Không nhận được nội dung từ Gemini."
    except Exception as exc:
        return f"[DEMO LLM Fallback] Lỗi khi gọi Gemini: {exc}"


def run_questions(questions: Iterable[str], top_k: int = 3) -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục dữ liệu: {DATA_DIR}")

    chunker = SentenceChunker(max_sentences_per_chunk=3)
    store = build_store(DATA_DIR, chunker)
    agent = KnowledgeBaseAgent(store=store, llm_fn=call_gemini_llm)

    print("=== Chạy thực nghiệm RAG với chiến lược SentenceChunker ===")
    print(f"Dữ liệu: {DATA_DIR}")
    print(f"Số chunk đã nạp: {store.get_collection_size()}")
    print()

    for idx, question in enumerate(questions, start=1):
        print(f"[{idx}] Câu hỏi: {question}")
        retrieved = store.search(question, top_k=top_k)
        for pos, item in enumerate(retrieved, start=1):
            content = item.get("content", "")
            preview = " ".join(content.split())[:160]
            print(f"  {pos}. score={item.get('score', 0):.4f} | {preview}...")
        print()
        answer = agent.answer(question, top_k=top_k)
        print("=> Trả lời:")
        print(answer)
        print("-" * 80)


def main() -> int:
    args = [arg for arg in sys.argv[1:] if arg.strip()]
    if args:
        questions = args
    else:
        questions = DEFAULT_QUESTIONS
    run_questions(questions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
