from panda3d.core import Vec3

class Weapon:
    def __init__(self):
        self.magazine = 30
        self.damage = 40

    def shoot(self, moving, accuracy):
        if self.magazine <= 0:
            return False, 0

        self.magazine -= 1
        spread = 0.2 if moving else 0
        return True, spread

    def reload(self):
        self.magazine = 30


class Player:
    def __init__(self):
        self.hp = 250
        self.score = 0
        self.velocity = Vec3(0, 0, 0)
        self.weapon = Weapon()

    def add_score(self, pts):
        self.score += pts


class Enemy:
    def __init__(self):
        self.hp = 150

    def take_damage(self, dmg, headshot=False):
        if headshot:
            self.hp = 0
            return 250

        self.hp -= dmg

        if self.hp <= 0:
            return 10

        return 0
