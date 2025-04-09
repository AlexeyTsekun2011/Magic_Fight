import random

import pygame as pg

pg.init()

from constants import *
from utils import *
from enemy import Enemy
from magicball import *
import pygame_menu

GESTURE_MODE = False
if GESTURE_MODE:
    from gesture import Gesture


class Player(pg.sprite.Sprite):
    def __init__(self, folder="fire wizard", first_player=True):
        super().__init__()

        self.folder = folder

        self.load_animations()
        if first_player:
            coord = (100, SCREEN_HEIGHT // 1.8)
            self.side = "right"
            self.current_animation = self.idle_animation_right
            self.key_left = pg.K_a
            self.key_right = pg.K_d
            self.key_down = pg.K_s
            self.key_charge = pg.K_SPACE

        else:
            coord = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 1.8)
            self.side = "left"
            self.current_animation = self.idle_animation_left
            self.key_right = pg.K_RIGHT
            self.key_down = pg.K_DOWN
            self.key_left = pg.K_LEFT
            self.key_charge = pg.K_RSHIFT

        self.current_image = 0
        self.image = self.current_animation[self.current_image]

        self.rect = self.image.get_rect()
        self.rect.center = coord

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.animation_mode = True

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill("orange")

        self.magic_balls = pg.sprite.Group()

        self.charge_mode = False

        self.attack_mode = False
        self.attack_interval = 500

        self.health = 100

    def load_animations(self):
        self.idle_animation_right = [
            load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH,
                       CHARACTER_HEIGHT) for i in range(1, 4)]

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in
                                    self.idle_animation_right]

        self.move_animation_right = [load_image(f"images/{self.folder}/move{i}.png",
                                                CHARACTER_WIDTH, CHARACTER_HEIGHT) for i in range(1, 5)]

        self.move_animation_left = [
            pg.transform.flip(move_image, True, False) for move_image in self.move_animation_right]
        self.charge = [load_image(f"images/{self.folder}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.charge.append(pg.transform.flip(self.charge[0], True, False))

        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

        self.down = [load_image(f"images/{self.folder}/down.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.down.append(pg.transform.flip(self.down[0], True, False))

    def update(self, gesture):
        direction = 0
        keys = pg.key.get_pressed()  # Получение всех нажатых в данный момент кнопок
        if keys[self.key_left]:
            direction = -1
            self.side = "left"
            if self.image == self.down[self.side != "right"]:
                direction = -1 * 0.5
        elif keys[self.key_right]:
            direction = 1
            self.side = "right"
            if self.image == self.down[self.side != "right"]:
                direction = 1 * 0.5

        self.handle_attack_mode()
        self.handle_movement(direction, keys, gesture)
        self.handle_animation()

    def handle_attack_mode(self):
        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.animation_mode = False
                self.timer = pg.time.get_ticks()

    def handle_animation(self):
        if not self.charge_mode and self.charge_mode > 0:
            self.attack = True
        if self.animation_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()
        if self.charge_mode:
            self.charge_power += 1
            self.charge_indicator = pg.Surface((self.charge_power, 10))
            self.charge_indicator.fill("orange")

        if self.animation_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.magic_balls.add(MagicBall(fireball_position, self.side, self.charge_power, self.folder))
            self.charge_power = 0
            self.charge_mode = False
            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()

    def handle_movement(self, direction, keys, gesture):
        if self.attack_mode:
            return
        if direction != 0:
            self.animation_mode = True
            self.charge_mode = False
            self.rect.centerx += direction * 2
            self.current_animation = self.move_animation_left if direction == -1 else self.move_animation_right
        elif (GESTURE_MODE and gesture == "fist") or (not GESTURE_MODE and keys[self.key_charge]):
            self.animation_mode = False
            self.image = self.charge[self.side != "right"]
            self.charge_mode = True

        else:
            self.current_animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right
            self.animation_mode = True
            self.charge_mode = False

        if keys[self.key_down]:
            self.animation_mode = False
            self.charge_mode = False
            self.image = self
            self.image = self.down[self.side != "right"]

        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0


class Menu:
    def __init__(self):
        self.surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pg.font.SysFont("arial", 40)
        pygame_menu.themes.THEME_SOLARIZED.widget_font = self.font
        self.menu = pygame_menu.Menu(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            theme=pygame_menu.themes.THEME_BLUE,  # тема
            title="Menu"
        )

        self.menu.add.label("Режим на одного")

        self.menu.add.selector("Противник: ", [("Маг молний", 1), ("Маг земли", 2), ("Случайный", 3)],
                               onchange=self.set_enemy)

        self.menu.add.button("Играть", self.start_one_player_game)

        self.menu.add.label("Режим на двоих (управление жестами не поддерживается)")

        self.menu.add.selector("Левый игрок: ", [("Маг молний", 1), ("Маг земли", 2), ("Маг огня", 3)],
                               onchange=self.set_left_player)
        self.menu.add.selector("Правый игрок: ", [("Маг молний", 1), ("Маг земли", 2), ("Маг огня", 3)],
                               onchange=self.set_right_player)

        self.menu.add.button("Играть", self.start_two_player_game)

        self.menu.add.button("Выход", quit)

        self.enemies = ["lightning wizard", "earth monk"]
        self.enemy = self.enemies[0]

        # Эти три строки — новые. Они нужны для хранения информации, кто за кого играет
        self.players = ["lightning wizard", "earth monk", "fire wizard"]
        self.left_player = self.players[0]
        self.right_player = self.players[0]

        self.run()

    def set_enemy(self, selected, value):
        if value in (1, 2):
            self.enemy = self.enemies[value - 1]
        else:
            self.enemy = random.choice(self.enemies)

    def set_left_player(self, selected, value):
        self.left_player = self.players[value - 1]

    def set_right_player(self, selected, value):
        self.right_player = self.players[value - 1]

    def start_one_player_game(self):
        Game("one player", (self.enemy,))

    def start_two_player_game(self):
        Game("two players", (self.left_player, self.right_player))

    def start_game(self):
        Game(self.enemy)

    def run(self):
        self.menu.mainloop(self.surface)


class Game:
    def __init__(self, mode, wizards):
        self.mode = mode
        # Создание окна
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Битва магов")
        if self.mode == "one player":
            self.player = Player()
            self.enemy = Enemy(wizards[0])
        elif self.mode == "two players":
            self.player = Player(wizards[0])
            self.enemy = Player(wizards[1], first_player=False)

        self.foreground = load_image("images/foreground.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.win = None

        self.gesture = None
        global GESTURE_MODE

        if GESTURE_MODE:
            # print("Загрузка модуля жестов")
            self.g = Gesture()
            # print("Загрузка завершена")

            self.GET_GESTURE = pg.USEREVENT + 1
            pg.time.set_timer(self.GET_GESTURE, 1000)

        else:
            GESTURE_MODE = False

        self.clock = pg.time.Clock()
        self.run()

    def run(self):
        while True:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    exit()
            if GESTURE_MODE:
                if event.type == self.GET_GESTURE:
                    self.gesture = self.g.get_gesture()
            if event.type == pg.KEYDOWN and self.win is not None:
                if event.key == pg.K_SPACE:
                   Menu()


    def update(self):
        if self.win is None:
            self.player.update(self.gesture)
            self.player.magic_balls.update()
            self.enemy.update(self.player)
            self.enemy.magic_balls.update()
            if self.mode == "one player" or self.enemy.image not in self.enemy.down:
               hits = pg.sprite.spritecollide(self.enemy, self.player.magic_balls, True,
                                           pg.sprite.collide_rect_ratio(0.6))
               for hit in hits:
                    self.enemy.health -= 15

            if self.player.image not in self.player.down:
                enemy_hits = pg.sprite.spritecollide(self.player, self.enemy.magic_balls, True,
                                                 pg.sprite.collide_rect_ratio(0.6))

                for hit in enemy_hits:
                    self.player.health -= 20
            if self.player.health <= 0:
                self.win = self.enemy
            elif self.enemy.health <= 0:
                self.win = self.enemy

    def draw(self):
        # Отрисовка интерфейса
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.player.image, self.player.rect)
        self.screen.blit(self.enemy.image, self.enemy.rect)
        self.screen.blit(self.foreground, (0, 0))
        if self.player.charge_mode:
            self.screen.blit(self.player.charge_indicator,
                             (self.player.rect.left + 120, self.player.rect.top))
        if self.mode == "two players":
            if self.enemy.charge_mode:
                self.screen.blit(self.enemy.charge_indicator,
                                 (self.enemy.rect.left + 120, self.enemy.rect.top))
        self.screen.blit(text_render(self.gesture), (0, 0))
        self.player.magic_balls.draw(self.screen)
        self.enemy.magic_balls.draw(self.screen)
        pg.draw.rect(self.screen, "green", (5, 5, self.player.health * 3, 15))
        pg.draw.rect(self.screen, "green", (SCREEN_WIDTH - 305, 5, self.enemy.health * 3, 15))
        if self.win == self.player:
            text = text_render("ПОБЕДА ИГРОКА СПРАВАа \n "
                               "НАЖМИТЕ SPACE ЧТОБЫ ВЫЙТИ")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            # text2 = text_render("...")
            # text_rect2 = text2.get_rect(center=(...))
            # self.screen.blit(text2, text_rect2)

        elif self.win == self.enemy:
            text = text_render("ПОБЕДА ИГРОКА СЛЕВА \n "
                               "НАЖМИТЕ SPACE ЧТОБЫ ВЫЙТИ")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            # text2 = text_render("ПОРАЖЕНИЕ")
            # text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
            # self.screen.blit(text2, text_rect2)

        pg.display.flip()


if __name__ == "__main__":
    Menu()
