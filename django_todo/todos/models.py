from django.db import models
from django.conf import settings

class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(default='', blank=True)
    completed = models.BooleanField(default=False, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
