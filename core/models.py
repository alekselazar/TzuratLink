# core/models.py
#
# MongoEngine models for storing page-level layout data:
# - Page: page ref + source PDF link + base64 payload + list of bounding boxes
# - BBox: embedded document containing ref + top/left/width/height
#
# Notes:
# - This file is for MongoEngine (NOT Django ORM).
# - Make sure MongoEngine is connected during Django startup (e.g., in AppConfig.ready()).

import datetime
from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    ListField,
    EmbeddedDocumentField,
    FloatField,
    URLField,
    DateTimeField,
    ValidationError,
)


class BBox(EmbeddedDocument):
    """
    A single bounding box on the page.

    Coordinates are typically in percents in the page image coordinate system.
    top/left represent the upper-left corner.
    """

    ref = StringField(required=True)  # e.g. "Berakhot 2a:1" or "Rashi Berakhot 2a"
    top = FloatField(required=True, min_value=0)
    left = FloatField(required=True, min_value=0)
    width = FloatField(required=True, min_value=0)
    height = FloatField(required=True, min_value=0)

    def clean(self):
        # Enforce non-empty ref and positive geometry (strictly > 0 for size).
        if not self.ref or not self.ref.strip():
            raise ValidationError("BBox.ref must be a non-empty string.")
        if self.width <= 0:
            raise ValidationError("BBox.width must be > 0.")
        if self.height <= 0:
            raise ValidationError("BBox.height must be > 0.")

    @property
    def right(self) -> float:
        return float(self.left) + float(self.width)

    @property
    def bottom(self) -> float:
        return float(self.top) + float(self.height)

    def to_dict(self) -> dict:
        return {
            "ref": self.ref,
            "top": float(self.top),
            "left": float(self.left),
            "width": float(self.width),
            "height": float(self.height),
        }


class Page(Document):
    """
    Page-level layout representation.
    Stores the page ref, link to the source PDF, a base64 payload (e.g., page image),
    and a list of bounding boxes that map refs to geometry.
    """

    meta = {
        "collection": "pages",
        "indexes": [
            {"fields": ["ref"], "unique": True},
            {"fields": ["source_pdf"]},
            {"fields": ["bboxes.ref"]},
            {"fields": ["created_at"]},
        ],
    }

    # Page identifier (your logical reference, e.g. "Berakhot 2a")
    ref = StringField(required=True)

    # Link to the PDF that the page came from
    source_pdf = URLField(required=True)

    # Base64-encoded payload (commonly PNG/JPEG bytes encoded as base64)
    base64_data = StringField(required=True)

    # Bounding boxes embedded within the page document
    bboxes = ListField(EmbeddedDocumentField(BBox), default=list)

    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    def clean(self):
        # Normalize/validate strings
        if not self.ref or not self.ref.strip():
            raise ValidationError("Page.ref must be a non-empty string.")
        self.ref = self.ref.strip()

        if not self.base64_data or not self.base64_data.strip():
            raise ValidationError("Page.base64_data must be a non-empty base64 string.")

        # Optional: basic sanity check that bboxes are unique by ref within a page.
        # If you want to allow multiple boxes per ref, remove this block.
        seen = set()
        for bbox in self.bboxes or []:
            r = (bbox.ref or "").strip()
            if not r:
                raise ValidationError("Found BBox with empty ref.")
            if r in seen:
                raise ValidationError(f"Duplicate bbox ref within page: '{r}'")
            seen.add(r)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "ref": self.ref,
            "source_pdf": self.source_pdf,
            "base64_data": self.base64_data,
            "bboxes": [b.to_dict() for b in (self.bboxes or [])],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_bbox_by_ref(self, bbox_ref: str) -> BBox | None:
        target = (bbox_ref or "").strip()
        if not target:
            return None
        for b in self.bboxes or []:
            if (b.ref or "").strip() == target:
                return b
        return None
