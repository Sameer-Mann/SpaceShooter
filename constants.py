from pygame.image import load
from pygame.transform import scale
from pygame.display import set_mode
WIDTH,HEIGHT = 900,1000
WIN  = set_mode((WIDTH,HEIGHT))
SPACESHIP = scale(load("./assets/Blue/ship.png"),(128,128))
BACKGROUND = scale(load("./assets/background.png"),(WIDTH,HEIGHT))
BULLET = load("assets/Blue/bullet.png")
ENEMY_SHIP = scale(load("./assets/Red/spaceship_enemy_red.png"),(128,128))
ENEMY_BULLET = load("./assets/Red/bullet_red.png")