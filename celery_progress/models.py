import uuid
from django.db import models
from django.conf import settings

class ProgressPersistent(models.Model):
    task_id = models.UUIDField(default=uuid.uuid4)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    

