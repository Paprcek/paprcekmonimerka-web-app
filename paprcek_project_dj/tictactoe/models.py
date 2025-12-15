from django.db import models

class GameState(models.Model):
    # 'board' (Hrací deska): Ukládá pole jako jeden řetězec.
    board = models.CharField(max_length=9, default='.........')

    # 'is_x_turn': Určuje, kdo je na tahu (True pro X)
    is_x_turn = models.BooleanField(default=True)

    # 'status': Stav hry (Active, X_Wins, O_Wins, Draw)
    status = models.CharField(max_length=10, default='Active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Hra {self.id} - Stav: {self.status}"
