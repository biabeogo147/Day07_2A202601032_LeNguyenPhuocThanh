from __future__ import annotations

from typing import Any, Callable

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
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # TODO: initialize chromadb client + collection
            client = chromadb.Client()

            self._collection = client.get_or_create_collection(
                name=self._collection_name
            )

            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # TODO: build a normalized stored record for one document
        #raise NotImplementedError("Implement EmbeddingStore._make_record")
        """Build one normalized record from a Document."""
        content = doc.content
        metadata = dict(doc.metadata or {})
        metadata.setdefault("doc_id", doc.id)

        embedding = self._embedding_fn(content)

        record_id = f"{self._collection_name}-{self._next_index}"
        self._next_index += 1

        return {
            "id": record_id,
            "content": content,
            "metadata": metadata,
            "embedding": embedding,
        }
    
    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        # TODO: run in-memory similarity search over provided records
        #raise NotImplementedError("Implement EmbeddingStore._search_records")

        """Run similarity search over the provided records."""
        if top_k <= 0 or not records:
            return []

        query_embedding = self._embedding_fn(query)

        results: list[dict[str, Any]] = []

        for record in records:
            similarity = _dot(
                query_embedding,
                record["embedding"],
            )

            results.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": dict(record["metadata"]),
                    "score": similarity,
                }
            )

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        # TODO: embed each doc and add to store
        #raise NotImplementedError("Implement EmbeddingStore.add_documents")
        if not docs:
            return

        records = [self._make_record(doc) for doc in docs]

        if self._use_chroma and self._collection is not None:
            self._collection.add(
                ids=[record["id"] for record in records],
                documents=[record["content"] for record in records],
                embeddings=[record["embedding"] for record in records],
                metadatas=[record["metadata"] for record in records],
            )
        else:
            self._store.extend(records)
    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        # TODO: embed query, compute similarities, return top_k
        #raise NotImplementedError("Implement EmbeddingStore.search")
        if top_k <= 0:
            return []

        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)

            query_result = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )

            ids = query_result.get("ids", [[]])[0]
            documents = query_result.get("documents", [[]])[0]
            metadatas = query_result.get("metadatas", [[]])[0]
            distances = query_result.get("distances", [[]])[0]

            results: list[dict[str, Any]] = []

            for record_id, content, metadata, distance in zip(
                ids,
                documents,
                metadatas,
                distances,
            ):
                results.append(
                    {
                        "id": record_id,
                        "content": content,
                        "metadata": metadata or {},
                        # Chroma returns distance: lower means more similar.
                        "score": 1.0 - float(distance),
                    }
                )

            return results

        return self._search_records(
            query=query,
            records=self._store,
            top_k=top_k,
        )
    
    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        # TODO
        #raise NotImplementedError("Implement EmbeddingStore.get_collection_size")
        if self._use_chroma and self._collection is not None:
            return self._collection.count()

        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        # TODO: filter by metadata, then search among filtered chunks
        #raise NotImplementedError("Implement EmbeddingStore.search_with_filter")
        if top_k <= 0:
            return []

        if not metadata_filter:
            return self.search(query, top_k)

        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)

            query_result = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=metadata_filter,
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )

            ids = query_result.get("ids", [[]])[0]
            documents = query_result.get("documents", [[]])[0]
            metadatas = query_result.get("metadatas", [[]])[0]
            distances = query_result.get("distances", [[]])[0]

            return [
                {
                    "id": record_id,
                    "content": content,
                    "metadata": metadata or {},
                    "score": 1.0 - float(distance),
                }
                for record_id, content, metadata, distance in zip(
                    ids,
                    documents,
                    metadatas,
                    distances,
                )
            ]

        filtered_records = [
            record
            for record in self._store
            if all(
                record["metadata"].get(key) == expected_value
                for key, expected_value in metadata_filter.items()
            )
        ]

        return self._search_records(
            query=query,
            records=filtered_records,
            top_k=top_k,
        )
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        # TODO: remove all stored chunks where metadata['doc_id'] == doc_id
        #raise NotImplementedError("Implement EmbeddingStore.delete_document")
        if self._use_chroma and self._collection is not None:
            matching = self._collection.get(
                where={"doc_id": doc_id},
                include=[],
            )

            matching_ids = matching.get("ids", [])

            if not matching_ids:
                return False

            self._collection.delete(ids=matching_ids)
            return True

        original_size = len(self._store)

        self._store = [
            record
            for record in self._store
            if record["metadata"].get("doc_id") != doc_id
        ]

        return len(self._store) < original_size