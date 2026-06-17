from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from entities import Player, Enemy
from managers import ScoreManager, EnemySpawner
import sys


class TacticalFPS(ShowBase):

    def show_message(self, message, duration=1.0):

        self.message_text.setText(message)

        def clear(task):
            self.message_text.setText("")
            return task.done

        self.taskMgr.doMethodLater(
            duration,
            clear,
            f"clear_message_{id(self)}"
        )

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
        self.accept("space", self.jump)
        self.mouse_locked = True
        self.accept("o", self.toggle_mouse)

        self.heading = 0
        self.pitch = 0
        self.vertical_velocity = 0
        self.gravity = -25
        self.jump_force = 10
        self.on_ground = True
        self.player_hp =100
        self.enemy_shot_timer = 0

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

        for key in ["z", "q", "s", "d",]:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])


    def set_key(self, key, value):
        self.keys[key] = value

    def setup_level(self):

        from panda3d.core import AmbientLight
        from panda3d.core import DirectionalLight

        musique = loader.loadMusic("Ambiance.mp3")
        musique.setLoop(True)
        musique.play()

        ambient = AmbientLight("ambient")
        ambient.setColor((0.4, 0.4, 0.4, 1))

        ambient_np = render.attachNewNode(ambient)
        render.setLight(ambient_np)

        sun = DirectionalLight("sun")
        sun.setColor((0.8, 0.8, 0.8, 1))

        sun_np = render.attachNewNode(sun)
        sun_np.setHpr(45, -45, 0)

        render.setLight(sun_np)


        self.walls = []
        self.disableMouse()

        self.camera.setPos(5, 40, 1.8)
        self.camera.lookAt(0,0,0)

    # Sol
        floor = self.loader.loadModel("models/box")
        floor.reparentTo(render)
        floor.setScale(10, 110, 0.2)
        floor.setPos(0, 40, 0)
        floor2 = self.loader.loadModel("models/box")
        floor2.reparentTo(render)
        floor2.setScale(50, 10, 0.2)
        floor2.setPos(-50, 140, 0)
        floor3 = self.loader.loadModel("models/box")
        floor3.reparentTo(render)
        floor3.setScale(10, 40, 0.2)
        floor3.setPos(-50, 150, 0)


    # Toit
    #    toit = self.loader.loadModel("models/box")
     #   toit.reparentTo(render)
      #  toit.setScale(1000, 1000, 0.2)
       # toit.setPos(-500, -500, 4)

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

        tex = self.loader.loadTexture("texture_mur.png")

        left_wall.setTexture(tex, 1)
        right_wall.setTexture(tex, 1)
        r2_wall.setTexture(tex, 1)
        l2_wall.setTexture(tex, 1)
        l3_wall.setTexture(tex, 1)
        r3_wall.setTexture(tex, 1)

        texsol = self.loader.loadTexture("texture_sol.png")

        floor.setTexture(texsol, 1)
        floor2.setTexture(texsol, 1)
        floor3.setTexture(texsol, 1)


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
            scale=0.3
        )

        self.message_text = OnscreenText(
            text="",
            pos=(-0.7, 0.9),      # haut droite
            align=1,             # texte aligné à droite
            scale=0.05,
            mayChange=True
        )

        self.ammo_text = OnscreenText(
            text="30/30",
            pos=(1.3, -0.9),
            align=1,
            scale=0.2,
            mayChange=True
        )

    def handle_shoot(self):

        bang = loader.loadSfx("bang.mp3")

        if self.player.weapon.magazine <= 0:
            self.show_message("Recharge !", 1)
            return

        self.player.weapon.magazine -= 1

        self.show_message("Bang !", 0.3)
        bang.play()

        from panda3d.core import LineSegs

        line = LineSegs()
        line.moveTo(self.camera.getPos())
        forward = self.camera.getQuat().getForward()

        line.drawTo(
            self.camera.getPos() + forward * 100
        )

        beam = render.attachNewNode(line.create())

        beam_name = f"beam_{id(beam)}"

        self.taskMgr.doMethodLater(
            0.05,
            lambda task, b=beam: (b.removeNode(), task.done)[1],
            beam_name
        )

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

                    self.show_message(
                        f"Touché ! ({self.enemy_hp} PV)",
                        0.8
                    )

                    if self.enemy_hp <= 0:

                        self.show_message("ENNEMI TUÉ +100", 1.5)

                        self.player.score += 100

                        self.enemy_model.removeNode()
                        self.enemy_model = None



    def update(self, task):

        self.ammo_text.setText(
            f"{self.player.weapon.magazine}/30"
        )
        #print("Camera:", self.camera.getPos())
        if self.mouse_locked and self.mouseWatcherNode.hasMouse():

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

            if not self.collides_with_wall(new_pos):
                self.camera.setPos(new_pos)
        self.vertical_velocity += self.gravity * dt

        new_z = self.camera.getZ() + self.vertical_velocity * dt

        ground_height = 1.8

        if new_z <= ground_height:
            new_z = ground_height
            self.vertical_velocity = 0
            self.on_ground = True

        self.camera.setZ(new_z)
#
        # IA ennemi simple
        if self.enemy_model:

            enemy_pos = self.enemy_model.getPos()
            player_pos = self.camera.getPos()

            direction = player_pos - enemy_pos
            direction.setZ(0)

            if direction.length() > 0:

                direction.normalize()

                self.enemy_model.setPos(
                    enemy_pos + direction * 2 * dt
                )

                self.enemy_model.lookAt(self.camera)
        if self.enemy_model:

            self.enemy_shot_timer -= dt

            distance = (
            self.enemy_model.getPos()
            - self.camera.getPos()
            ).length()

            if distance < 20:

                if self.enemy_shot_timer <= 0:
                    from panda3d.core import LineSegs

                    line = LineSegs()
                    line.setColor(1, 0, 0)
                    line.setThickness(2)
                    line.moveTo(self.enemy_model.getPos())
                    line.drawTo(self.camera.getPos())

                    beam = render.attachNewNode(line.create())

                    self.taskMgr.doMethodLater(
                         0.05,
                        lambda task, b=beam: (b.removeNode(), task.done)[1],
                        f"enemy_beam_{id(beam)}"
                    )

                    self.player_hp -= 10

                    self.show_message(
                        f"-10 HP ({self.player_hp})",
                        0.5
                    )

                    self.enemy_shot_timer = 1



#
        if self.camera.getY() > 95:
            self.end_game()


        return task.cont

    def end_game(self):
        total_time = self.score_manager.get_elapsed_time()
        final_score = self.score_manager.calculate_final_score(self.player, total_time)
        rank = self.score_manager.get_rank(final_score)
        #print(f"Game Over! Score: {final_score}, Rank: {rank}")
        #sys.exit()
    def toggle_mouse(self):
        props = WindowProperties()
        self.mouse_locked = not self.mouse_locked

        if self.mouse_locked:
            props.setCursorHidden(True)
            props.setMouseMode(WindowProperties.M_relative)

            center_x = self.win.getXSize() // 2
            center_y = self.win.getYSize() // 2
            self.win.movePointer(0, center_x, center_y)

        else:
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)

        self.win.requestProperties(props)
    def jump(self):
        if self.on_ground:
            self.vertical_velocity = self.jump_force
            self.on_ground = False

if __name__ == "__main__":
    game = TacticalFPS()
    game.run()
