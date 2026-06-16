from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from entities import Player, Enemy
from managers import ScoreManager, EnemySpawner
import sys

class TacticalFPS(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Configuration de la fenêtre
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)

        # Initialisation des systèmes
        self.player = Player()
        self.score_manager = ScoreManager()
        self.spawner = EnemySpawner()
        
        # Environnement (Couloir)
        self.setup_level()
        
        # HUD
        self.setup_ui()

        # Events
        self.accept("mouse1", self.handle_shoot)
        self.accept("r", self.player.weapon.reload)
        self.accept("escape", sys.exit)

        # Loop
        self.taskMgr.add(self.update, "update_task")

    def setup_level(self):
        # Chargement des modèles (murs, sol, caisses)
        # self.loader.loadModel("models/corridor")
        pass

    def setup_ui(self):
        # Utilisation de OnscreenText pour le HUD
        pass

    def handle_shoot(self):
        is_moving = self.player.velocity.length() > 0.1
        shot_fired, spread = self.player.weapon.shoot(is_moving, 1.0)
        
        if shot_fired:
            # Logique de détection de collision (Headshot vs Body)
            # Si touché : self.player.add_score(enemy.take_damage(40, is_headshot))
            pass

    def update(self, task):
        dt = globalClock.getDt()
        # Mise à jour des mouvements, timer, UI
        return task.cont

    def end_game(self):
        total_time = self.score_manager.get_elapsed_time()
        final_score = self.score_manager.calculate_final_score(self.player, total_time)
        rank = self.score_manager.get_rank(final_score)
        print(f"Game Over! Score: {final_score}, Rank: {rank}")
        sys.exit()

if __name__ == "__main__":
    game = TacticalFPS()
    game.run()