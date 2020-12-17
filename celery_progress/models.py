import uuid
from django.db import models
from django.conf import settings

class STATES(models.TextChoices):
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    PENDING = "PENDING"

class ProgressPersistent(models.Model):
    task_id = models.UUIDField(default=uuid.uuid4)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    state =  models.CharField(max_length=15, choices=STATES.choices, default=STATES.PENDING)

    

