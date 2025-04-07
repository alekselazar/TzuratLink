from django.db import models

class Page(models.Model):
    file = models.TextField()
    foreign_url = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

class BoundingContainer(models.Model):
    sefaria_ref = models.CharField(max_length=100)
    top = models.CharField(max_length=50)
    left = models.CharField(max_length=50)
    height = models.CharField(max_length=50)
    width = models.CharField(max_length=50)
    page_ref = models.ForeignKey(Page, on_delete=models.CASCADE)

class PageAnchor(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    sefaria_ref = models.CharField(max_length=100)

class TranslatedSentance(models.Model):
    sentance = models.TextField()
    sefaria_ref = models.CharField(max_length=100)
    is_translated = models.BooleanField(default=False)

class Translation(models.Model):
    CHOICES = [
        ('en', 'English'),
        ('he', 'Hebrew'),
        ('ru', 'Russian'),
        ('ua', 'Ukrainian')
    ]
    translation = models.TextField()
    sentance = models.ForeignKey(TranslatedSentance, on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=CHOICES)
