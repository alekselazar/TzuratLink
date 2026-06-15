import datetime
from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    ListField,
    IntField,
    EmbeddedDocumentField,
    DateTimeField,
    ValidationError,
)


class SegmentRef(EmbeddedDocument):
    """Maps a range of words in a Line to a Sefaria segment reference."""
    sefaria_ref = StringField(required=True)
    start = IntField(required=True, min_value=0)  # inclusive index into Line.words
    end = IntField(required=True, min_value=0)    # exclusive index into Line.words

    def clean(self):
        if not self.sefaria_ref or not self.sefaria_ref.strip():
            raise ValidationError("SegmentRef.sefaria_ref must be non-empty.")
        if self.end <= self.start:
            raise ValidationError("SegmentRef.end must be > start.")

    def to_dict(self) -> dict:
        return {
            "sefaria_ref": self.sefaria_ref,
            "start": self.start,
            "end": self.end,
        }


class Line(EmbeddedDocument):
    """
    A single line of text on the page.

    words and tags are parallel arrays of equal length.
    tags[i] is the HTML tag name to wrap words[i] with (e.g. 'big'), or '' for none.
    segments map contiguous word ranges to Sefaria segment refs for onClick linking.
    """
    class_names = ListField(StringField(), default=list)
    words = ListField(StringField(), default=list)
    tags = ListField(StringField(), default=list)
    segments = ListField(EmbeddedDocumentField(SegmentRef), default=list)

    def clean(self):
        if len(self.words) != len(self.tags):
            raise ValidationError("Line.words and Line.tags must have the same length.")
        for seg in self.segments or []:
            if seg.end > len(self.words):
                raise ValidationError(
                    f"SegmentRef end={seg.end} exceeds line length {len(self.words)}."
                )

    def to_dict(self) -> dict:
        return {
            "class_names": list(self.class_names or []),
            "words": list(self.words),
            "tags": list(self.tags),
            "segments": [s.to_dict() for s in (self.segments or [])],
        }


class Block(EmbeddedDocument):
    class_names = ListField(StringField(), default=list)
    lines = ListField(EmbeddedDocumentField(Line), default=list)

    def to_dict(self) -> dict:
        return {
            "class_names": list(self.class_names or []),
            "lines": [line.to_dict() for line in (self.lines or [])],
        }


class Page(Document):
    meta = {
        "collection": "pages",
        "indexes": [
            {"fields": ["ref"], "unique": True},
            {"fields": ["created_at"]},
        ],
    }

    ref = StringField(required=True)
    sefaria_ref = StringField(required=False)
    blocks = ListField(EmbeddedDocumentField(Block), default=list)

    created_at = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc))

    def clean(self):
        if not self.ref or not self.ref.strip():
            raise ValidationError("Page.ref must be non-empty.")
        self.ref = self.ref.strip()

    def effective_sefaria_ref(self) -> str:
        return self.sefaria_ref or self.ref

    def save(self, *args, **kwargs):
        self.updated_at = lambda: datetime.datetime.now(datetime.timezone.utc)()
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "ref": self.ref,
            "sefaria_ref": self.effective_sefaria_ref(),
            "blocks": [block.to_dict() for block in (self.blocks or [])],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
