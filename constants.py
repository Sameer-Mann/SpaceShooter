from pygame.image import load
from pygame.transform import scale,rotate
from pygame.display import set_mode
WIDTH,HEIGHT = 1440,900
WIN  = set_mode((WIDTH,HEIGHT))
SPACESHIP = scale(load("./assets/Blue/ship.png"),(128,128))
BACKGROUND = scale(load("./assets/background.png"),(WIDTH,HEIGHT))
BULLET = scale(load("assets/Blue/bullet.png"),(64,64))
ENEMY_SHIP = scale(load("./assets/Red/spaceship_enemy_red.png"),(64,64))
ENEMY_BULLET = rotate(scale(load("./assets/Red/bullet_red.png"),(64,64)),180)