"""Simple retrieval chatbot using TF-IDF and your sentiment classifier.

This is intentionally small and offline-friendly. For better results replace the
retrieval+VADER approach with embeddings (sentence-transformers) + semantic search.
"""
from typing import List, Tuple
import numpy as np


def build_index(texts: List[str]):
    """Build a TF-IDF vectorizer and matrix for the provided texts.

    Returns (vectorizer, matrix)
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    vec = TfidfVectorizer(stop_words="english", max_features=5000)
    mat = vec.fit_transform(texts)
    return vec, mat


class SimpleChatbot:
    def __init__(self, texts: List[str]):
        self.texts = texts
        self.vec, self.mat = build_index(texts)
        from .sentiment import classify
        self._classify = classify

    def respond(self, query: str, top_k: int = 3) -> List[Tuple[str, float, dict]]:
        """Return top_k matches as list of (text, score, sentiment).

        Score is cosine similarity in [0,1]. If no positive matches, returns empty list.
        """
        qv = self.vec.transform([query])
        from sklearn.metrics.pairwise import cosine_similarity

        sims = cosine_similarity(qv, self.mat).ravel()
        idx = np.argsort(-sims)[:top_k]
        results: List[Tuple[str, float, dict]] = []
        for i in idx:
            if sims[i] <= 0:
                continue
            text = self.texts[i]
            sentiment = self._classify(text)
            results.append((text, float(sims[i]), sentiment))
        return results
