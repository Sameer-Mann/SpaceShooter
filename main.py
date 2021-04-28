import pygame
from pygame import font,mixer
from random import randint
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
pygame.init()
font.init()
pygame.mixer.init()
bulletSound = mixer.Sound("assets/laser.wav")
explosion = pygame.mixer.Sound("assets/explosion.wav")
def collide(obj1, obj2) -> bool:
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    collision = obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
    if collision:
        explosion.play()
    return collision

class Laser:
    def __init__(self,x,y,img):
        self.x,self.y,self.img = x,y,img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window) -> None:
        window.blit(self.img,(self.x,self.y))

    def move(self,vel) -> None:
        self.y += vel

    def off_screen(self) -> bool:
        return not(self.y <= HEIGHT and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 5
    def __init__(self,x,y):
        self.x,self.y=x,y
        self.lasers,self.img = [],None
        self.cool_down_counter = 0

    def draw(self,window) -> None:
        window.blit(self.img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def get_width(self) -> int:
        return self.img.get_width()

    def get_height(self) -> int:
        return self.img.get_height()

    def cooldown(self) -> None:
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

class Player(Ship):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.img,self.laser_img,self.score = SPACESHIP,BULLET,0
        self.mask = from_surface(self.img)
        self.v = 7

    def move(self ,keys) -> None:
        if keys[K_LEFT] and (self.x - self.v>0):
            self.x -= self.v
        if keys[K_RIGHT] and (self.x + self.v + self.get_width()< WIDTH):
            self.x += self.v
        if keys[K_UP] and (self.y - self.v >0):
            self.y -= self.v
        if keys[K_DOWN] and (self.y + self.v + self.get_height()< HEIGHT):
            self.y += self.v

    def shoot(self) -> None:
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 28, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, objs) -> None:
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        explosion.play()
                        objs.remove(obj)
                        self.score += 1
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

    def shoot(self,lasers):
        self.cooldown()
        if self.cool_down_counter == 0:
            lasers.append(Laser(self.x+10, self.y, self.laser_img))
            self.cool_down_counter = 1

    def off_screen(self) -> bool:
        return self.y + self.get_height() > HEIGHT

def move_lasers(vel:int,pl:Player,lasers: list,lives: int) -> int:
    v = lives
    for laser in lasers[:]:
        laser.move(vel)
        if laser.off_screen():
            lasers.remove(laser)
        elif laser.collision(pl):
            lives -= 1
            lasers.remove(laser)
            break
    if lives<v:
        for laser in lasers[:]:
            lasers.remove(laser)
    return lives

def spawn(count):
    enemies = []
    for _ in range(count):
        x,y = randint(60,WIDTH),randint(-200,0)
        enemy = Enemy(x,y)
        fl = True
        while fl:
            fl = False
            for obj in enemies[:]:
                if collide(obj,enemy):
                    fl = True
                    break
            if fl:
                x,y = randint(0,WIDTH),randint(-200,0)
                enemy.x,enemy.y = x,y
        enemies.append(enemy)
    return enemies
def main() -> None:
    run,FPS = True,60
    LIVES,FONT,CLOCK = 5,SysFont("comicsans",50),Clock()
    player = Player(300,650)
    player_vel = 5
    bgy,bgy2 = 0.0,-float(BACKGROUND.get_height())
    enemies,enemy_lasers = [],[]
    wave_length,enemy_vel,laser_vel = 5,1,5
    mixer.music.load("assets/background.wav")
    mixer.music.play(-1)
    def update_window() -> None:
        WIN.blit(BACKGROUND,(0,bgy))
        WIN.blit(BACKGROUND,(0,bgy2))
        level_label = FONT.render(f"Score: {player.score}",True,(255,255,255))
        lives_label = FONT.render(f"Lives: {LIVES}",True,(255,255,255))
        WIN.blit(lives_label,(10,10))
        for enemy in enemies:
            enemy.draw(WIN)
        for laser in enemy_lasers:
            laser.draw(WIN)
        WIN.blit(level_label,(WIDTH - level_label.get_width()-10,10))
        player.draw(WIN)
        update()
    while run:
        CLOCK.tick(FPS)
        update_window()
        if len(enemies) == 0:
            wave_length += 1
            enemies.extend(spawn(wave_length))
        bgy += 1.4;bgy2 += 1.4
        if bgy>HEIGHT:
            bgy = -BACKGROUND.get_height()
        if bgy2>HEIGHT:
            bgy2 = -BACKGROUND.get_height()
        for event in get():
            if event.type == QUIT:
                quit()
        keys = get_pressed()
        if len(keys):
            player.move(keys)
        if keys[K_SPACE]:
            bulletSound.play()
            player.shoot()
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            if randint(0, 2*30) == 1 and enemy.y>0:
                enemy.shoot(enemy_lasers)
            if collide(enemy, player):
                enemies.remove(enemy)
                LIVES -= 1
            elif enemy.off_screen():
                enemies.remove(enemy)
        LIVES = move_lasers(laser_vel,player,enemy_lasers,LIVES)
        if LIVES<=0:
            quit()
        player.move_lasers(-8,enemies)

def menu():
    titleFont = font.SysFont("comicsans",70)
    run = True
    while run:
        WIN.blit(BACKGROUND,(0,0))
        titleLabel = titleFont.render("Press Spacebar to Begin...",1,(255,255,255))
        WIN.blit(titleLabel,(WIDTH//2 - titleLabel.get_width()//2,HEIGHT//2))
        pygame.display.update()
        for event in get():
            if event.type == pygame.QUIT:
                run = False
                break
            keys = get_pressed()
            if keys[K_SPACE]:
                main()
    pygame.quit()
if __name__ == '__main__':
    menu()