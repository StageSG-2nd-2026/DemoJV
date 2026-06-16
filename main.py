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
        self.keys = {}

        for key in ["z", "q", "s", "d","space","b","m","l"]:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])


    def set_key(self, key, value):
        self.keys[key] = value

    def setup_level(self):

        self.disableMouse()

        self.camera.setPos(5, 40, 1.8)
        self.camera.lookAt(0,0,0)

    # Sol
        floor = self.loader.loadModel("models/environment")
        floor.reparentTo(render)
        floor.setScale(10, 100, 0.2)
        floor.setPos(0, 40, 0)

    # Toit
        toit = self.loader.loadModel("models/box")
        toit.reparentTo(render)
        toit.setScale(10, 100, 0.2)
        toit.setPos(0, 40, 4)

    # Mur gauche
        left_wall = self.loader.loadModel("models/box")
        left_wall.reparentTo(render)
        left_wall.setScale(0.2, 100, 4)
        left_wall.setPos(0, 40,0)

    # Mur droit
        right_wall = self.loader.loadModel("models/box")
        right_wall.reparentTo(render)
        right_wall.setScale(0.2, 100, 4)
        right_wall.setPos(10, 40, 0)

        #self.finish = finish

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
        print("Camera:", self.camera.getPos())

        dt = globalClock.getDt()

        speed = 50

        move_x = 0
        move_y = 0
        move_z = 0
        orientationx = 0

        if self.keys.get("z", False):
            move_y += speed * dt

        if self.keys.get("s", False):
            move_y -= speed * dt

        if self.keys.get("q", False):
            move_x -= speed * dt

        if self.keys.get("d", False):
            move_x += speed * dt

        if self.keys.get("space", False):
            move_z+= speed * dt

        if self.keys.get("b", False):
            move_z-= speed * dt

        if self.keys.get("m",False):
            orientationx += dt*90

        if self.keys.get("l",False):
            orientationx -= dt*90

        self.camera.setX(self.camera.getX() + move_x)
        self.camera.setY(self.camera.getY() + move_y)
        self.camera.setZ(self.camera.getZ() + move_z)

        if self.camera.getY() > 95:
            self.end_game()

        self.camera.lookAt(
            self.camera.getX()+orientationx,
            self.camera.getY() + 10,
            self.camera.getZ()
        )

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
