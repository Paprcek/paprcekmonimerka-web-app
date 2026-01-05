from django.db import models
from django.contrib.auth.models import User

class GameScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    time_spent = models.IntegerField() # Čas v sekundách
    date_achieved = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['time_spent']

class TicTacToeRecord(models.Model):
    time_seconds = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['time_seconds']

    def __str__(self):
        return f"Rekord: {self.time_seconds}s ({self.created_at.strftime('%d.%m.%Y')})"