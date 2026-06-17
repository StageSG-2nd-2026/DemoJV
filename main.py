from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from entities import Player, Enemy
from managers import ScoreManager, EnemySpawner
import sys

class TacticalFPS(ShowBase):

    def collides_with_wall(self, pos):

        player_radius = 0.5

        for wall in self.walls:

            bounds = wall.getTightBounds()

            if bounds is None:
                continue

            min_point, max_point = bounds

            min_x = min_point.x
            max_x = max_point.x

            min_y = min_point.y
            max_y = max_point.y

            if (min_x-player_radius <= pos.x <= max_x+player_radius and min_y-player_radius <= pos.y <= max_y+player_radius):

                return True

        return False

    def __init__(self):

        self.heading = 0
        self.pitch = 0

        ShowBase.__init__(self)

        # Configuration de la fenêtre
        props = WindowProperties()
        props.setCursorHidden(False)
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

        for key in ["z", "q", "s", "d","space","b"]:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])


    def set_key(self, key, value):
        self.keys[key] = value

    def setup_level(self):


        self.walls = []
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
        toit.setScale(10, 110, 0.2)
        toit.setPos(0, 40, 4)

    # Mur gauche
        left_wall = self.loader.loadModel("models/box")
        left_wall.reparentTo(render)
        left_wall.setScale(0.2, 100, 4)
        left_wall.setPos(0, 40,0)
        self.walls.append(left_wall)

    # Mur droit
        right_wall = self.loader.loadModel("models/box")
        right_wall.reparentTo(render)
        right_wall.setScale(0.2, 110, 4)
        right_wall.setPos(10, 40, 0)
        self.walls.append(right_wall)

    # Mur du droit 2
        r2_wall = self.loader.loadModel("models/box")
        r2_wall.reparentTo(render)
        r2_wall.setScale(50, 0.2, 4)
        r2_wall.setPos(-40, 150, 0)
        self.walls.append(r2_wall)
    # Mur de gaucke 2
        l2_wall = self.loader.loadModel("models/box")
        l2_wall.reparentTo(render)
        l2_wall.setScale(50, 0.2, 4)
        l2_wall.setPos(-50, 140, 0)
        self.walls.append(l2_wall)
    # Mur de gauche 3
        l3_wall = self.loader.loadModel("models/box")
        l3_wall.reparentTo(render)
        l3_wall.setScale(0.2, 50, 4)
        l3_wall.setPos(-50, 140, 0)
        self.walls.append(l3_wall)
    # Mur de droite 3
        r3_wall = self.loader.loadModel("models/box")
        r3_wall.reparentTo(render)
        r3_wall.setScale(0.2, 40, 4)
        r3_wall.setPos(-40, 150, 0)
        self.walls.append(r3_wall)

        enemy = self.loader.loadModel("models/box")
        enemy.reparentTo(render)
        enemy.setScale(1)
        enemy.setPos(5, 80, 1)
        self.enemy_hp = 150

        self.enemy_model = enemy


        #self.finish = finish

    def setup_ui(self):
        from direct.gui.OnscreenText import OnscreenText

        self.crosshair = OnscreenText(
        text="+",
        pos=(0, 0),
        scale=0.3)

    def handle_shoot(self):

        if self.player.weapon.magazine <= 0:
            print("Recharge !")
            return

        self.player.weapon.magazine -= 1

        print("Bang !")
        from panda3d.core import LineSegs

        line = LineSegs()
        line.moveTo(self.camera.getPos())
        forward = self.camera.getQuat().getForward()

        line.drawTo(
            self.camera.getPos() + forward * 100
        )

        beam = render.attachNewNode(line.create())

        # Détection de touche
        if self.enemy_model is None:
            return
        else:

            enemy_pos = self.enemy_model.getPos()

            origin = self.camera.getPos()
            forward = self.camera.getQuat().getForward()

            to_enemy = enemy_pos - origin
            distance = to_enemy.length()

            if distance > 0:
                to_enemy.normalize()

                # Produit scalaire
                dot = forward.dot(to_enemy)

                # 0.99 ≈ très proche du centre du viseur
                if dot > 0.99:

                    self.enemy_hp -= 40

                    print("Touché ! PV restants :", self.enemy_hp)

                    if self.enemy_hp <= 0:

                        print("ENNEMI TUÉ")

                        self.player.score += 100

                        self.enemy_model.removeNode()
                        self.enemy_model = None
        # destruction après 0.05 seconde
        self.taskMgr.doMethodLater(
            0.05,
            lambda task: (beam.removeNode(), task.done)[1],
            "remove_beam"
        )


    def update(self, task):
        #print("Camera:", self.camera.getPos())
        if self.mouseWatcherNode.hasMouse():

            mouse = self.win.getPointer(0)

            x = mouse.getX()
            y = mouse.getY()

            center_x = self.win.getXSize() // 2
            center_y = self.win.getYSize() // 2

            dx = x - center_x
            dy = y - center_y

            sensitivity = 0.15

            self.heading -= dx * sensitivity
            self.pitch -= dy * sensitivity

            self.pitch = max(-85, min(85, self.pitch))

            self.camera.setH(self.heading)
            self.camera.setP(self.pitch)

            self.win.movePointer(
            0,
            center_x,
            center_y
            )


        dt = globalClock.getDt()

        speed = 20

        forward = self.camera.getQuat().getForward()
        right = self.camera.getQuat().getRight()

        move = forward * 0

        # On garde les déplacements au sol
        forward.setZ(0)
        right.setZ(0)

        forward.normalize()
        right.normalize()

        if self.keys.get("z", False):
            move += forward

        if self.keys.get("s", False):
            move -= forward

        if self.keys.get("d", False):
            move += right

        if self.keys.get("q", False):
            move -= right

        # Vol vertical temporaire
        if self.keys.get("space", False):
            self.camera.setZ(self.camera.getZ() + speed * dt)

        if self.keys.get("b", False):
            self.camera.setZ(self.camera.getZ() - speed * dt)

        if move.length() > 0:

            move.normalize()

            new_pos = (
                self.camera.getPos() +
                move * speed * dt
            )

            if move.length() > 0:

                move.normalize()

                current_pos = self.camera.getPos()

                move_x = move * speed * dt
                move_y = move * speed * dt

                # Déplacement horizontal seul
                test_x = current_pos + move_x
                test_x.setY(current_pos.getY())

                if not self.collides_with_wall(test_x):
                    current_pos.setX(test_x.getX())

                # Déplacement vertical seul
                test_y = current_pos + move_y
                test_y.setX(current_pos.getX())

                if not self.collides_with_wall(test_y):
                    current_pos.setY(test_y.getY())

                self.camera.setPos(current_pos)

        if self.camera.getY() > 95:
            self.end_game()


        return task.cont

    def end_game(self):
        total_time = self.score_manager.get_elapsed_time()
        final_score = self.score_manager.calculate_final_score(self.player, total_time)
        rank = self.score_manager.get_rank(final_score)
        #print(f"Game Over! Score: {final_score}, Rank: {rank}")
        #sys.exit()

if __name__ == "__main__":
    game = TacticalFPS()
    game.run()
