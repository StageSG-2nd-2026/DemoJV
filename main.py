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
        self.mouse_sensitivity = 0.15
        self.accept("p", self.increase_sensitivity)
        self.accept("m", self.decrease_sensitivity)
        self.air_speed_bonus = 0
        self.shooting = False
        self.fire_rate = 0.08      # 80 ms entre les balles (~750 RPM)
        self.fire_timer = 0
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
        self.crouching = False
        self.accept("c", self.start_crouch)
        self.accept("c-up", self.stop_crouch)
        self.kill_sounds = [
            self.loader.loadSfx("killsound1.mp3"),
            self.loader.loadSfx("killsound2.mp3"),
            self.loader.loadSfx("killsound3.mp3"),
            self.loader.loadSfx("killsound4.mp3"),
            self.loader.loadSfx("killsound5.mp3")
        ]
        for sound in self.kill_sounds:
            sound.setVolume(10.0)


        self.kill_index = 0


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
        self.accept("mouse1", self.start_shooting)
        self.accept("mouse1-up", self.stop_shooting)
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

        self.camera.setPos(5, 21, 1.8)
        self.camera.lookAt(5,0,1.8)

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
        floor3.setScale(10, 50, 0.2)
        floor3.setPos(-50, 150, 0)
        floor4 = self.loader.loadModel("models/box")
        floor4.reparentTo(render)
        floor4.setScale(30, 20, 0.2)
        floor4.setPos(-10, 20, 0)
        floor5 = self.loader.loadModel("models/box")
        floor5.reparentTo(render)
        floor5.setScale(90,10,0.2)
        floor5.setPos(-40,190,0)
        floor6 = self.loader.loadModel("models/box")
        floor6.reparentTo(render)
        floor6.setScale(10,40,0.2)
        floor6.setPos(-10,150,0)
        interieur = self.loader.loadModel("models/box")
        interieur.reparentTo(render)
        interieur.setScale(30, 40, 0.2)
        interieur.setPos(-40, 150, 0)


    # Toit
        toit = self.loader.loadModel("models/box")
        toit.reparentTo(render)
        toit.setScale(10, 110, 0.2)
        toit.setPos(0, 40, 4)
        toit2 = self.loader.loadModel("models/box")
        toit2.reparentTo(render)
        toit2.setScale(50, 10, 0.2)
        toit2.setPos(-50, 140, 4)
        toit3 = self.loader.loadModel("models/box")
        toit3.reparentTo(render)
        toit3.setScale(10, 50, 0.2)
        toit3.setPos(-50, 150, 4)
        toit4 = self.loader.loadModel("models/box")
        toit4.reparentTo(render)
        toit4.setScale(30, 20, 0.2)
        toit4.setPos(-10, 20, 8)
        toit5 = self.loader.loadModel("models/box")
        toit5.reparentTo(render)
        toit5.setScale(90,10,0.2)
        toit5.setPos(-40,190,4)
        toit6 = self.loader.loadModel("models/box")
        toit6.reparentTo(render)
        toit6.setScale(10,40,0.2)
        toit6.setPos(-10,150,4)
        interieurt = self.loader.loadModel("models/box")
        interieurt.reparentTo(render)
        interieurt.setScale(30, 40, 0.2)
        interieurt.setPos(-40, 150, 4)

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
        l3_wall.setScale(0.2, 60, 4)
        l3_wall.setPos(-50, 140, 0)
        self.walls.append(l3_wall)
    # Mur de droite 3
        r3_wall = self.loader.loadModel("models/box")
        r3_wall.reparentTo(render)
        r3_wall.setScale(0.2, 40, 4)
        r3_wall.setPos(-40, 150, 0)
        self.walls.append(r3_wall)
    # Mur de gauche debut
        r4_wall = self.loader.loadModel("models/box")
        r4_wall.reparentTo(render)
        r4_wall.setScale(0.2,20,8)
        r4_wall.setPos(-10,20,0)
        self.walls.append(r4_wall)
    # Mur de droite debut
        l4_wall = self.loader.loadModel("models/box")
        l4_wall.reparentTo(render)
        l4_wall.setScale(0.2,20,8)
        l4_wall.setPos(20,20,0)
        self.walls.append(l4_wall)
    # Mur de fond
        f_wall = self.loader.loadModel("models/box")
        f_wall.reparentTo(render)
        f_wall.setScale(30,0.2,8)
        f_wall.setPos(-10,20,0)
        self.walls.append(f_wall)
        f1_wall = self.loader.loadModel("models/box")
        f1_wall.reparentTo(render)
        f1_wall.setScale(10,0.2,8)
        f1_wall.setPos(-10,40,0)
        self.walls.append(f1_wall)
        f2_wall = self.loader.loadModel("models/box")
        f2_wall.reparentTo(render)
        f2_wall.setScale(10,0.2,8)
        f2_wall.setPos(10,40,0)
        self.walls.append(f2_wall)
        f0_wall = self.loader.loadModel("models/box")
        f0_wall.reparentTo(render)
        f0_wall.setScale(10,0.2,4)
        f0_wall.setPos(0,40,4)
        #pas de collision
        #mur gauche5
        l5_wall = self.loader.loadModel("models/box")
        l5_wall.reparentTo(render)
        l5_wall.setScale(100,0.2,4)
        l5_wall.setPos(-50,200,0)
        self.walls.append(l5_wall)
        #mur droite5
        r5_wall = self.loader.loadModel("models/box")
        r5_wall.reparentTo(render)
        r5_wall.setScale(30,0.2,4)
        r5_wall.setPos(-40,190,0)
        self.walls.append(r5_wall)
        r5b_wall = self.loader.loadModel("models/box")
        r5b_wall.reparentTo(render)
        r5b_wall.setScale(50,0.2,4)
        r5b_wall.setPos(0,190,0)
        self.walls.append(r5b_wall)
        l6_wall = self.loader.loadModel("models/box")
        l6_wall.reparentTo(render)
        l6_wall.setScale(0.2,40,4)
        l6_wall.setPos(-10,150,0)
        self.walls.append(l6_wall)
        r6_wall = self.loader.loadModel("models/box")
        r6_wall.reparentTo(render)
        r6_wall.setScale(0.2,45,4)
        r6_wall.setPos(0,150,0)
        self.walls.append(r6_wall)
        b6_wall = self.loader.loadModel("models/box")
        b6_wall.reparentTo(render)
        b6_wall.setScale(10,0.2,1.5)
        b6_wall.setPos(-10,175,0)
        self.walls.append(b6_wall)
        b7_wall = self.loader.loadModel("models/box")
        b7_wall.reparentTo(render)
        b7_wall.setScale(10,0.2,1.5)
        b7_wall.setPos(-10,175,2.5)
        b8_wall = self.loader.loadModel("models/box")
        b8_wall.reparentTo(render)
        b8_wall.setScale(10,0.2,4)
        b8_wall.setPos(-10,169,0)
        self.walls.append(b8_wall)

        self.skybox = self.loader.loadModel("models/box")
        self.skybox.reparentTo(render)
        self.skybox.setScale(1000)
        self.skybox.setLightOff()
        self.skybox.setDepthWrite(False)
        self.skybox.setBin("background", 0)
        self.skybox.setTwoSided(True)
        sky = self.loader.loadTexture("skybox.png")
        self.skybox.setTexture(sky,1)





        tex = self.loader.loadTexture("texture_mur.png")

        left_wall.setTexture(tex, 1)
        right_wall.setTexture(tex, 1)
        r2_wall.setTexture(tex, 1)
        l2_wall.setTexture(tex, 1)
        l3_wall.setTexture(tex, 1)
        r3_wall.setTexture(tex, 1)
        r4_wall.setTexture(tex, 1)
        l4_wall.setTexture(tex, 1)
        f_wall.setTexture(tex, 1)
        f1_wall.setTexture(tex, 1)
        f2_wall.setTexture(tex, 1)
        f0_wall.setTexture(tex, 1)
        l5_wall.setTexture(tex, 1)
        r5_wall.setTexture(tex, 1)
        r5b_wall.setTexture(tex, 1)
        l6_wall.setTexture(tex, 1)
        r6_wall.setTexture(tex, 1)
        b6_wall.setTexture(tex, 1)
        b7_wall.setTexture(tex, 1)
        b8_wall.hide()


        texsol = self.loader.loadTexture("texture_sol.png")

        floor.setTexture(texsol, 1)
        floor2.setTexture(texsol, 1)
        floor3.setTexture(texsol, 1)
        floor4.setTexture(texsol, 1)
        floor5.setTexture(texsol, 1)
        floor6.setTexture(texsol, 1)
        interieur.setTexture(texsol, 1)


        textoit = self.loader.loadTexture("texture_toit.png")
        textoit2 = self.loader.loadTexture("texture_toit2.png")

        toit.setTexture(textoit,1)
        toit2.setTexture(textoit2,1)
        toit3.setTexture(textoit,1)
        toit4.setTexture(textoit2,1)
        toit5.setTexture(textoit2,1)
        toit6.setTexture(textoit,1)
        interieurt.setTexture(textoit,1)


        import random

        self.enemies = []

        positions = [
            (5, 110, 1),
            (3, 120, 1),
            (7, 120, 1),
            (-5,169.5,1),
            (-5, 180, 1)]
        for pos in positions:

            enemy = render.attachNewNode("enemy")
            enemy.setPos(*pos)

            body = self.loader.loadModel("models/box")
            body.reparentTo(enemy)
            body.setScale(1, 1, 1.5)
            body.setColor(1, 0, 0, 1)

            head = self.loader.loadModel("models/box")
            head.reparentTo(enemy)
            head.setScale(0.6)
            head.setPos(0, 0, 1.8)
            head.setColor(1, 0.8, 0.8, 1)

            self.enemies.append({
            "node": enemy,
            "body": body,
            "head": head,
            "hp": 150,
            "velocity_z": 0,
            "jump_timer": random.uniform(0.5, 1.5)
            })


        #self.finish = finish

    def setup_ui(self):
        from direct.gui.OnscreenText import OnscreenText

        self.crosshair = OnscreenText(
            text="+",
            pos=(0, 0),
            scale=0.3
            ,fg=(0, 1, 0, 1)
        )

        self.message_text = OnscreenText(
            text="",
            pos=(-0.7, 0.9),      # haut droite
            align=1,             # texte aligné à droite
            scale=0.05,
            mayChange=True,
            fg=(1,1,1,1)
        )

        self.ammo_text = OnscreenText(
            text="30/30",
            pos=(1.3, -0.9),
            align=1,
            scale=0.2,
            mayChange=True,
            fg=(1,1,1,1)
        )

        from direct.gui.DirectGui import DirectWaitBar

        self.hp_bar = DirectWaitBar(
            text="Vie",
            value=100,
            range=100,
            pos=(-1.15, 0, -0.9),   # bas gauche
            scale=(0.4, 1, 0.5)
        )

    def handle_shoot(self):
        bang = loader.loadSfx("sound.wav")
        bang.setVolume(3.0)

        if self.player.weapon.magazine <= 0:
            self.show_message("Recharge !", 1)
            return

        self.player.weapon.magazine -= 1
        import random
        if self.crouching:

            self.pitch += random.uniform(0.3, 0.7)
            self.heading -= random.uniform(-0.15, 0.15)

        else:

            self.pitch += random.uniform(0.8, 1.5)
            self.heading -= random.uniform(-0.4, 0.4)
        self.show_message("Bang !", 0.3)
        bang.play()

        from panda3d.core import LineSegs

        line = LineSegs()
        line.setColor(1, 1, 0, 1)
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
        origin = self.camera.getPos()
        forward = self.camera.getQuat().getForward()

        best_enemy = None
        best_hit = None
        best_dot = 0

        for enemy in self.enemies:

            enemy_pos = enemy["node"].getPos()

            body_pos = enemy_pos
            head_pos = enemy_pos + (0, 0, 1.8)

            body_dir = body_pos - origin
            head_dir = head_pos - origin

            body_dir.normalize()
            head_dir.normalize()

            body_dot = forward.dot(body_dir)
            head_dot = forward.dot(head_dir)

            if head_dot > best_dot:
                best_dot = head_dot
                best_enemy = enemy
                best_hit = "head"

            if body_dot > best_dot:
                best_dot = body_dot
                best_enemy = enemy
                best_hit = "body"

        if best_enemy is None:
            return

        enemy_pos = best_enemy["node"].getPos()

        distance = (enemy_pos - origin).length()

# précision variable selon la distance
        body_threshold = min(0.995, 0.97 + distance * 0.0002)
        head_threshold = min(0.9999, 0.995 + distance * 0.00005)

        if best_enemy:

            if best_hit == "head" and best_dot > head_threshold:
                best_enemy["hp"] -= 100
                self.show_message("HEADSHOT !", 1)

            elif best_hit == "body" and best_dot > body_threshold:
                best_enemy["hp"] -= 40
                self.show_message("Touché !", 0.8)

            if best_enemy["hp"] <= 0:
                best_enemy["node"].removeNode()
                self.enemies.remove(best_enemy)
                self.kill_sounds[self.kill_index].play()
                self.kill_index += 1
                if self.kill_index >= len(self.kill_sounds):
                    self.kill_index = 0
                self.player.score += 100
                self.show_message("ENNEMI TUÉ +100", 1.5)
                from random import choice
                choice(self.kill_sounds).play()


    def update(self, task):

        self.skybox.setPos((self.camera.getX()-500,self.camera.getY()-500,-5))

        self.ammo_text.setText(
            f"{self.player.weapon.magazine}/30"
        )

        self.hp_bar["value"] = self.player_hp
        self.hp_bar["text"] = f"{self.player_hp} HP"
        if self.player_hp > 60:
            self.hp_bar["barColor"] = (0, 1, 0, 1)      # vert

        elif self.player_hp > 30:
            self.hp_bar["barColor"] = (1, 0.6, 0, 1)    # orange

        else:
            self.hp_bar["barColor"] = (1, 0, 0, 1)      # rouge
        if self.mouse_locked and self.mouseWatcherNode.hasMouse():

            mouse = self.win.getPointer(0)

            x = mouse.getX()
            y = mouse.getY()

            center_x = self.win.getXSize() // 2
            center_y = self.win.getYSize() // 2

            dx = x - center_x
            dy = y - center_y

            self.heading -= dx * self.mouse_sensitivity
            self.pitch -= dy * self.mouse_sensitivity

            self.pitch = max(-85, min(85, self.pitch))

            self.camera.setH(self.heading)
            self.camera.setP(self.pitch)

            self.win.movePointer(
            0,
            center_x,
            center_y
            )


        dt = globalClock.getDt()
        self.fire_timer -= dt

        if self.shooting and self.fire_timer <= 0:

            self.handle_shoot()

            self.fire_timer = self.fire_rate

        speed = 20 + self.air_speed_bonus
        if self.crouching:
            speed *= 0.6

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

        ground_height = 1.0 if self.crouching else 1.8

        if new_z <= ground_height:
            new_z = ground_height
            self.vertical_velocity = 0
            if not self.on_ground:
                self.air_speed_bonus *= 0.9
            self.on_ground = True

        if self.player_hp<=0:
            from direct.gui.OnscreenText import OnscreenText
            from panda3d.core import TextNode
            total_time = self.score_manager.get_elapsed_time()
            final_score = self.score_manager.calculate_final_score(self.player, total_time)
            rank = self.score_manager.get_rank(final_score)
            print(f"Game Over! Score: {final_score}, Rank: {rank}")
            OnscreenText(text="GAME OVER",pos=(0,0),scale=0.2,fg=(1,0,0,1),align=TextNode.ACenter)
            self.taskMgr.doMethodLater(
            3.0,           # attendre 3 secondes
            self.quit_game,
            "quit_game"
            )


        self.camera.setZ(new_z)
#
        # IA ennemi simple
        import random

        for enemy in self.enemies:

            node = enemy["node"]

            enemy_pos = node.getPos()
            player_pos = self.camera.getPos()

            direction = player_pos - enemy_pos
            direction.setZ(0)

            distance = direction.length()

# L'ennemi ne s'active qu'à moins de 60 mètres
            if distance <= 100:

    # Il s'arrête à 10 mètres du joueur
                if distance >= 20:

                    direction.normalize()

                    strafe = direction.cross((0, 0, 1))
                    strafe.normalize()

                    move = (
                        direction * 10 +
                        strafe * random.uniform(-4, 4)
                    )

                    move.normalize()

                    new_pos = enemy_pos + move * 12 * dt

                    # Collision avec les murs
                    if not self.collides_with_wall(new_pos):
                        node.setPos(new_pos)

                node.lookAt(self.camera)
            enemy["jump_timer"] -= dt

            if enemy["jump_timer"] <= 0:

                enemy["velocity_z"] = 8
                enemy["jump_timer"] = random.uniform(1, 1.5)

            enemy["velocity_z"] -= 25 * dt

            new_z = (
                node.getZ() +
                enemy["velocity_z"] * dt
            )

            if new_z < 1:
                new_z = 1
                enemy["velocity_z"] = 0

            node.setZ(new_z)
            self.enemy_shot_timer -= dt
            if len(self.enemies) == 0:
                return task.cont
            distance = (
                node.getPos() -
                self.camera.getPos()
            ).length()



            if distance <= 20:

                    if self.enemy_shot_timer <= 0:
                        from panda3d.core import LineSegs

                        line = LineSegs()
                        line.setColor(1, 0, 0)
                        line.setThickness(2)
                        line.moveTo(node.getPos())
                        line.drawTo(self.camera.getPos())

                        beam = render.attachNewNode(line.create())
                        bang = loader.loadSfx("tire.mp3")
                        bang.play()

                        self.taskMgr.doMethodLater(
                         0.05,
                        lambda task, b=beam: (b.removeNode(), task.done)[1],
                        f"enemy_beam_{id(beam)}"
                        )

                        self.player_hp -= 5

                        self.show_message(
                        f"-10 HP ({self.player_hp})",
                        0.5
                        )

                        self.enemy_shot_timer = 2



#
        print(self.camera.getY())
        if self.camera.getY() > 300:
            self.end_game()


        return task.cont

    def end_game(self):

        from direct.gui.OnscreenText import OnscreenText
        from panda3d.core import TextNode

    # éviter de recréer les textes à chaque frame
        if hasattr(self, "victory_shown"):
            return

        self.victory_shown = True

        total_time = self.score_manager.get_elapsed_time()
        final_score = self.score_manager.calculate_final_score(
            self.player,
            total_time
        )

        rank = self.score_manager.get_rank(final_score)

        OnscreenText(
            text="MISSION ACCOMPLIE",
            pos=(0, 0.3),
            scale=0.15,
            fg=(0, 1, 0, 1),
            align=TextNode.ACenter
        )

        OnscreenText(
        text=f"Score : {final_score}",
        pos=(0, 0.05),
        scale=0.1,
        align=TextNode.ACenter
        )

        OnscreenText(
        text=f"Rang : {rank}",
        pos=(0, -0.1),
        scale=0.08,
        fg=(1, 1, 0, 1),
        align=TextNode.ACenter
        )

        self.taskMgr.doMethodLater(
        5,
        self.quit_game,
        "victory_quit"
        )
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

            self.air_speed_bonus += 2
            self.air_speed_bonus = min(self.air_speed_bonus, 12)
    def start_crouch(self):

        self.crouching = True

        self.camera.setZ(1.0)

    def stop_crouch(self):

        self.crouching = False

        if self.on_ground:
            self.camera.setZ(1.8)
    def increase_sensitivity(self):
        self.mouse_sensitivity += 0.01
        self.show_message(f"Sensibilité souris: {self.mouse_sensitivity:.2f}", 1)
    def decrease_sensitivity(self):
        self.mouse_sensitivity -= max(0.01, self.mouse_sensitivity - 0.01)
        self.show_message(f"Sensibilité souris: {self.mouse_sensitivity:.2f}", 1)
    def start_shooting(self):
        self.shooting = True

    def stop_shooting(self):
        self.shooting = False
    def quit_game(self, task):
        sys.exit()

if __name__ == "__main__":
    game = TacticalFPS()
    game.run()
