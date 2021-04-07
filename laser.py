import pygame
# WIDTH,HEIGHT = 800,800
from constants import HEIGHT
class Laser:
    def __init__(self,x,y,img):
        self.x,self.y,self.img = x,y,img
        self.mask = pygame.mask.from_surface(self.img)
        # self.v = velocity

    def draw(self,window) -> None:
        """Redraws a laser on the window"""
        window.blit(self.img,(self.x,self.y))

    def move(self,vel) -> None:
        """Changes the position of a laser by velocity"""
        self.y += vel

    def off_screen(self) -> bool:
        return not(self.y <= HEIGHT and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

def collide(obj1, obj2) -> bool:
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None