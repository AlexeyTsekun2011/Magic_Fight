import pygame as pg
from gesture import Gesture

screen = pg.display.set_mode((500, 500))

g = Gesture()

color = "red"

fps = 30
clock = pg.time.Clock()

frame = 0

while True:
    frame += 1

    if frame % 15 == 0:
        current_gesture = g.get_gesture()
        print(frame, current_gesture)

        match current_gesture:
            case "live long":
                color = "blue"
            case "rock":
                color = "green"
            case "peace":
                color = "yellow"
            case _:
                color = "red"

    screen.fill(pg.Color("white"))

    pg.draw.rect(screen, pg.Color(color), (300, 300, 100, 100), 100)

    pg.display.flip()
    clock.tick(fps)