from django.db import models


class TimestampedModel(models.Model):
    """Abstract base Model which provides auto-updating created_at and updated_at fields."""

    created_at = models.DateTimeField(
        'Date de création',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Date de modification',
        auto_now=True
    )

    class Meta:
        abstract = True
        ordering = ("-created_at",)
