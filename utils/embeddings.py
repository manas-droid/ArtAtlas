"""Embedding utilities shared across ingestion and retrieval."""

from __future__ import annotations

import torch
from sentence_transformers import SentenceTransformer

from utils.config import EMBEDDING_MODEL_NAME

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME).to(_device)
    return _model


def encode_text(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(text).tolist()


def encode_batch(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return model.encode(texts).tolist()
