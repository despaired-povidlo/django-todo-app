from django.db import models
from django.db.models import CharField, TextField
from django.contrib.auth.models import User


# Todo: add image field with option to add multiple files
class Todo(models.Model):
    title = CharField(max_length=32)
    memo = TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
