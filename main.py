import pygame
from pygame import font
import random
from laser import collide,Laser
from ship import Ship
from constants import WIN,SPACESHIP,BULLET,BACKGROUND,\
                      HEIGHT,WIDTH,ENEMY_SHIP,ENEMY_BULLET
from pygame import K_LEFT,K_RIGHT,K_UP,K_DOWN,\
                   K_a,K_w,K_d,K_s,K_SPACE,QUIT
from pygame.display import update
from pygame.font import SysFont
from pygame.time import Clock
from pygame.mask import from_surface
from pygame.key import get_pressed
from pygame.event import get
font.init()

class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.img,self.laser_img,self.max_health = SPACESHIP,BULLET,health
        self.mask = from_surface(self.img)
        self.v = 5

    def move(self ,keys) -> None:
        if (keys[K_a]^keys[K_LEFT]) and (self.x - self.v>0):
            self.x -= self.v
        if (keys[K_d]^keys[K_RIGHT]) and (self.x + self.v + self.get_width()< WIDTH):
            self.x += self.v
        if (keys[K_w]^keys[K_UP]) and (self.y - self.v >0):
            self.y -= self.v
        if (keys[K_s]^keys[K_DOWN]) and (self.y + self.v + self.get_height()< HEIGHT):
            self.y += self.v

    def move_lasers(self, vel, objs) -> None:
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

class Enemy(Ship):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.img = ENEMY_SHIP
        self.laser_img = ENEMY_BULLET
        self.mask = from_surface(self.img)

    def move(self,velocity):
        self.y += velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def main() -> None:
    run,FPS = True,60
    LEVEL,LIVES,FONT,CLOCK = 1,5,SysFont("comicsans",50),Clock()
    player = Player(300,650)
    player_vel = 5
    bgy,bgy2 = 0.0,-float(BACKGROUND.get_height())
    enemies = []
    wave_length,enemy_vel,laser_vel = 5,1,5
    def update_window() -> None:
        WIN.blit(BACKGROUND,(0,bgy))
        WIN.blit(BACKGROUND,(0,bgy2))
        level_label = FONT.render(f"Level: {LEVEL}",True,(255,255,255))
        lives_label = FONT.render(f"Lives: {LIVES}",True,(255,255,255))
        WIN.blit(lives_label,(10,10))
        for enemy in enemies:
            enemy.draw(WIN)
        WIN.blit(level_label,(WIDTH - level_label.get_width()-10,10))
        player.draw(WIN)
        update()
    while run:
        CLOCK.tick(FPS)
        update_window()
        if len(enemies) == 0:
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100),)
                enemies.append(enemy)
        bgy += 1.4
        bgy2 += 1.4
        if bgy>HEIGHT:
            bgy=-BACKGROUND.get_height()
        if bgy2>HEIGHT:
            bgy2=-BACKGROUND.get_height()
        for event in get():
            if event.type == QUIT:
                run = False
        keys = get_pressed()
        player.move(keys)
        if keys[K_SPACE]:
            player.shoot()
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)
        player.move_lasers(-6,enemies)
if __name__ == '__main__':
    main()