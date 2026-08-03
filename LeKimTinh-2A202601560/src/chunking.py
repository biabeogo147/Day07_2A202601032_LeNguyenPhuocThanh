from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []

        # Split while keeping sentence-ending punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Remove empty sentences and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i + self.max_sentences_per_chunk])
            chunks.append(chunk)

        return chunks

class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # # TODO: implement recursive splitting strategy
        # raise NotImplementedError("Implement RecursiveChunker.chunk")
        """
        Split text into chunks whose lengths do not exceed chunk_size.
        """
        text = text.strip()

        if not text:
            return []

        pieces = self._split(text, self.separators)

        # Merge adjacent small pieces into larger chunks.
        chunks: list[str] = []
        current_chunk = ""

        for piece in pieces:
            if not piece:
                continue

            if len(current_chunk) + len(piece) <= self.chunk_size:
                current_chunk += piece
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                current_chunk = piece

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
#        raise NotImplementedError("Implement RecursiveChunker._split")
        """
        Recursively split current_text using the available separators.

        The separators are tried in priority order. Oversized pieces are
        recursively split using the next separator.
        """
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Empty separator means splitting by individual characters.
        if separator == "":
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        raw_parts = current_text.split(separator)

        # Separator does not exist: try the next separator.
        if len(raw_parts) == 1:
            return self._split(current_text, next_separators)

        pieces: list[str] = []

        for index, part in enumerate(raw_parts):
            # Restore the separator so text content is not lost.
            if index < len(raw_parts) - 1:
                part += separator

            if not part:
                continue

            if len(part) <= self.chunk_size:
                pieces.append(part)
            else:
                pieces.extend(self._split(part, next_separators))

        return pieces

def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    #raise NotImplementedError("Implement compute_similarity")
    
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must have the same length")

    magnitude_a = math.sqrt(sum(value**2 for value in vec_a))
    magnitude_b = math.sqrt(sum(value**2 for value in vec_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # TODO: call each chunker, compute stats, return comparison dict
        #raise NotImplementedError("Implement ChunkingStrategyComparator.compare")
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size),
            "by_sentences": SentenceChunker(),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        result = {}

        for strategy_name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            chunk_lengths = [len(chunk) for chunk in chunks]

            result[strategy_name] = {
                "count": len(chunks),
                "avg_length": (
                    sum(chunk_lengths) / len(chunk_lengths)
                    if chunk_lengths
                    else 0.0
                ),
                "chunks": chunks,
            }

        return result