from aplications.authentication.models import CustomUser
from django.db import models
from django.utils import timezone


# Create your models here.
class Follow(models.Model):
    follower = models.ForeignKey(
        CustomUser, related_name="following_relations", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        CustomUser, related_name="follower_relations", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("follower", "followed")  # Evita relaciones duplicadas
        verbose_name = "Follow"
        verbose_name_plural = "Follows"

    def __str__(self):
        return f"{self.follower} follows {self.followed}"
