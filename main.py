from tkinter import Tk, Canvas, PhotoImage, Label
from random import randint
from math import sqrt


root = Tk()


class Window:
    def __init__(self,height,width):
        # window size
        self.height = height
        self.width = width
        self.midheight = self.height / 2
        self.midwidth = self.width / 2
        # boundaries to prevent nodes from going off screen
        self.top_boundary = 2
        self.left_boundary = 2
        # canvas
        self.game = Canvas(root, height=self.height, width=self.width)
        self.game.pack()
        # map
        self.background = PhotoImage(file='./maps/zombie_city.png')
        self.game.create_image(0, 0, image=self.background, anchor='nw')
window = Window(800,1280)


class Node:
    def __init__(self, start_x, start_y, diameter, color, speed):
        # size
        self.diameter = diameter
        self.radius = self.diameter / 2
        # speed
        self.speed = speed
        self.diagonal_speed = sqrt(self.speed**2 / 2)
        # color
        self.color = color
        # center
        self.center_x = start_x; self.center_y = start_y
        # health
        self.health = HealthBar(self)
        self.alive = True
        # tkinter shape initialization
        self.shape = window.game.create_oval(start_x-self.radius, start_y-self.radius,
        start_x+self.radius, start_y+self.radius, fill=self.color)
        # x1,y1,x2,x2 positions
        self.x1,self.y1,self.x2,self.y2 = window.game.coords(self.shape)
    def draw(self):
        self.boundary_check()
        self.update()
        window.game.coords(self.shape,self.x1,self.y1,self.x2,self.y2)
        self.health.draw()
        if self.weapon != False: self.weapon.draw()
    def boundary_check(self): 
        if self.center_y - self.radius < window.top_boundary:
            self.center_y = window.top_boundary + self.radius
        elif self.center_y + self.radius > window.height:
            self.center_y = window.height - self.radius
        if self.center_x - self.radius < window.left_boundary:
            self.center_x = window.left_boundary + self.radius
        elif self.center_x + self.radius > window.width:
            self.center_x = window.width - self.radius
    def update(self): # takes a center (x,y) and updates x1,x2,y1,x2
        self.x1 = self.center_x - self.radius
        self.x2 = self.center_x + self.radius
        self.y1 = self.center_y - self.radius
        self.y2 = self.center_y + self.radius
    def distance(self, other): # returns distance from self's center to other node's center
        return sqrt((self.center_x - other.center_x)**2 + (self.center_y - other.center_y)**2)


class HealthBar:
    def __init__(self, ent):
        # the entity healthbar is associated with
        self.ent = ent
        # name shortening for convienence
        self.ent_x = self.ent.center_x; self.ent_y = self.ent.center_y; self.ent_r = self.ent.radius
        # entity health stats
        self.hp_max = self.ent_r * 3
        self.hp = self.hp_max
        # tkinter shape initialization
        self.shape = window.game.create_rectangle(self.ent_x-self.ent_r, self.ent_y - self.ent_r - 7,
                                    self.ent_x+self.ent_r, self.ent_y-self.ent_r - 3, fill='red')
    def update_pos(self): # updates entity's x and y
        self.ent_x = self.ent.center_x; self.ent_y = self.ent.center_y 
    def draw(self): # updates position of healthbar on screen
        self.update_pos()
        ratio = self.hp / self.hp_max
        lenOut = (ratio * self.ent_r)
        if lenOut > 0:
            window.game.coords(self.shape,self.ent_x-lenOut, self.ent_y - self.ent_r - 7,
                    self.ent_x+lenOut, self.ent_y-self.ent_r - 3)
        else:
            self.ent.alive = False
            window.game.delete(self.shape)


class Pistol:
    def __init__(self, ent):
        self.ent = ent
        self.width = 8
        self.length = 17
        self.dmg = 7
        self.ent_x = self.ent.center_x; self.ent_y = self.ent.center_y; self.ent_r = self.ent.radius; self.ent_ld = self.ent.look_direction
        self.shape = window.game.create_rectangle(self.ent_x - self.width/2, self.ent_y - self.ent_r - self.length, 
                                            self.ent_x + self.width/2, self.ent_y - self.ent_r, fill='silver')
    def update_pos(self):
        self.ent_x = self.ent.center_x; self.ent_y = self.ent.center_y; self.ent_r = self.ent.radius;  self.ent_ld = self.ent.look_direction
    def draw(self):
        self.update_pos()
        if not self.ent.alive:
            window.game.delete(self.shape)
            return
        elif self.ent_ld == 'w':
            window.game.coords(self.shape, self.ent_x - self.width/2, self.ent_y - self.ent_r - self.length, 
                                self.ent_x + self.width/2, self.ent_y - self.ent_r)
        elif self.ent_ld == 'a':
            window.game.coords(self.shape, self.ent_x - self.ent_r - self.length, self.ent_y + self.width/2, 
                                self.ent_x - self.ent_r, self.ent_y - self.width/2)
        elif self.ent_ld == 's':
            window.game.coords(self.shape, self.ent_x - self.width/2, self.ent_y + self.ent_r, 
                                self.ent_x + self.width/2, self.ent_y + self.ent_r + self.length)
        elif self.ent_ld == 'd':
            window.game.coords(self.shape, self.ent_x + self.ent_r, self.ent_y + self.width/2, 
                                self.ent_x + self.ent_r + self.length, self.ent_y - self.width/2)
    def shoot(self):
        self.drawGunfire()
        for zombie in sorted(list(w.zombies), key=lambda x: x.distance(player)):
            if self.ent_ld == 'w':
                if zombie.center_y < (self.ent_y - self.ent_r - self.length) and (zombie.center_x - zombie.radius) <= self.ent_x <= (zombie.center_x + zombie.radius):
                    zombie.health.hp -= self.dmg
                    break
            elif self.ent_ld == 'a':
                if zombie.center_x < (self.ent_x - self.ent_r - self.length) and (zombie.center_y - zombie.radius) <= self.ent_y <= (zombie.center_y + zombie.radius):
                    zombie.health.hp -= self.dmg
                    break
            elif self.ent_ld == 's':
                if zombie.center_y > (self.ent_y + self.ent_r + self.length) and (zombie.center_x - zombie.radius) <= self.ent_x <= (zombie.center_x + zombie.radius):
                    zombie.health.hp -= self.dmg
                    break
            elif self.ent_ld == 'd':
                if zombie.center_x > (self.ent_x + self.ent_r + self.length) and (zombie.center_y - zombie.radius) <= self.ent_y <= (zombie.center_y + zombie.radius):
                    zombie.health.hp -= self.dmg
                    break
    def drawGunfire(self):
        if self.ent_ld == 'w':
            self.gunfire_img = PhotoImage(file='./assets/upfire.png')
            self.gunfire = window.game.create_image(self.ent_x - self.width/2, self.ent_y - self.ent_r - self.length, image=self.gunfire_img, anchor='sw')
        elif self.ent_ld == 'a':
            self.gunfire_img = PhotoImage(file='./assets/leftfire.png')
            self.gunfire = window.game.create_image(self.ent_x - self.ent_r - self.length, self.ent_y + self.width/2, image=self.gunfire_img, anchor='se')
        elif self.ent_ld == 's':
            self.gunfire_img = PhotoImage(file='./assets/downfire.png')
            self.gunfire = window.game.create_image(self.ent_x - self.width/2, self.ent_y + self.ent_r + self.length, image=self.gunfire_img, anchor='nw')
        elif self.ent_ld == 'd':
            self.gunfire_img = PhotoImage(file='./assets/rightfire.png')
            self.gunfire = window.game.create_image(self.ent_x + self.ent_r + self.length, self.ent_y - self.width/2, image=self.gunfire_img, anchor='nw')
        root.after(10, window.game.delete, self.gunfire)


class Player(Node):
    def __init__(self, start_x, start_y, diameter, color, speed):
        super().__init__(start_x,start_y,diameter,color,speed)
        self.look_direction = 'w'
        self.weapon = Pistol(self)
        self.key_presses = set()
        root.after(10, self.exist)
        root.bind('<KeyPress>', self.key_push)
        root.bind('<KeyRelease>', self.key_release)
    def key_push(self,event): 
        if event.char == ' ':
            self.weapon.shoot()
            return
        self.key_presses.add(event.keysym.lower())
    def key_release(self,event): 
        if event.char == ' ': return
        self.key_presses.remove(event.keysym.lower())
    def move(self):
        if 'w' in self.key_presses:
            self.look_direction = 'w'
        elif 'a' in self.key_presses:
            self.look_direction = 'a'
        elif 's' in self.key_presses:
            self.look_direction = 's'
        elif 'd' in self.key_presses:
            self.look_direction = 'd'
        if 'w' in self.key_presses and 'a' in self.key_presses:
            self.center_y -= self.diagonal_speed
            self.center_x -= self.diagonal_speed
        elif 'w' in self.key_presses and 'd' in self.key_presses:
            self.center_y -= self.diagonal_speed
            self.center_x += self.diagonal_speed
        elif 's' in self.key_presses and 'a' in self.key_presses:
            self.center_y += self.diagonal_speed
            self.center_x -= self.diagonal_speed
        elif 's' in self.key_presses and 'd' in self.key_presses:
            self.center_y += self.diagonal_speed
            self.center_x += self.diagonal_speed
        elif 'w' in self.key_presses:
            self.center_y -= self.speed
        elif 's' in self.key_presses:
            self.center_y += self.speed
        elif 'a' in self.key_presses:
            self.center_x -= self.speed
        elif 'd' in self.key_presses:
            self.center_x += self.speed
        self.draw()
        root.after(10,self.exist)
    def exist(self):
        if not self.alive: 
            return
        else: self.move()
player = Player(window.midwidth, window.midheight, 30, 'bisque', 2)


class Enemy(Node):
    def __init__(self, start_x, start_y, diameter, color, speed, dmg):
        super().__init__(start_x,start_y,diameter,color,speed)
        self.waypoint = None # (x,y) | None
        self.dmg = dmg
        self.weapon = False
        root.after(10,self.exist)
    def exist(self):
        if not self.alive: 
            w.deleteZombie(self)
            return
        else:
            self.move()
    def move(self):
        if self.distance(player) <= 200:
            self.waypoint = None
            self.persue()
        elif self.waypoint == None:
            self.patrol()
        if self.center_x > self.waypoint[0] and self.center_y > self.waypoint[1]:
            self.center_x -= self.diagonal_speed
            self.center_y -= self.diagonal_speed
        elif self.center_x > self.waypoint[0] and self.center_y < self.waypoint[1]:
            self.center_x -= self.diagonal_speed
            self.center_y += self.diagonal_speed
        elif self.center_x < self.waypoint[0] and self.center_y > self.waypoint[1]:
            self.center_x += self.diagonal_speed
            self.center_y -= self.diagonal_speed
        elif self.center_x < self.waypoint[0] and self.center_y < self.waypoint[1]:
            self.center_x += self.diagonal_speed
            self.center_y += self.diagonal_speed
        elif self.center_x > self.waypoint[0]:
            self.center_x -= self.diagonal_speed
        elif self.center_x < self.waypoint[0]:
            self.center_x += self.diagonal_speed
        elif self.center_y > self.waypoint[1]:
            self.center_y -= self.diagonal_speed
        elif self.center_y < self.waypoint[1]:
            self.center_y += self.diagonal_speed
        if self.distance(player) <= (self.radius + player.radius):
            player.health.hp -= self.dmg
        self.draw()
        self.check_waypoint()
        root.after(10, self.exist)
    def persue(self):
        self.waypoint = (player.center_x, player.center_y)
    def patrol(self):
        new_x, new_y = randint(-200,200) + self.center_x, randint(-200,200) + self.center_y
        if new_x > window.width: new_x = window.width
        elif new_x < window.left_boundary: new_x = window.left_boundary
        if new_y > window.height: new_y = window.height
        elif new_y < window.top_boundary: new_y = window.top_boundary
        self.waypoint = (new_x,new_y)
    def check_waypoint(self):
        if abs(self.center_x - self.waypoint[0]) <= self.radius and abs(self.center_y - self.waypoint[1]) <= self.radius:
            self.waypoint = None


class Zombie(Enemy):
    def __init__(self, start_x, start_y, diameter, color, speed, dmg):
        super().__init__(start_x, start_y, diameter, color, speed, dmg)
        self.merged = False
    def check_Zcollision(self):
        for zombie in w.zombies:
            if self.distance(zombie) <= self.radius and zombie != self and type(self) == Zombie and type(zombie) == Zombie:
                return zombie
        return False
    def formHorde(self,other):
        # horde attributes
        if not self.merged:
            start_x = (self.center_x + other.center_x) / 2
            start_y = (self.center_y + other.center_y) / 2
            area = (3.14 * (self.radius**2)) + (3.14 * (other.radius)**2)
            diameter = sqrt((area / 3.14)) * 2
            speed = self.speed * 1.25
            damage = self.dmg + other.dmg
            # # create horde
            h = Horde(start_x, start_y, diameter, 'black', speed, damage)
            w.addZombie(h)
        # remove zombies
        self.merged = True; self.alive = False; self.other=False
    def move(self):
        super().move()
        collision = self.check_Zcollision()
        if collision:
            collision.merged = True
            self.formHorde(collision)


class Horde(Enemy):
    def __init__(self, start_x, start_y, diameter, color, speed, dmg):
        super().__init__(start_x, start_y, diameter, color, speed, dmg)
        self.zombies = 2
        self.label = Label(root, text=f'{self.zombies}', background='black', foreground='white', font=('Arial', 15, 'bold'))
        self.label.place(x=self.center_x, y=self.center_y, anchor='center')
    def absorb(self,zombie): # when horde collides with zombie
        pass
    def update(self): # updates horde
        super().update()
        self.label.place(x=self.center_x, y=self.center_y, anchor='center')
    def collide(self,horde): # when two hordes collide
        pass
    def bleed(self): # random chance for zombie to escape horde
        pass


class Wave():
    def __init__(self,level):
        self.zombies = set()
        for i in range(level * 3):
            x_start, y_start = randint(0, window.width), randint(0, window.height)
            zombie = Zombie(x_start,y_start,30,'green',.75,1)
            self.zombies.add(zombie)
    def addZombie(self,zombie):
        self.zombies.add(zombie)
    def deleteZombie(self,zombie):
        try:
            zombie.label.destroy()
        finally:
            window.game.delete(zombie.shape)
            window.game.delete(zombie.health.shape)
            self.zombies.remove(zombie)
w = Wave(3)


class Game():
    pass


root.mainloop()