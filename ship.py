from laser import Laser
from constants import WIDTH,HEIGHT
class Ship:
    """A general class that contains helper functions.
    All ships player as well as enemies are derived from this"""
    COOLDOWN = 15
    def __init__(self,x,y,health=100):
        self.x,self.y,self.health=x,y,health
        self.lasers,self.img = [],None
        self.wait_time = 0
        self.cool_down_counter = 0

    def draw(self,window) -> None:
        """Redraws a ship on the window """
        window.blit(self.img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def get_width(self) -> int:
        """Returns the width of the image
        asset associated with this ship"""
        return self.img.get_width()

    def get_height(self) -> int:
        """Returns the height of the image
        asset associated with this ship"""
        return self.img.get_height()

    def cooldown(self) -> None:
        """To introduce a certain delay between consecutive shots"""
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self) -> None:
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                # obj.health -= 10
                self.lasers.remove(laser)
