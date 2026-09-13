"""Content-based product recommendation engine.

Uses TF-IDF-style weighting over product metadata and cosine similarity. The
implementation is intentionally dependency-free so it can run locally with
only Python's standard library.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class ProductRecommender:
    def __init__(self, catalog_path: str | Path):
        self.catalog_path = Path(catalog_path)
        self.products: list[dict[str, Any]] = []
        self.vocabulary: dict[str, float] = {}
        self.product_vectors: dict[str, dict[str, float]] = {}
        self.load_catalog()

    def load_catalog(self) -> None:
        with self.catalog_path.open("r", encoding="utf-8") as file:
            self.products = json.load(file)
        self._fit()

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return TOKEN_PATTERN.findall(text.lower())

    @staticmethod
    def _product_text(product: dict[str, Any]) -> str:
        fields = [
            product["name"],
            product["category"],
            product["brand"],
            product["description"],
            " ".join(product.get("features", [])),
            " ".join(product.get("colors", [])),
        ]
        return " ".join(fields)

    def _fit(self) -> None:
        documents = [Counter(self._tokens(self._product_text(product))) for product in self.products]
        document_frequency: Counter[str] = Counter()
        for document in documents:
            document_frequency.update(document.keys())

        document_count = max(len(documents), 1)
        self.vocabulary = {
            token: math.log((1 + document_count) / (1 + frequency)) + 1
            for token, frequency in document_frequency.items()
        }
        self.product_vectors = {
            product["id"]: self._vectorize(document)
            for product, document in zip(self.products, documents)
        }

    def _vectorize(self, counts: Counter[str]) -> dict[str, float]:
        total_terms = max(sum(counts.values()), 1)
        vector = {
            token: (count / total_terms) * self.vocabulary.get(token, 1.0)
            for token, count in counts.items()
        }
        magnitude = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        return {token: value / magnitude for token, value in vector.items()}

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(token, 0.0) for token, value in left.items())

    def _query_vector(self, query: str) -> dict[str, float]:
        return self._vectorize(Counter(self._tokens(query)))

    def recommend(
        self,
        query: str = "",
        product_id: str | None = None,
        category: str | None = None,
        limit: int = 6,
    ) -> list[dict[str, Any]]:
        source_product = next(
            (product for product in self.products if product["id"] == product_id), None
        )
        if source_product:
            query = self._product_text(source_product)

        query_vector = self._query_vector(query) if query.strip() else {}
        scored: list[tuple[float, dict[str, Any]]] = []
        for product in self.products:
            if product_id and product["id"] == product_id:
                continue
            if category and category != "All" and product["category"] != category:
                continue
            score = self._cosine(query_vector, self.product_vectors[product["id"]])
            if not query_vector:
                score = product.get("rating", 0) / 5
            scored.append((score, product))

        scored.sort(key=lambda item: (item[0], item[1].get("rating", 0)), reverse=True)
        results = []
        for score, product in scored[: max(1, min(limit, 24))]:
            result = dict(product)
            result["match_score"] = round(min(score * 100, 99.9), 1)
            results.append(result)
        return results

    def categories(self) -> list[str]:
        return sorted({product["category"] for product in self.products})

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        return next((product for product in self.products if product["id"] == product_id), None)
