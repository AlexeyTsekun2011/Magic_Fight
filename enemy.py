import pygame as pg
import random
from constants import *
from utils import *
from magicball import *


class Enemy(pg.sprite.Sprite):
    def __init__(self, folder):
        super().__init__()

        self.folder = folder
        self.load_animations()

        self.image = self.idle_animation_right[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_left

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 1.8)

        self.timer = pg.time.get_ticks()
        self.timer_2 = pg.time.get_ticks()

        self.animation_timer = pg.time.get_ticks()
        self.interval = 300
        self.side = "left"
        self.animation_mode = True

        self.magic_balls = pg.sprite.Group()

        self.attack_mode = False
        self.attack_interval = 500

        self.move_interval = 800
        self.move_duration = 0
        self.direction = 0
        self.move_timer = pg.time.get_ticks()

        self.charge_power = 0

        self.attack_mode_chance = 1

        self.health = 100

    def load_animations(self):
        self.idle_animation_right = [load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 4)]

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = [load_image(f"images/{self.folder}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 5)]

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

    def update(self, player):
        self.handle_attack_mode(player)
        self.handle_movement()
        self.handle_animation()

    def handle_attack_mode(self, player):
        if not self.attack_mode:
            if player.charge_mode:
                self.attack_mode_chance += 1
            if random.randint(0, 300) <= self.attack_mode_chance:
                self.attack_mode = True
                self.charge_power = random.randint(1,100)
                self.animation_mode = False
                if player.rect.x < self.rect.x:
                    self.side = "left"
                    self.image = self.attack[1]
                else:
                    self.side = "right"
                    self.image = self.attack[0]
        if self.attack_mode:
            print(self.timer_2)
            if pg.time.get_ticks() - self.timer_2 > self.attack_interval:
                self.attack_mode = False
                self.attack_mode_chance = 1
                self.timer_2 = pg.time.get_ticks()

    def handle_movement(self):
        if self.attack_mode:
            return

        now = pg.time.get_ticks()  # взять количество тиков

        if now - self.move_timer < self.move_duration:
            # включить режим анимации
            self.animation_mode = True
            # подвинуть по X координате на direction
            self.rect.centerx += self.direction * 2
            self.current_animation = self.move_animation_left if self.direction == -1 else self.move_animation_right
        else:
            if random.randint(1, 100) == 1 and now - self.move_timer > self.move_interval:
                self.move_timer = pg.time.get_ticks()
                self.move_duration = random.randint(400,1500)  # случайное число от 400 до 1500
                self.direction = random.choice([-1, 1])
            else:
                # включить режим анимации
                self.current_animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right
                self.animation_mode = True

        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0


    def handle_animation(self):
        if self.animation_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()


        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.magic_balls.add(MagicBall(fireball_position, self.side, self.charge_power, self.folder))
            self.charge_power = 0
            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()
