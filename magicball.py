from utils import *
from constants import *
class MagicBall(pg.sprite.Sprite):
    def __init__(self, coord, side, power,folder):
        super().__init__()
        self.side = side
        self.power = power
        self.image = load_image(f"images/{folder}/magicball.png", 200, 150)

        if side == "right":
            self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = coord[0], coord[1] + 120

    def update(self):
        if self.side == "right":
            self.rect.x += 4
        else:
            self.rect.x -= 4
        if self.rect.x >= SCREEN_WIDTH or self.rect.right <= 0:
            self.kill()