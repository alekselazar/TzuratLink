from django.db import models
from pgvector.django import HnswIndex, VectorField

# Embedding dimensions for OpenAI's text-embedding-3-small.
EMBEDDING_DIM = 1536


class ShasPassage(models.Model):
    """One dafyomi.co.il "insight" topic (a short summary of one discussion
    point on a daf), embedded for retrieval-grounded daf lookup (see
    ai_chavruta.retrieval). Several rows can share the same `ref` — a daf
    with N distinct discussion points yields N passages, not one giant blob,
    so retrieval can match the specific topic rather than the whole amud."""

    ref = models.CharField(max_length=64, db_index=True)
    tractate = models.CharField(max_length=32)
    daf = models.PositiveSmallIntegerField()
    amud = models.CharField(max_length=1, choices=[("a", "a"), ("b", "b")])
    subject = models.CharField(max_length=256, blank=True)
    text = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIM)

    class Meta:
        indexes = [
            HnswIndex(
                name="shaspassage_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.ref} ({self.subject})" if self.subject else self.ref
