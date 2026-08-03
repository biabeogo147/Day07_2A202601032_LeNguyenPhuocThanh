from __future__ import annotations

from typing import Any, Callable
from uuid import uuid4

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._client = None
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            self._client = chromadb.EphemeralClient()
            internal_name = f"lab7_{uuid4().hex}"
            self._collection = self._client.get_or_create_collection(
                name=internal_name,
                configuration={"hnsw": {"space": "ip"}},
                embedding_function=None,
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._client = None
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = {
            str(key): self._normalize_metadata_value(value)
            for key, value in dict(doc.metadata).items()
        }
        metadata.setdefault("doc_id", str(doc.id))
        record = {
            "id": f"{doc.id}::{self._next_index}",
            "content": doc.content,
            "metadata": metadata,
            "embedding": [float(value) for value in self._embedding_fn(doc.content)],
        }
        self._next_index += 1
        return record

    @staticmethod
    def _normalize_metadata_value(value: Any) -> str | int | float | bool | list:
        """Convert arbitrary Document metadata into values accepted by ChromaDB."""
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) for item in value):
            return value
        if value is None:
            return ""
        return str(value)

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0 or not records:
            return []

        query_embedding = self._embedding_fn(query)
        results = [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": dict(record["metadata"]),
                "score": float(_dot(query_embedding, record["embedding"])),
            }
            for record in records
        ]
        results.sort(key=lambda result: result["score"], reverse=True)
        return results[:top_k]

    def _search_chroma(self, query: str, top_k: int, where: dict | None = None) -> list[dict[str, Any]]:
        if top_k <= 0 or self._collection is None:
            return []

        count = self._collection.count()
        if count == 0:
            return []

        query_result = self._collection.query(
            query_embeddings=[[float(value) for value in self._embedding_fn(query)]],
            n_results=min(top_k, count),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        ids = (query_result.get("ids") or [[]])[0]
        documents = (query_result.get("documents") or [[]])[0]
        metadatas = (query_result.get("metadatas") or [[]])[0]
        distances = (query_result.get("distances") or [[]])[0]

        results = [
            {
                "id": record_id,
                "content": document or "",
                "metadata": metadata or {},
                "score": 1.0 - float(distance),
            }
            for record_id, document, metadata, distance in zip(ids, documents, metadatas, distances)
        ]
        results.sort(key=lambda result: result["score"], reverse=True)
        return results

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        records = [self._make_record(doc) for doc in docs]
        if not records:
            return

        # Keep a memory mirror so a Chroma failure can fall back without data loss.
        self._store.extend(records)
        if not self._use_chroma or self._collection is None:
            return

        try:
            self._collection.add(
                ids=[record["id"] for record in records],
                documents=[record["content"] for record in records],
                embeddings=[record["embedding"] for record in records],
                metadatas=[record["metadata"] for record in records],
            )
        except Exception:
            self._use_chroma = False

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if top_k <= 0:
            return []
        if self._use_chroma:
            try:
                return self._search_chroma(query, top_k)
            except Exception:
                self._use_chroma = False
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            try:
                return int(self._collection.count())
            except Exception:
                self._use_chroma = False
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k)
        if top_k <= 0:
            return []

        normalized_filter = {
            str(key): self._normalize_metadata_value(value)
            for key, value in metadata_filter.items()
        }
        if self._use_chroma:
            conditions = [{key: value} for key, value in normalized_filter.items()]
            where = conditions[0] if len(conditions) == 1 else {"$and": conditions}
            try:
                return self._search_chroma(query, top_k, where=where)
            except Exception:
                self._use_chroma = False

        filtered_records = [
            record
            for record in self._store
            if all(record["metadata"].get(key) == value for key, value in normalized_filter.items())
        ]
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        normalized_doc_id = str(doc_id)
        record_ids = [
            record["id"]
            for record in self._store
            if record["metadata"].get("doc_id") == normalized_doc_id
        ]
        if not record_ids:
            return False

        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(ids=record_ids)
            except Exception:
                self._use_chroma = False

        ids_to_remove = set(record_ids)
        self._store = [record for record in self._store if record["id"] not in ids_to_remove]
        return True
