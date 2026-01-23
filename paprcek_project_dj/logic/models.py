from django.db import models

class LogicScore(models.Model):
    player_name = models.CharField(max_length=100, default="Anonym")
    time = models.FloatField()
    difficulty = models.CharField(max_length=10, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['time']

    def __str__(self):
        return f"{self.player_name}: {self.time}s"