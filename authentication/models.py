import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class Player(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.first_name + " " + self.last_name
