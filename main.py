from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from entities import Player, Enemy
from managers import ScoreManager, EnemySpawner
import sys
import webbrowser

class TacticalFPS(ShowBase):
    def start_game(self):

        self.game_started = True

        self.start_frame.destroy()

        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)

        self.win.requestProperties(props)

        center_x = self.win.getXSize() // 2
        center_y = self.win.getYSize() // 2

        self.win.movePointer(
            0,
            center_x,
            center_y
        )

    def show_start_screen(self):

        from direct.gui.DirectGui import DirectFrame, DirectButton
        from direct.gui.OnscreenText import OnscreenText

        self.start_frame = DirectFrame(
            frameColor=(0, 0, 0, 1),
            frameSize=(-2, 2, -2, 2)
        )

        OnscreenText(
            text="TACTICAL FPS",
            parent=self.start_frame,
            pos=(0, 0.3),
            scale=0.15,
            fg=(1, 1, 1, 1)
        )
        DirectButton(
            text="PARAMETRES",
            scale=0.08,
            pos=(0, 0, -0.45),
            parent=self.start_frame,
            command=self.show_settings
        )

        OnscreenText(
            text="Eliminez tous les ennemis puis atteignez la sortie",
            parent=self.start_frame,
            pos=(0, 0.1),
            scale=0.05
        )
        DirectButton(
            text="GitHub",
            scale=0.08,
            pos=(0, 0, -0.7),
            parent=self.start_frame,
            command=lambda: webbrowser.open("https://github.com/StageSG-2nd-2026/DemoJV")
        )

        DirectButton(
            text="JOUER",
            scale=0.08,
            pos=(0, 0, -0.15),
            parent=self.start_frame,
            command=self.start_game
        )
        DirectButton(
            text="???",
            scale=0.08,
            pos=(0, 0, -0.60),
            parent=self.start_frame,
            command=self.open_youtube
        )

        self.best_score_text = OnscreenText(
            text=f"Meilleur score : {self.best_score}",
            pos=(0, -0.2),
            scale=0.07,
            fg=(1, 1, 0, 1)
        )

        DirectButton(
            text="QUITTER",
            scale=0.08,
            pos=(0, 0, -0.3),
            parent=self.start_frame,
            command=sys.exit
        )
        self.start_frame["image"] = "end.png"

    def toggle_pause(self):

        self.paused = not self.paused

        if self.paused:

            from direct.gui.DirectGui import DirectFrame, DirectButton

            self.pause_frame = DirectFrame(
                frameColor=(0, 0, 0, 0.7),
                frameSize=(-0.5, 0.5, -0.4, 0.4)
            )

            DirectButton(
                text="Reprendre",
                scale=0.08,
                pos=(0, 0, 0.2),
                parent=self.pause_frame,
                command=self.toggle_pause
            )

            DirectButton(
                text="Parametres",
                scale=0.08,
                pos=(0, 0, 0),
                parent=self.pause_frame,
                command=self.show_pause_settings
            )

            DirectButton(
                text="Quitter",
                scale=0.08,
                pos=(0, 0, -0.2),
                parent=self.pause_frame,
                command=sys.exit
            )

            props = WindowProperties()
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)
            self.win.requestProperties(props)

        else:

            if self.pause_frame:
                self.pause_frame.destroy()

            props = WindowProperties()
            props.setCursorHidden(True)
            props.setMouseMode(WindowProperties.M_relative)
            self.win.requestProperties(props)

            center_x = self.win.getXSize() // 2
            center_y = self.win.getYSize() // 2
            self.win.movePointer(0, center_x, center_y)
    def apply_pause_settings(self):

        self.mouse_sensitivity = self.pause_sens_slider["value"]

        self.show_message(
            f"Sensibilite : {self.mouse_sensitivity:.2f}",
            1
        )

        self.pause_settings_frame.destroy()

    def show_pause_settings(self):

        from direct.gui.DirectGui import DirectFrame
        from direct.gui.DirectGui import DirectButton
        from direct.gui.DirectGui import DirectSlider
        from direct.gui.OnscreenText import OnscreenText

        self.pause_settings_frame = DirectFrame(
            frameColor=(0,0,0,0.9),
            frameSize=(-0.8,0.8,-0.6,0.6)
        )

        OnscreenText(
            text="Sensibilite souris",
            parent=self.pause_settings_frame,
            pos=(0,0.25),
            scale=0.07
        )

        self.pause_sens_slider = DirectSlider(
            parent=self.pause_settings_frame,
            range=(0.05,0.5),
            value=self.mouse_sensitivity,
            scale=0.5,
            pos=(0,0,0)
        )

        DirectButton(
            text="Valider",
            parent=self.pause_settings_frame,
            scale=0.06,
            pos=(0,0,-0.25),
            command=self.apply_pause_settings
        )


    def has_line_of_sight(self, start, end):

        direction = end - start
        distance = direction.length()

        if distance == 0:
            return True

        direction.normalize()

        step = 0.5
        current = start
        travelled = 0

        while travelled < distance:

            for wall in self.walls:

                # b8_wall laisse passer les balles
                if wall in self.bullet_pass_walls:
                    continue

                bounds = wall.getTightBounds()

                if bounds is None:
                    continue

                min_p, max_p = bounds

                if (
                    min_p.x <= current.x <= max_p.x
                    and
                    min_p.y <= current.y <= max_p.y
                ):
                    return False

            current += direction * step
            travelled += step

        return True

        while travelled < distance:

                if self.collides_with_wall(current):
                    return False

                current += direction * step
                travelled += step

        return True

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

        player_radius = 1

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
        self.game_started = False
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
        self.player_armor =100
        self.enemy_shot_timer = 0
        self.paused = False
        self.pause_frame = None

        self.accept("i", self.toggle_pause)

        ShowBase.__init__(self)
        try:
            with open("best_score.txt", "r") as f:
                self.best_score = int(f.read())
        except:
            self.best_score = 0

        from panda3d.core import DisplayRegion

        # Caméra de minimap
        self.minimap_cam = self.makeCamera(self.win)

        # Coin supérieur droit
        dr = self.minimap_cam.node().getDisplayRegion(0)
        dr.setDimensions(0.75, 1.0, 0.75, 1.0)

        self.minimap_cam.reparentTo(render)

        # Vue de dessus
        self.minimap_cam.setPos(0, 0, 100)
        self.minimap_cam.setP(-90)

        from panda3d.core import OrthographicLens

        lens = OrthographicLens()
        lens.setFilmSize(80, 80)

        self.minimap_cam.node().setLens(lens)

        self.crouching = False
        self.accept("c", self.start_crouch)
        self.accept("c-up", self.stop_crouch)
        self.kill_sounds = [
            self.loader.loadSfx("killsound1.wav"),
            self.loader.loadSfx("killsound2.wav"),
            self.loader.loadSfx("killsound3.wav"),
            self.loader.loadSfx("killsound4.wav"),
            self.loader.loadSfx("killsound5.wav")
        ]
        for sound in self.kill_sounds:
            sound.setVolume(1.0)


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
        self.show_start_screen()

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
    def open_youtube(self):
        webbrowser.open("https://youtu.be/dQw4w9WgXcQ?si=kXAHIlXrw_UiIjVi")
    def apply_settings(self):

        self.mouse_sensitivity = self.sens_slider["value"]

        self.settings_frame.destroy()
    def show_settings(self):

        from direct.gui.DirectGui import DirectFrame
        from direct.gui.DirectGui import DirectButton
        from direct.gui.DirectGui import DirectSlider
        from direct.gui.OnscreenText import OnscreenText

        self.settings_frame = DirectFrame(
            frameColor=(0,0,0,0.9),
            frameSize=(-1,1,-1,1)
        )

        OnscreenText(
            text="Sensibilite souris",
            parent=self.settings_frame,
            pos=(0,0.3),
            scale=0.08
        )

        self.sens_slider = DirectSlider(
            parent=self.settings_frame,
            range=(0.05,0.5),
            value=self.mouse_sensitivity,
            scale=0.5,
            pos=(0,0,0)
        )

        DirectButton(
            text="Valider",
            parent=self.settings_frame,
            scale=0.07,
            pos=(0,0,-0.3),
            command=self.apply_settings
        )

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
        sbs = self.loader.loadModel("models/box")
        sbs.reparentTo(render)
        sbs.setScale(50,50,0.2)
        sbs.setPos(50,170,0)


    # Toit
        toit = self.loader.loadModel("models/box")
        toit.reparentTo(render)
        toit.setScale(10, 110, 0.2)
        toit.setPos(0, 40, 6)
        toit2 = self.loader.loadModel("models/box")
        toit2.reparentTo(render)
        toit2.setScale(50, 10, 0.2)
        toit2.setPos(-50, 140, 6)
        toit3 = self.loader.loadModel("models/box")
        toit3.reparentTo(render)
        toit3.setScale(10, 50, 0.2)
        toit3.setPos(-50, 150, 6)
        toit4 = self.loader.loadModel("models/box")
        toit4.reparentTo(render)
        toit4.setScale(30, 20, 0.2)
        toit4.setPos(-10, 20, 10)
        toit5 = self.loader.loadModel("models/box")
        toit5.reparentTo(render)
        toit5.setScale(90,10,0.2)
        toit5.setPos(-40,190,6)
        toit6 = self.loader.loadModel("models/box")
        toit6.reparentTo(render)
        toit6.setScale(10,40,0.2)
        toit6.setPos(-10,150,6)
        interieurt = self.loader.loadModel("models/box")
        interieurt.reparentTo(render)
        interieurt.setScale(30, 40, 0.2)
        interieurt.setPos(-40, 150, 6)
        sbt = self.loader.loadModel("models/box")
        sbt.reparentTo(render)
        sbt.setScale(50,50,0.2)
        sbt.setPos(50,170,10)

    # Mur gauche
        left_wall = self.loader.loadModel("models/box")
        left_wall.reparentTo(render)
        left_wall.setScale(0.2, 100, 6)
        left_wall.setPos(0, 40,0)
        self.walls.append(left_wall)

    # Mur droit
        right_wall = self.loader.loadModel("models/box")
        right_wall.reparentTo(render)
        right_wall.setScale(0.2, 110, 6)
        right_wall.setPos(10, 40, 0)
        self.walls.append(right_wall)

    # Mur du droit 2
        r2_wall = self.loader.loadModel("models/box")
        r2_wall.reparentTo(render)
        r2_wall.setScale(50, 0.2, 6)
        r2_wall.setPos(-40, 150, 0)
        self.walls.append(r2_wall)
    # Mur de gaucke 2
        l2_wall = self.loader.loadModel("models/box")
        l2_wall.reparentTo(render)
        l2_wall.setScale(50, 0.2, 6)
        l2_wall.setPos(-50, 140, 0)
        self.walls.append(l2_wall)
    # Mur de gauche 3
        l3_wall = self.loader.loadModel("models/box")
        l3_wall.reparentTo(render)
        l3_wall.setScale(0.2, 60, 6)
        l3_wall.setPos(-50, 140, 0)
        self.walls.append(l3_wall)
    # Mur de droite 3
        r3_wall = self.loader.loadModel("models/box")
        r3_wall.reparentTo(render)
        r3_wall.setScale(0.2, 40, 6)
        r3_wall.setPos(-40, 150, 0)
        self.walls.append(r3_wall)
    # Mur de gauche debut
        r4_wall = self.loader.loadModel("models/box")
        r4_wall.reparentTo(render)
        r4_wall.setScale(0.2,20,10)
        r4_wall.setPos(-10,20,0)
        self.walls.append(r4_wall)
    # Mur de droite debut
        l4_wall = self.loader.loadModel("models/box")
        l4_wall.reparentTo(render)
        l4_wall.setScale(0.2,20,10)
        l4_wall.setPos(20,20,0)
        self.walls.append(l4_wall)
    # Mur de fond
        f_wall = self.loader.loadModel("models/box")
        f_wall.reparentTo(render)
        f_wall.setScale(30,0.2,10)
        f_wall.setPos(-10,20,0)
        self.walls.append(f_wall)
        f1_wall = self.loader.loadModel("models/box")
        f1_wall.reparentTo(render)
        f1_wall.setScale(10,0.2,10)
        f1_wall.setPos(-10,40,0)
        self.walls.append(f1_wall)
        f2_wall = self.loader.loadModel("models/box")
        f2_wall.reparentTo(render)
        f2_wall.setScale(10,0.2,10)
        f2_wall.setPos(10,40,0)
        self.walls.append(f2_wall)
        f0_wall = self.loader.loadModel("models/box")
        f0_wall.reparentTo(render)
        f0_wall.setScale(10,0.2,4)
        f0_wall.setPos(0,40,6)
        #pas de collision
        #mur gauche5
        l5_wall = self.loader.loadModel("models/box")
        l5_wall.reparentTo(render)
        l5_wall.setScale(100,0.2,6)
        l5_wall.setPos(-50,200,0)
        self.walls.append(l5_wall)
        #mur droite5
        r5_wall = self.loader.loadModel("models/box")
        r5_wall.reparentTo(render)
        r5_wall.setScale(30,0.2,6)
        r5_wall.setPos(-40,190,0)
        self.walls.append(r5_wall)
        r5b_wall = self.loader.loadModel("models/box")
        r5b_wall.reparentTo(render)
        r5b_wall.setScale(50,0.2,6)
        r5b_wall.setPos(0,190,0)
        self.walls.append(r5b_wall)
        l6_wall = self.loader.loadModel("models/box")
        l6_wall.reparentTo(render)
        l6_wall.setScale(0.2,40,6)
        l6_wall.setPos(-10,150,0)
        self.walls.append(l6_wall)
        r6_wall = self.loader.loadModel("models/box")
        r6_wall.reparentTo(render)
        r6_wall.setScale(0.2,45,6)
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
        b7_wall.setPos(-10,175,4.5)
        b8_wall = self.loader.loadModel("models/box")
        b8_wall.reparentTo(render)
        b8_wall.setScale(10,0.2,6)
        b8_wall.setPos(-10,169,0)
        self.walls.append(b8_wall)
        end = self.loader.loadModel("models/box")
        end.reparentTo(render)
        end.setScale(0.2,10,6)
        end.setPos(100,190,0)
        end.setLightOff()
        self.bullet_pass_walls = []
        self.bullet_pass_walls.append(b8_wall)
        self.bullet_pass_walls.append(b7_wall)
        self.bullet_pass_walls.append(b6_wall)


        sb = self.loader.loadModel("models/box")
        sb.reparentTo(render)
        sb.setScale(0.2,20,10)
        sb.setPos(50,170,0)
        self.walls.append(sb)
        sb1 = self.loader.loadModel("models/box")
        sb1.reparentTo(render)
        sb1.setScale(0.2,20,10)
        sb1.setPos(50,200,0)
        self.walls.append(sb1)
        sb2 = self.loader.loadModel("models/box")
        sb2.reparentTo(render)
        sb2.setScale(50,0.2,10)
        sb2.setPos(50,170,0)
        self.walls.append(sb2)
        sb3 = self.loader.loadModel("models/box")
        sb3.reparentTo(render)
        sb3.setScale(50,0.2,10)
        sb3.setPos(50,220,0)
        self.walls.append(sb3)
        sb4 = self.loader.loadModel("models/box")
        sb4.reparentTo(render)
        sb4.setScale(0.2,20,10)
        sb4.setPos(100,170,0)
        self.walls.append(sb4)
        sb5 = self.loader.loadModel("models/box")
        sb5.reparentTo(render)
        sb5.setScale(0.2,20,10)
        sb5.setPos(100,200,0)
        self.walls.append(sb5)
        endr = self.loader.loadModel("models/box")
        endr.reparentTo(render)
        endr.setScale(0.2,10,4)
        endr.setPos(100,190,6)
        endrb = self.loader.loadModel("models/box")
        endrb.reparentTo(render)
        endrb.setScale(0.2,10,4)
        endrb.setPos(50,190,6)





        self.skybox = self.loader.loadModel("models/box")
        self.skybox.reparentTo(render)
        self.skybox.setScale(1000)
        self.skybox.setLightOff()
        self.skybox.setDepthWrite(False)
        self.skybox.setBin("background", 0)
        self.skybox.setTwoSided(True)
        sky = self.loader.loadTexture("skybox.png")
        self.skybox.setTexture(sky,1)

        self.playerc = self.loader.loadModel("models/box")
        self.playerc.reparentTo(render)
        self.playerc.setScale(3)
        self.playerc.setPos(0,0,11)
        self.playerc.setColor(0,255,0,1)





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
        sb.setTexture(tex, 1)
        sb1.setTexture(tex, 1)
        sb2.setTexture(tex, 1)
        sb3.setTexture(tex, 1)
        sb4.setTexture(tex, 1)
        sb5.setTexture(tex, 1)
        endr.setTexture(tex, 1)
        endrb.setTexture(tex, 1)
        b8_wall.hide()


        texsol = self.loader.loadTexture("texture_sol.png")

        floor.setTexture(texsol, 1)
        floor2.setTexture(texsol, 1)
        floor3.setTexture(texsol, 1)
        floor4.setTexture(texsol, 1)
        floor5.setTexture(texsol, 1)
        floor6.setTexture(texsol, 1)
        interieur.setTexture(texsol, 1)
        sbs.setTexture(texsol,1)


        textoit = self.loader.loadTexture("texture_toit.png")
        textoit2 = self.loader.loadTexture("texture_toit2.png")

        toit.setTexture(textoit,1)
        toit2.setTexture(textoit2,1)
        toit3.setTexture(textoit,1)
        toit4.setTexture(textoit2,1)
        toit5.setTexture(textoit2,1)
        toit6.setTexture(textoit,1)
        interieurt.setTexture(textoit,1)
        sbt.setTexture(textoit,1)

        endtex = self.loader.loadTexture("end.png")
        end.setTexture(endtex,1)


        import random
        self.medkits = []
        medkit_positions = [
            (5, 80, 1),
            (-45, 160, 1),
            (-5, 185, 1)
        ]

        for pos in medkit_positions:

            medkit = self.loader.loadModel("models/box")
            medkit.reparentTo(render)
            medkit.setPos(*pos)

            medkit.setScale(0.5)
            medkit.setColor(0, 1, 0, 1)

            self.medkits.append(medkit)

        self.enemies = []

        positions = [
            (5, 110, 1),
            (3, 120, 1),
            (7, 120, 1),
            (-5,169.5,1),
            (-5, 180, 1),
            (-45,145,1),
            (-45,195,1),
            (-1,190,1),
            (50,195,1)]
        for pos in positions:
            enemy = render.attachNewNode("enemy")
            enemy.setPos(*pos)

            body = self.loader.loadModel("models/box")
            body.reparentTo(enemy)
            body.setScale(1, 1, 1.5)
            body.setColor(1, 0, 0, 1)
            enemy_model = loader.loadModel("enemy_detailed.obj")
            enemy_model.reparentTo(enemy)
            enemy_model.setScale(1)

            head = self.loader.loadModel("models/box")
            head.reparentTo(enemy)
            head.setScale(0.6)
            head.setPos(0, 0, 1.8)
            head.setColor(1, 0.8, 0.8, 1)
            # Cube rouge au-dessus de l'ennemi
            marker = self.loader.loadModel("models/box")
            marker.reparentTo(enemy)
            marker.setScale(2)
            marker.setPos(0, 0, 11)
            marker.setColor(1, 0, 0, 1)

            # ======================
            # Barre de vie
            # ======================

            hp_node = enemy.attachNewNode("hp_node")
            hp_node.setPos(0, 0, 2.8)

            from panda3d.core import BillboardEffect
            hp_node.setEffect(
                BillboardEffect.makePointEye()
            )

            hp_bg = self.loader.loadModel("models/box")
            hp_bg.reparentTo(hp_node)
            hp_bg.setScale(1.2, 0.05, 0.08)
            hp_bg.setColor(0, 0, 0, 1)
            hp_bg.hide()

            hp_fill = self.loader.loadModel("models/box")
            hp_fill.reparentTo(hp_node)
            hp_fill.setScale(1.0, 0.04, 0.06)
            hp_fill.setColor(0, 1, 0, 1)


            self.enemies.append({
                "node": enemy,
                "body": body,
                "head": head,
                "hp_fill": hp_fill,
                "hp": 150,
                "max_hp": 150,
                "velocity_z": 0,
                "jump_timer": random.uniform(0.5, 1.5),
            })
        boss = render.attachNewNode("boss")
        boss.setPos(75, 195, 1)
        boss_body = self.loader.loadModel("models/box")
        boss_body.reparentTo(boss)
        boss_body.setScale(3, 3, 4)
        boss_body.setColor(0.5, 0, 0, 1)
        boss_head = self.loader.loadModel("models/box")
        boss_head.reparentTo(boss)
        boss_head.setScale(1.5)
        boss_head.setPos(0, 0, 4.5)
        boss_head.setColor(1, 0, 0, 1)
        boss_hp_node = boss.attachNewNode("boss_hp")

        from panda3d.core import BillboardEffect
        boss_hp_node.setEffect(
            BillboardEffect.makePointEye()
        )

        boss_hp_node.setPos(0, 0, 6)

        boss_hp_fill = self.loader.loadModel("models/box")
        boss_hp_fill.reparentTo(boss_hp_node)
        boss_hp_fill.setScale(3, 0.08, 0.15)
        boss_hp_fill.setColor(0, 1, 0, 1)
        self.enemies.append({
            "node": boss,
            "body": boss_body,
            "head": boss_head,
            "hp_fill": boss_hp_fill,
            "hp": 1000,
            "max_hp": 1000,
            "velocity_z": 0,
            "jump_timer": 1,
            "is_boss": True
        })
        boss_body.setScale(4, 4, 6)
        boss_head.setScale(2)
        boss_head.setPos(0, 0, 6.5)


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


        self.armor_bar = DirectWaitBar(
            text="Armure",
            value=100,
            range=100,
            pos=(-1.15, 0, -0.8),
            scale=(0.4, 1, 0.5),
            barColor=(0, 0.5, 1, 1)
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
        closest_wall = None
        closest_distance = 999999
        impact_pos = None

        for wall in self.walls:

            bounds = wall.getTightBounds()

            if bounds is None:
                continue

            min_p, max_p = bounds

            for dist in range(1, 100):

                test_pos = origin + forward * dist

                if (
                    min_p.x <= test_pos.x <= max_p.x
                    and
                    min_p.y <= test_pos.y <= max_p.y
                    and
                    min_p.z <= test_pos.z <= max_p.z
                ):

                    if dist < closest_distance:
                        closest_distance = dist
                        closest_wall = wall
                        impact_pos = test_pos

                    break
        if impact_pos:

            impact = self.loader.loadModel("models/box")
            impact.reparentTo(render)

            impact.setScale(0.08)
            impact.setPos(impact_pos)

            impact.setColor(0.1, 0.1, 0.1, 1)

            self.taskMgr.doMethodLater(
                15,
                lambda task, n=impact: (
                    n.removeNode(),
                    task.done
                )[1],
                f"impact_{id(impact)}"
            )

        best_enemy = None
        best_hit = None
        best_dot = 0

        for enemy in self.enemies:
            if enemy["node"].isEmpty():
                continue

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

            enemy_pos = best_enemy["node"].getPos()

            if self.has_line_of_sight(
                self.camera.getPos(),
                enemy_pos
            ):

                if best_hit == "head" and best_dot > head_threshold:

                    best_enemy["hp"] -= 100
                    self.show_message("HEADSHOT !", 1)

                elif best_hit == "body" and best_dot > body_threshold:

                    best_enemy["hp"] -= 40
                    self.show_message("Touché !", 0.8)
                if best_enemy["hp"] <= 0:

                    best_enemy["node"].removeNode()


                    if best_enemy.get("is_boss"):
                        self.player.score += 1000
                        self.show_message("BOSS ELIMINE +1000", 3)
                        self.kill_sounds[self.kill_index].play
                    else:
                        self.player.score += 100
                        self.show_message("ENNEMI TUÉ +100", 1.5)
                        self.kill_sounds[self.kill_index].play


                    self.kill_index += 1

                    if self.kill_index >= len(self.kill_sounds):
                            self.kill_index = 0


    def update(self, task):
        if not self.game_started:
            return task.cont
        if hasattr(self, "best_score_text"):
            self.best_score_text.destroy()
            del self.best_score_text
        if self.paused:
         return task.cont

        self.skybox.setPos((self.camera.getX()-500,self.camera.getY()-500,-5))

        self.ammo_text.setText(
            f"{self.player.weapon.magazine}/30"
        )

        self.hp_bar["value"] = self.player_hp
        self.armor_bar["value"] = self.player_armor
        self.armor_bar["text"] = f"{self.player_armor} ARMURE"
        self.hp_bar["text"] = f"{self.player_hp} HP"
        if self.player_hp > 60:
            self.hp_bar["barColor"] = (0, 1, 0, 1)      # vert

        elif self.player_hp > 30:
            self.hp_bar["barColor"] = (1, 0.6, 0, 1)    # orange

        else:
            self.hp_bar["barColor"] = (1, 0, 0, 1)      # rouge
        if self.player_armor > 60:
            self.armor_bar["barColor"] = (0, 0.5, 1, 1)

        elif self.player_armor > 30:
            self.armor_bar["barColor"] = (0.3, 0.3, 1, 1)

        else:
            self.armor_bar["barColor"] = (0.8, 0.8, 0.8, 1)
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
            if final_score > self.best_score:
                with open("best_score.txt", "w") as f:
                    f.write(str(final_score))
            print(f"Game Over! Score: {final_score}, Rank: {rank}")
            OnscreenText(text="GAME OVER",pos=(0,0),scale=0.2,fg=(1,0,0,1),align=TextNode.ACenter)
            self.taskMgr.doMethodLater(
            1.0,           # attendre 3 secondes
            self.quit_game,
            "quit_game"
            )


        self.camera.setZ(new_z)
        self.playerc.setPos(camera.getX()-1,camera.getY()-1,11)
    #
        # IA ennemi simple
        import random

        for enemy in self.enemies:
            ratio = enemy["hp"] / enemy["max_hp"]

            enemy["hp_fill"].setScale(
            max(0.01, ratio),
            0.04,
            0.06
            )

            enemy["hp_fill"].setX(
            -(1 - ratio) / 2
            )
            if ratio > 0.6:
                enemy["hp_fill"].setColor(0, 1, 0, 1)

            elif ratio > 0.3:
                enemy["hp_fill"].setColor(1, 0.7, 0, 1)

            else:
                enemy["hp_fill"].setColor(1, 0, 0, 1)

            node = enemy["node"]
            if node.isEmpty():
                continue

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
            if node.isEmpty():
                continue
            distance = (
                node.getPos() -
                self.camera.getPos()
            ).length()


            if node.isEmpty():
                continue
            if distance <= 25 and self.has_line_of_sight(node.getPos(),self.camera.getPos()):

                if self.enemy_shot_timer <= 0:

                    import random
                    import math

                    # Direction réelle vers le joueur
                    if node.isEmpty():
                        continue
                    shoot_dir = self.camera.getPos() - node.getPos()
                    shoot_dir.setZ(0)
                    shoot_dir.normalize()

                    # Erreur aléatoire entre -10° et +10°
                    angle_error = random.uniform(-10, 10)

                    heading = math.degrees(
                        math.atan2(shoot_dir.getX(), shoot_dir.getY())
                    )

                    heading += angle_error

                    # Nouvelle direction de tir
                    shot_x = math.sin(math.radians(heading))
                    shot_y = math.cos(math.radians(heading))

                    shot_dir = (shot_x, shot_y)

                    # Direction parfaite vers le joueur
                    player_x = shoot_dir.getX()
                    player_y = shoot_dir.getY()

                    # Produit scalaire
                    dot = (
                        shot_x * player_x +
                        shot_y * player_y
                    )

                    # Le joueur est touché seulement si le tir passe assez près
                    if dot > 0.98:

                        damage = 5

                        if self.player_armor > 0:

                            armor_damage = damage * 0.7
                            health_damage = damage * 0.3

                            self.player_armor = max(
                                0,
                                self.player_armor - armor_damage
                            )

                            self.player_hp -= health_damage

                        else:
                            self.player_hp -= damage

                        self.show_message(
                            f"-10 HP ({self.player_hp})",
                            0.5
                        )

                    self.enemy_shot_timer = 2




        print(self.camera.getX(),self.camera.getY())
        if self.camera.getY() > 190 and self.camera.getX() >100:
            self.end_game()
        player_pos = self.camera.getPos()

        self.minimap_cam.setPos(
         player_pos.getX(),
         player_pos.getY(),
         100
        )
        self.minimap_cam.setH(0)
        for medkit in self.medkits[:]:

            distance = (
                medkit.getPos() -
                self.camera.getPos()
            ).length()
            medkit.setH(
                medkit.getH() + 100 * dt
            )

            if distance < 2:

                self.player_hp = min(
                    100,
                    self.player_hp + 30
                )

                self.show_message(
                    "+30 HP",
                    1
                )

                medkit.removeNode()
                self.medkits.remove(medkit)


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
        if final_score > self.best_score:
            self.best_score = final_score

            with open("best_score.txt", "w") as f:
                f.write(str(final_score))
        print(total_time)

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
