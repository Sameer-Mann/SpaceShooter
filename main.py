import pygame
import os
import time
import random
pygame.font.init()
WIDTH,HEIGHT = 800,800

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

class Ship:
    COOLDOWN = 15
    def __init__(self,x,y,health=100):
        self.x,self.y,self.health=x,y,health
        self.lasers,self.img = [],None
        self.wait_time = 0
        self.cool_down_counter = 0

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Laser:
    def __init__(self,x,y,img):
        self.x,self.y,self.img = x,y,img
        self.mask = pygame.mask.from_surface(self.img)
        # self.v = velocity

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self):
        return not(self.y <= HEIGHT and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.img = SPACESHIP
        self.laser_img = BULLET
        self.mask = pygame.mask.from_surface(self.img)
        self.max_health = health
        self.v = 5

    def move(self ,keys):
        if (keys[pygame.K_a]^keys[pygame.K_LEFT]) and (self.x - self.v>0):
            self.x -= self.v
        if (keys[pygame.K_d]^keys[pygame.K_RIGHT]) and (self.x + self.v + self.get_width()< WIDTH):
            self.x += self.v
        if (keys[pygame.K_w]^keys[pygame.K_UP]) and (self.y - self.v >0):
            self.y -= self.v
        if (keys[pygame.K_s]^keys[pygame.K_DOWN]) and (self.y + self.v + self.get_height()< HEIGHT):
            self.y += self.v

    def move_lasers(self, vel, objs=[]):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            # else:
            #     for obj in objs:
            #         if laser.collision(obj):
            #             objs.remove(obj)
            #             if laser in self.lasers:
            #                 self.lasers.remove(laser)

class Enemy(Ship):
    def __init__(self,x,y):
        super().__init__(x,y)

def main():
    run,FPS = True,60
    CLOCK = pygame.time.Clock()
    LEVEL,LIVES = 1,5
    FONT = pygame.font.SysFont("comicsans",50)
    player = Player(300,650)
    player_vel = 5;
    bgy,bgy2 = 0,-BACKGROUND.get_height()
    def update_window():
        WIN.blit(BACKGROUND,(0,bgy))
        WIN.blit(BACKGROUND,(0,bgy2))
        level_label = FONT.render(f"Level: {LEVEL}",1,(255,255,255))
        lives_label = FONT.render(f"Lives: {LIVES}",1,(255,255,255))
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH - level_label.get_width()-10,10))
        player.draw(WIN)
        pygame.display.update()

    while run:
        CLOCK.tick(FPS)
        update_window()
        bgy += 1.4
        bgy2 += 1.4
        if bgy>HEIGHT:
            bgy=-BACKGROUND.get_height()
        if bgy2>HEIGHT:
            bgy2=-BACKGROUND.get_height()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        player.move(keys)
        if keys[pygame.K_SPACE]:
            player.shoot()
        player.move_lasers(-5)
if __name__ == '__main__':
    WIN  = pygame.display.set_mode((WIDTH,HEIGHT))
    SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets/Blue","ship.png")),(128,128))
    BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets","background.png")),(WIDTH,HEIGHT))
    BULLET = pygame.image.load(os.path.join("assets/Blue","bullet.png"))
    main()