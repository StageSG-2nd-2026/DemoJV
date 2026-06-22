import time

class ScoreManager:
    def __init__(self):
        self.start_time = time.time()

    def get_elapsed_time(self):
        return time.time() - self.start_time

    def calculate_final_score(self, player, elapsed):
        score = player.score

        if player.hp == 250:
            score += 1000
        elif player.hp >= 200:
            score += 500
        elif player.hp >= 150:
            score += 250
        elif player.hp >= 100:
            score += 100
        elif player.hp >= 50:
            score += 50

        if elapsed < 30:
            score += 1500
        elif elapsed < 60:
            score += 1000
        elif elapsed < 90:
            score += 500
        elif elapsed < 120:
            score += 250

        return score

    def get_rank(self, score):
        if score >= 5000:
            return "S"
        elif score >= 3000:
            return "A"
        elif score >= 2000:
            return "B"
        elif score >= 1000:
            return "C"
        return "D"


class EnemySpawner:
    def __init__(self):
        self.enemies = []

    def spawn_enemy(self):
        pass
