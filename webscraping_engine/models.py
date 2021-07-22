from django.db import models
from django.db.models.fields import CharField


class ValidUniversities(models.Model):
    name = CharField(max_length=120, null=False, blank=False, unique=True)
    url = CharField(max_length=200, null=False, unique=True)

    def __str__(self):
        return f"{self.name}"
