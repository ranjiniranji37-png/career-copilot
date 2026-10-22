"""Lightweight RAG: chunk -> TF-IDF vectors -> cosine-similarity retrieval.

Runs fully offline (no embedding API needed). To upgrade, swap the vectorizer
for an embedding model + vector DB (FAISS / Chroma) behind the same interface.
"""
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    source: str
    text: str


def chunk_text(text: str, size: int = 500, overlap: int = 80) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max(size - overlap, 1)
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]


class KnowledgeBase:
    def __init__(self):
        self.chunks: list[Chunk] = []
        self._vec = None
        self._matrix = None

    def add_document(self, source: str, text: str, size: int = 120, overlap: int = 30):
        for piece in chunk_text(text, size, overlap):
            self.chunks.append(Chunk(source, piece))
        self._index()

    def _index(self):
        if not self.chunks:
            return
        self._vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._matrix = self._vec.fit_transform([c.text for c in self.chunks])

    def search(self, query: str, k: int = 3) -> list[dict]:
        if self._matrix is None:
            return []
        scores = cosine_similarity(self._vec.transform([query]), self._matrix)[0]
        top = scores.argsort()[::-1][:k]
        return [
            {"source": self.chunks[i].source, "score": round(float(scores[i]), 3),
             "text": self.chunks[i].text}
            for i in top if scores[i] > 0
        ]
