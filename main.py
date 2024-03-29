import pygame
from pygame import font, mixer
from random import randint
from constants import WIN, SPACESHIP, BULLET, BACKGROUND,\
                      HEIGHT, WIDTH, ENEMY_SHIP, ENEMY_BULLET
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN,\
                   K_SPACE, QUIT, K_ESCAPE, KEYDOWN, K_m
from pygame.display import update
from pygame.font import SysFont
from pygame.time import Clock
from pygame.mask import from_surface
from pygame.key import get_pressed
from pygame.event import get
from pickle import dumps, loads
pygame.init()
font.init()
pygame.mixer.init()
bulletSound = mixer.Sound("assets/laser.wav")
explosion = pygame.mixer.Sound("assets/explosion.wav")
validChars = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
shiftChars = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'
shiftDown = False
isMuted = False


class TextBox(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.text = ""
        self.font = pygame.font.Font(None, 50)
        self.image = self.font.render("Enter your name", False, [255, 255, 255])
        self.rect = self.image.get_rect()

    def add_chr(self, char):
        global shiftDown
        if char in validChars and not shiftDown:
            self.text += char
        elif char in validChars and shiftDown:
            self.text += shiftChars[validChars.index(char)]
        self.update()

    def update(self):
        old_rect_pos = self.rect.center
        self.image = self.font.render(self.text, False, [255, 255, 255])
        self.rect = self.image.get_rect()
        self.rect.center = old_rect_pos


def collide(obj1, obj2) -> bool:
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    collision = obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None
    if collision:
        explosion.play()
    return collision


class Laser:
    def __init__(self, x, y, img):
        self.x, self.y, self.img = x, y, img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window) -> None:
        window.blit(self.img, (self.x, self.y))

    def move(self, vel) -> None:
        self.y += vel

    def off_screen(self) -> bool:
        return not(HEIGHT >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 5

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.lasers, self.img = [], None
        self.cool_down_counter = 0

    def draw(self, window) -> None:
        window.blit(self.img, (self.x, self.y))
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
    def __init__(self, x, y, username):
        super().__init__(x, y)
        self.img, self.laser_img, self.score = SPACESHIP, BULLET, 0
        self.mask = from_surface(self.img)
        self.username = username
        self.v = 7

    def move(self, keys) -> None:
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
        global isMuted
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
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = ENEMY_SHIP
        self.laser_img = ENEMY_BULLET
        self.mask = from_surface(self.img)

    def move(self, velocity):
        self.y += velocity

    def shoot(self, lasers):
        self.cooldown()
        if self.cool_down_counter == 0:
            lasers.append(Laser(self.x+10, self.y, self.laser_img))
            self.cool_down_counter = 1

    def off_screen(self) -> bool:
        return self.y + self.get_height() > HEIGHT


def move_lasers(vel: int, pl: Player, lasers: list, lives: int) -> int:
    v = lives
    for laser in lasers[:]:
        laser.move(vel)
        if laser.off_screen():
            lasers.remove(laser)
        elif laser.collision(pl):
            lives -= 1
            lasers.remove(laser)
            break
    if lives < v:
        for laser in lasers[:]:
            lasers.remove(laser)
    return lives


def spawn(count: int):
    enemies = []
    for _ in range(count):
        x, y = randint(60, WIDTH-120), randint(-200, 0)
        enemy = Enemy(x, y)
        fl = True
        while fl:
            fl = False
            for obj in enemies[:]:
                if collide(obj, enemy):
                    fl = True
                    break
            if fl:
                x, y = randint(60, WIDTH-120), randint(-200, 0)
                enemy.x, enemy.y = x, y
        enemies.append(enemy)
    return enemies


def main(username: str) -> int:
    global isMuted
    run, fps = True, 60
    lives, font_, clock = 5, SysFont("comicsans", 50), Clock()
    level = 0
    player = Player(300, 650, username)
    bgy, bgy2 = 0.0, -float(BACKGROUND.get_height())
    enemies, enemy_lasers = [], []
    player_laser_vel = -8
    wave_length, enemy_vel, laser_vel = 5, 1, 5
    mixer.music.load("assets/background.wav")
    mixer.music.play(-1)

    def update_window() -> None:
        WIN.blit(BACKGROUND, (0, bgy))
        WIN.blit(BACKGROUND, (0, bgy2))
        level_label = font_.render(f"Score: {player.score}", True, (255, 255, 255))
        lives_label = font_.render(f"Lives: {lives}", True, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        for enemy in enemies:
            enemy.draw(WIN)
        for laser in enemy_lasers:
            laser.draw(WIN)
        WIN.blit(level_label, (WIDTH - level_label.get_width()-10, 10))
        player.draw(WIN)
        update()

    while run:
        clock.tick(fps)
        if len(enemies) == 0:
            if level == 10:
                update_scores(player)
                return 1
            wave_length += 1
            enemies.extend(spawn(wave_length))
            level += 1
            if level % 4 == 0:
                enemy_vel += 1
                player.v += 1
                player_laser_vel -= 1
            level_label = font_.render(F"Level {level}...", True, (255, 255, 255))
            WIN.blit(level_label, (WIDTH//2 - level_label.get_width()//2, HEIGHT//2))
            update()
            pygame.time.wait(2500)
        update_window()
        bgy += 1.4
        bgy2 += 1.4
        if bgy > HEIGHT:
            bgy = -BACKGROUND.get_height()
        if bgy2 > HEIGHT:
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
        if keys[K_m]:
            isMuted = not isMuted
            if isMuted:
                mixer.music.stop()
            else:
                mixer.music.play(-1)
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            if randint(0, 2*30) == 1 and enemy.y > 0:
                enemy.shoot(enemy_lasers)
            if collide(enemy, player):
                enemies.remove(enemy)
                lives -= 1
            elif enemy.off_screen():
                enemies.remove(enemy)
                player.score -= 1
                player.score = max(player.score, 0)
        lives = move_lasers(laser_vel, player, enemy_lasers, lives)
        if lives <= 0:
            update_scores(player)
            return 1
        player.move_lasers(player_laser_vel, enemies)
    update_scores(player)
    return 1


def wait():
    while True:
        for event in get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return 1
            if event.type == KEYDOWN and event.key == K_SPACE:
                return 0


def update_scores(player):
    scores = {}
    with open("scores", "rb") as f:
        scores = loads(f.read())
    scores[player.username] = max(scores.get(player.username, 0), player.score)
    with open("scores", "wb") as f:
        f.write(dumps(scores))


def renderfont(text, size, x, y, style="comicsans") -> None:
    obj1 = font.SysFont(style, size).render(text, True, (255, 255, 255))
    WIN.blit(obj1, (x, y))


def display_scores():
    with open("scores", "rb") as f:
        scores = loads(f.read())
    a = sorted([(scores[x], x) for x in scores], reverse=True)
    WIN.blit(BACKGROUND, (0, 0))
    renderfont("Usernames", 50, 100, 50)
    renderfont("Scores", 50, 850, 50)
    y = 90
    for i in range(10):
        renderfont(str(a[i][1]), 45, 100, y)
        renderfont(str(a[i][0]), 45, 850, y)
        y += 45
    update()
    wait()


def menu():
    global shiftDown
    textbox = TextBox()
    textbox.rect.center = [320, 240]
    run = True
    username = ""
    while run:
        WIN.blit(BACKGROUND, (0, 0))
        WIN.blit(textbox.image, textbox.rect)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
            if e.type == pygame.KEYUP:
                if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                    shiftDown = False
            if e.type == pygame.KEYDOWN:
                textbox.add_chr(pygame.key.name(e.key))
                if e.key == pygame.K_SPACE:
                    textbox.text += " "
                    textbox.update()
                if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                    shiftDown = True
                if e.key == pygame.K_BACKSPACE:
                    textbox.text = textbox.text[:-1]
                    textbox.update()
                if e.key == pygame.K_RETURN:
                    if len(textbox.text) > 0:
                        username = textbox.text
                        run = False
    run = True
    titlefont = font.SysFont("comicsans", 70)
    while run:
        WIN.blit(BACKGROUND, (0, 0))
        titlelabel = titlefont.render("Press Spacebar to Begin...", True, (255, 255, 255))
        WIN.blit(titlelabel, (WIDTH//2 - titlelabel.get_width()//2, HEIGHT//2))
        update()
        for event in get():
            if event.type == pygame.QUIT:
                run = False
                break
            keys = get_pressed()
            if keys[K_SPACE]:
                if main(username) == 1:
                    WIN.blit(BACKGROUND, (0, 0))
                    titlelabel = titlefont.render("Game Over...", True, (255, 255, 255))
                    WIN.blit(titlelabel, (WIDTH//2 - titlelabel.get_width()//2, HEIGHT//2))
                    update()
                    pygame.time.wait(2000)
                    WIN.blit(BACKGROUND, (0, 0))
                    titlelabel = titlefont.render("Press Space To Restart/Escape To Quit...", True, (255, 255, 255))
                    WIN.blit(titlelabel, (WIDTH//2 - titlelabel.get_width()//2, HEIGHT//2))
                    update()
                    if wait() == 1:
                        run = False
                        break
    display_scores()
    pygame.quit()


if __name__ == '__main__':
    menu()
