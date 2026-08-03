from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    GEMINI_EMBEDDING_MODEL,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    GeminiEmbedder,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Thư mục dữ liệu mặc định cho demo = bộ khởi động cố định của lớp K4.

# Đổi bằng biến môi trường: LAB_DATA_DIR=data/<thu-muc-cua-nhom> python3 main.py
DEFAULT_DATA_DIR = "data/k4_ecommerce"


def _select_embedder():
    """Chọn backend nhúng theo biến môi trường EMBEDDING_PROVIDER (gemini | mock | local | openai)."""
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "gemini").strip().lower()
    if provider == "gemini":
        try:
            return GeminiEmbedder(model_name=os.getenv("GEMINI_EMBEDDING_MODEL", GEMINI_EMBEDDING_MODEL))
        except Exception as e:
            print(f"Gemini embedder không sẵn sàng ({e}); tạm dùng mock.")
            return _mock_embed
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            print("Local embedder không sẵn sàng; tạm dùng mock.")
            return _mock_embed
    if provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            print("OpenAI embedder không sẵn sàng; tạm dùng mock.")
            return _mock_embed
    return _mock_embed


def gemini_llm(prompt: str) -> str:
    """Gọi Gemini LLM nếu có API key, ngược lại dùng demo LLM."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        preview = prompt[:400].replace("\n", " ")
        return f"[DEMO LLM] Generated answer from prompt preview: {preview}..."
    try:
        import requests

        model_name = os.getenv("GEMINI_MODEL", "models/gemini-3.5-flash-lite")
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]
        return f"[DEMO LLM] Generated response."
    except Exception as e:
        preview = prompt[:400].replace("\n", " ")
        return f"[DEMO LLM Fallback] {preview}..."


def demo_llm(prompt: str) -> str:
    return gemini_llm(prompt)



def run_manual_demo(question: str | None = None, data_dir: str | None = None) -> int:
    data_dir = data_dir or DEFAULT_DATA_DIR
    query = question or "Tóm tắt thông tin chính từ bộ tài liệu."

    print("=== Demo pipeline nạp dữ liệu (ingest.build_knowledge_base) ===")
    print(f"Thư mục dữ liệu: {data_dir}")
    if not Path(data_dir).exists():
        print(f"Không tìm thấy thư mục dữ liệu: {data_dir}")
        print("Thu thập tài liệu vào thư mục này (xem docs/DATA_COLLECTION.md) rồi chạy lại:")
        print("  python3 main.py")
        return 1

    embedder = _select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    print(f"Backend nhúng: {backend}")
    if backend == "mock embeddings fallback":
        print(
            "Lưu ý: mock chỉ để chạy thử/unit test và KHÔNG phản ánh chất lượng ngữ nghĩa. "
            "Ở Giai đoạn 2, đặt EMBEDDING_PROVIDER=local để so sánh retrieval có ý nghĩa."
        )

    # Pipeline cung cấp sẵn: parse front matter -> chunk -> gắn metadata -> nạp store.
    store = build_knowledge_base(data_dir, embedding_fn=embedder)
    print(f"Đã nạp {store.get_collection_size()} chunk vào EmbeddingStore")

    print("\n=== Tìm kiếm (EmbeddingStore.search) ===")
    print(f"Câu hỏi: {query}")
    for index, result in enumerate(store.search(query, top_k=3), start=1):
        print(f"{index}. score={result['score']:.3f} source={result['metadata'].get('source')}")
        print(f"   {result['content'][:120].replace(chr(10), ' ')}...")

    print("\n=== KnowledgeBaseAgent ===")
    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)
    print(agent.answer(query, top_k=3))
    return 0


def main() -> int:
    question = " ".join(sys.argv[1:]).strip() or None
    data_dir = os.getenv("LAB_DATA_DIR", DEFAULT_DATA_DIR)
    return run_manual_demo(question=question, data_dir=data_dir)


if __name__ == "__main__":
    raise SystemExit(main())
