"""Query-time counterpart to management/commands/index_shas.py: embeds the
student's question and finds the nearest ShasPassage rows via pgvector, so
the navigate intent can ground its answer in actually-retrieved Shas
content instead of the model's own unverified recall."""
from pgvector.django import CosineDistance

from ..llm.factory import get_embeddings
from ..models import ShasPassage


def search_shas(query_text, top_k=5):
    """Returns up to top_k ShasPassage rows nearest to query_text, nearest
    first. Each has a `.distance` attribute (cosine distance, lower = closer)."""
    embedding = get_embeddings().embed_query(query_text)
    return list(
        ShasPassage.objects
        .annotate(distance=CosineDistance("embedding", embedding))
        .order_by("distance")[:top_k]
    )
