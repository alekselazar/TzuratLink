"""
One-time (resumable) batch job: walks every daf of Talmud Bavli, fetches
dafyomi.co.il's "Insights into the Daily Daf" summary for it (short,
topic-labeled points — far more suited to embedding/retrieval than raw
Gemara translation), embeds each point, and stores it in ShasPassage for
the navigate intent's retrieval step (see ai_chavruta/retrieval).

Only tractates dafyomi.co.il covers (ai_chavruta.context.dafyomi_client.
TRACTATE_SLUGS) are walked — Kinim/Middot aren't part of the Daf Yomi cycle
and have no coverage there (or real Gemara to summarize).

A tractate's actual daf range isn't hardcoded — it's discovered live via
Sefaria (reliable for "does this daf exist at all", used only as an oracle
here, not as the text source): probe sequentially from 2a, requiring a run
of consecutive misses (not just one) before concluding we've passed the
end, since dafyomi.co.il's own insights coverage has real gaps on valid
dapim and shouldn't be confused with "tractate is over".
"""
import logging

from django.core.management.base import BaseCommand

from core.sefaria import get_text_v3
from ai_chavruta.context.dafyomi_client import TRACTATE_SLUGS, fetch_insights_points
from ai_chavruta.llm.factory import get_embeddings
from ai_chavruta.models import ShasPassage

logger = logging.getLogger(__name__)

MAX_DAF = 200  # above Bava Batra's real range (176) with margin
CONSECUTIVE_MISS_LIMIT = 4  # 2 full dafs of no Sefaria text before we call it the end
EMBED_BATCH_SIZE = 20


def _daf_exists(ref):
    data = get_text_v3(ref)
    return bool(data and data.get("ref") == ref)


def _points_to_passages(daf_ref, tractate, daf, amud):
    passages = []
    for point in fetch_insights_points(daf_ref):
        subject = (point.get("subject") or "").strip()
        body = " ".join(e.get("text", "") for e in point.get("entries", []) if e.get("text"))
        text = f"{subject}. {body}".strip(". ").strip()
        if text:
            passages.append((subject, text))
    return [
        (daf_ref, tractate, daf, amud, subject, text)
        for subject, text in passages
    ]


class Command(BaseCommand):
    help = "Build the Shas vector index from dafyomi.co.il's daily-daf insight summaries."

    def handle(self, *args, **options):
        already_indexed_refs = set(ShasPassage.objects.values_list("ref", flat=True).distinct())
        embeddings = get_embeddings()

        total_indexed = 0
        for tractate in TRACTATE_SLUGS:
            self.stdout.write(f"[{tractate}] scanning...")
            buffer = []  # list of (ref, tractate, daf, amud, subject, text)
            consecutive_misses = 0
            daf = 2
            side_index = 0  # 0 = 'a', 1 = 'b'

            while daf <= MAX_DAF and consecutive_misses < CONSECUTIVE_MISS_LIMIT:
                amud = "a" if side_index == 0 else "b"
                ref = f"{tractate} {daf}{amud}"

                if not _daf_exists(ref):
                    consecutive_misses += 1
                else:
                    consecutive_misses = 0
                    if ref not in already_indexed_refs:
                        buffer.extend(_points_to_passages(ref, tractate, daf, amud))
                        if len(buffer) >= EMBED_BATCH_SIZE:
                            total_indexed += self._flush(buffer, embeddings)
                            buffer = []

                if side_index == 0:
                    side_index = 1
                else:
                    side_index = 0
                    daf += 1

            if buffer:
                total_indexed += self._flush(buffer, embeddings)

        self.stdout.write(self.style.SUCCESS(f"Done. Indexed {total_indexed} new passages."))

    def _flush(self, buffer, embeddings):
        texts = [text for *_, text in buffer]
        try:
            vectors = embeddings.embed_documents(texts)
        except Exception:
            logger.exception("Embedding batch failed for refs %s", [r for r, *_ in buffer])
            return 0

        ShasPassage.objects.bulk_create([
            ShasPassage(
                ref=ref, tractate=tractate, daf=daf, amud=amud,
                subject=subject, text=text, embedding=vector,
            )
            for (ref, tractate, daf, amud, subject, text), vector in zip(buffer, vectors)
        ])

        self.stdout.write(f"  indexed {len(buffer)} passages ({buffer[0][0]} .. {buffer[-1][0]})")
        return len(buffer)
