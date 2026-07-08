# core/models.py
#
# MongoEngine models for storing page-level layout data:
# - Page: page ref + source PDF link + list of bounding boxes
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


class CropBox(EmbeddedDocument):
    """
    Fractions (0-1) of the full-rendered PDF page that contain actual content.
    Used to crop the page image on demand without storing base64 in the DB.
    """
    left = FloatField(required=True, min_value=0, max_value=1)
    top = FloatField(required=True, min_value=0, max_value=1)
    right = FloatField(required=True, min_value=0, max_value=1)
    bottom = FloatField(required=True, min_value=0, max_value=1)


class BBox(EmbeddedDocument):
    """
    A single bounding box on the page.

    Coordinates are fractions (0-1) of the page image; top/left are the
    upper-left corner.
    """

    ref = StringField(required=True)  # display ref, e.g. "Shekalim 2a:1"
    top = FloatField(required=True, min_value=0)
    left = FloatField(required=True, min_value=0)
    width = FloatField(required=True, min_value=0)
    height = FloatField(required=True, min_value=0)

    def clean(self):
        if not self.ref or not self.ref.strip():
            raise ValidationError("BBox.ref must be a non-empty string.")
        if self.width <= 0:
            raise ValidationError("BBox.width must be > 0.")
        if self.height <= 0:
            raise ValidationError("BBox.height must be > 0.")

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
    Stores the page ref, link to the source PDF, an optional crop box, and a
    list of bounding boxes that map refs to geometry.
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

    # Display reference used in our URLs, e.g. "Shekalim 2a"
    ref = StringField(required=True)

    # Sefaria API reference when it differs from ref, e.g. "Jerusalem Talmud Shekalim 2a"
    # Falls back to ref when not set.
    sefaria_ref = StringField(required=False)

    # Link to the PDF that the page came from
    source_pdf = URLField(required=True)

    crop_box = EmbeddedDocumentField(CropBox)

    # Bounding boxes embedded within the page document
    bboxes = ListField(EmbeddedDocumentField(BBox), default=list)

    created_at = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc))

    def clean(self):
        if not self.ref or not self.ref.strip():
            raise ValidationError("Page.ref must be non-empty.")
        self.ref = self.ref.strip()

        seen = set()
        for bbox in self.bboxes or []:
            r = (bbox.ref or "").strip()
            if not r:
                raise ValidationError("Found BBox with empty ref.")
            if r in seen:
                raise ValidationError(f"Duplicate bbox ref within page: '{r}'")
            seen.add(r)

    def effective_sefaria_ref(self) -> str:
        return self.sefaria_ref or self.ref

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "ref": self.ref,
            "sefaria_ref": self.effective_sefaria_ref(),
            "source_pdf": self.source_pdf,
            "crop_box": {
                "left": self.crop_box.left, "top": self.crop_box.top,
                "right": self.crop_box.right, "bottom": self.crop_box.bottom,
            } if self.crop_box else None,
            "bboxes": [b.to_dict() for b in (self.bboxes or [])],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
