from tkinter import Tk, Canvas, PhotoImage, Label
from random import randint
from math import sqrt


root = Tk()


class Window:
    def __init__(self,height,width):
        # window size
        self.height = height
        self.width = width
        # the top and left edges of the canvas have a boundary of 2, which prevents nodes from going off screen
        self.left_top_boundary = 2
        # canvas
        self.game = Canvas(root, height=self.height, width=self.width)
        self.game.pack()
        # map image
        self.map = PhotoImage(file='./maps/zombie_city.png')
        self.game.create_image(0, 0, image=self.map, anchor='nw')
        # map boundaries
        self.boundaries = []
        self.danger_zones = []
        with open('./maps/zombie_city.dat', "r") as file:
            for line in file:
                # print(line)
                obj_type, x1, y2, x2, y1 = line.rstrip().split(' ')
                # top_left_corner = (x1, y2)
                # top_right_corner = (x2, y2)
                # bottom_left_corner = (x1, y1)
                # bottom_right_corner = (x2, y1)
                x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
                obj = (x1, x2, y1, y2)
                if obj_type == 'boundary': self.boundaries.append(obj)
                elif obj_type == 'danger_zone': self.danger_zones.append(obj)
window = Window(800,1280)

class Node:
    def __init__(self, start_x, start_y, radius, color, speed):
        # size
        self.radius = radius
        # speed
        self.speed = speed
        # see appendix 1
        self.diag_speed = sqrt(self.speed**2 / 2)
        # color
        self.color = color
        # center
        self.center_x = start_x
        self.center_y = start_y
        # health
        self.health = HealthBar(self)
        self.alive = True
        # tkinter shape initialization
        self.shape = window.game.create_oval(start_x-self.radius, start_y-self.radius,
                            start_x+self.radius, start_y+self.radius, fill=self.color)
        # x1,y1,x2,x2 positions
        self.x1, self.y1, self.x2, self.y2 = window.game.coords(self.shape)
    def boundary_check(self): # adjusts center (x,y) when outside the window
        if self.center_y - self.radius < window.left_top_boundary:
            self.center_y = window.left_top_boundary + self.radius
        elif self.center_y + self.radius > window.height:
            self.center_y = window.height - self.radius
        if self.center_x - self.radius < window.left_top_boundary:
            self.center_x = window.left_top_boundary + self.radius
        elif self.center_x + self.radius > window.width:
            self.center_x = window.width - self.radius
    def update(self): # calls boundary_check method / takes a center (x,y) and updates x1, x2, y1, x2
        self.boundary_check()
        self.x1 = self.center_x - self.radius
        self.x2 = self.center_x + self.radius
        self.y1 = self.center_y - self.radius
        self.y2 = self.center_y + self.radius
    def draw(self): # calls update method / moves the shape / calls healthbar draw method
        self.update()
        window.game.coords(self.shape, self.x1, self.y1, self.x2, self.y2)
        self.health.draw()
    def distance(self, other): # returns distance from self's center to other node's center
        return sqrt((self.center_x - other.center_x)**2 + (self.center_y - other.center_y)**2)
    def check_collision(self): # returns true if collision, otherwise, returns false
        for boundary in window.boundaries:
            x1, x2, y1, y2 = boundary
            if self.center_x + self.radius > x1 and self.center_x - self.radius < x2 and self.center_y - self.radius < y1 and self.center_y + self.radius > y2:
                return True
        return False

class HealthBar:
    def __init__(self, ent):
        # the entity that the healthbar is associated with
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
            self.gunfire_img = PhotoImage(file='./assets/images/upfire.png')
            self.gunfire = window.game.create_image(self.ent_x - self.width/2, self.ent_y - self.ent_r - self.length, image=self.gunfire_img, anchor='sw')
        elif self.ent_ld == 'a':
            self.gunfire_img = PhotoImage(file='./assets/images/leftfire.png')
            self.gunfire = window.game.create_image(self.ent_x - self.ent_r - self.length, self.ent_y + self.width/2, image=self.gunfire_img, anchor='se')
        elif self.ent_ld == 's':
            self.gunfire_img = PhotoImage(file='./assets/images/downfire.png')
            self.gunfire = window.game.create_image(self.ent_x - self.width/2, self.ent_y + self.ent_r + self.length, image=self.gunfire_img, anchor='nw')
        elif self.ent_ld == 'd':
            self.gunfire_img = PhotoImage(file='./assets/images/rightfire.png')
            self.gunfire = window.game.create_image(self.ent_x + self.ent_r + self.length, self.ent_y - self.width/2, image=self.gunfire_img, anchor='nw')
        root.after(10, window.game.delete, self.gunfire)


class Player(Node):
    def __init__(self, start_x, start_y, radius, color, speed):
        super().__init__(start_x,start_y,radius,color,speed)
        self.look_direction = 'w'
        self.weapon = Pistol(self)
        self.key_presses = set()
        root.after(10, self.exist)
        root.bind('<KeyPress>', self.key_push)
        root.bind('<KeyRelease>', self.key_release)
    def key_push(self,event): 
        if event.char == ' ' and self.alive == True:
            self.weapon.shoot()
            return
        self.key_presses.add(event.keysym.lower())
    def key_release(self,event): 
        if event.char == ' ': return
        self.key_presses.remove(event.keysym.lower())
    def move(self):
        self.check_danger()
        original_pos = (self.center_x, self.center_y)
        if 'w' in self.key_presses:
            self.look_direction = 'w'
        elif 'a' in self.key_presses:
            self.look_direction = 'a'
        elif 's' in self.key_presses:
            self.look_direction = 's'
        elif 'd' in self.key_presses:
            self.look_direction = 'd'
        if 'w' in self.key_presses and 'a' in self.key_presses:
            self.center_y -= self.diag_speed
            self.center_x -= self.diag_speed
        elif 'w' in self.key_presses and 'd' in self.key_presses:
            self.center_y -= self.diag_speed
            self.center_x += self.diag_speed
        elif 's' in self.key_presses and 'a' in self.key_presses:
            self.center_y += self.diag_speed
            self.center_x -= self.diag_speed
        elif 's' in self.key_presses and 'd' in self.key_presses:
            self.center_y += self.diag_speed
            self.center_x += self.diag_speed
        elif 'w' in self.key_presses:
            self.center_y -= self.speed
        elif 's' in self.key_presses:
            self.center_y += self.speed
        elif 'a' in self.key_presses:
            self.center_x -= self.speed
        elif 'd' in self.key_presses:
            self.center_x += self.speed
        if self.check_collision(): self.center_x, self.center_y = original_pos
        self.draw()
        root.after(10, self.exist)
    def exist(self):
        if not self.alive: 
            return
        else: self.move()
    def draw(self):
        super().draw()
        self.weapon.draw()
    def check_danger(self):
        for danger_zone in window.danger_zones:
            x1, x2, y1, y2 = danger_zone
            if self.center_x + self.radius > x1 and self.center_x - self.radius < x2 and self.center_y - self.radius < y1 and self.center_y + self.radius > y2:
                self.health.hp -= 0.01
player = Player(window.width/2, window.height/2, 15, 'bisque', 1)


class Enemy(Node):
    def __init__(self, start_x, start_y, radius, color, speed, dmg):
        super().__init__(start_x,start_y,radius,color,speed)
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
        original_pos = (self.center_x, self.center_y)
        if self.distance(player) <= 200 and player.alive:
            self.waypoint = None
            self.persue()
        elif self.waypoint == None:
            self.patrol()
        if self.center_x > self.waypoint[0] and self.center_y > self.waypoint[1]:
            self.center_x -= self.diag_speed
            self.center_y -= self.diag_speed
        elif self.center_x > self.waypoint[0] and self.center_y < self.waypoint[1]:
            self.center_x -= self.diag_speed
            self.center_y += self.diag_speed
        elif self.center_x < self.waypoint[0] and self.center_y > self.waypoint[1]:
            self.center_x += self.diag_speed
            self.center_y -= self.diag_speed
        elif self.center_x < self.waypoint[0] and self.center_y < self.waypoint[1]:
            self.center_x += self.diag_speed
            self.center_y += self.diag_speed
        elif self.center_x > self.waypoint[0]:
            self.center_x -= self.diag_speed
        elif self.center_x < self.waypoint[0]:
            self.center_x += self.diag_speed
        elif self.center_y > self.waypoint[1]:
            self.center_y -= self.diag_speed
        elif self.center_y < self.waypoint[1]:
            self.center_y += self.diag_speed
        if self.distance(player) <= (self.radius + player.radius):
            player.health.hp -= self.dmg
        if self.check_collision(): self.center_x, self.center_y = original_pos
        self.draw()
        self.check_waypoint()
        root.after(10, self.exist)
    def persue(self):
        self.waypoint = (player.center_x, player.center_y)
    def patrol(self):
        new_x, new_y = randint(-200,200) + self.center_x, randint(-200,200) + self.center_y
        if new_x > window.width: new_x = window.width
        elif new_x < window.left_top_boundary: new_x = window.left_top_boundary
        if new_y > window.height: new_y = window.height
        elif new_y < window.left_top_boundary: new_y = window.left_top_boundary
        self.waypoint = (new_x,new_y)
    def check_waypoint(self):
        if abs(self.center_x - self.waypoint[0]) <= self.radius and abs(self.center_y - self.waypoint[1]) <= self.radius:
            self.waypoint = None


class Zombie(Enemy):
    def __init__(self, start_x, start_y, radius, color, speed, dmg):
        super().__init__(start_x, start_y, radius, color, speed, dmg)
    def formHorde(self):
        for zombie in list(filter(lambda x: self.distance(x) < self.radius * 2, w.zombies)):
            if self.distance(zombie) <= self.radius and zombie != self and type(zombie) == Zombie and zombie.alive and self.alive:
                self.alive = False; zombie.alive = False
                start_x = (self.center_x + zombie.center_x) / 2
                start_y = (self.center_y + zombie.center_y) / 2
                radius = (sqrt(2) * 15)
                # create horde
                h = Horde(start_x, start_y, radius, 'black', n_zombies=2)
                w.addZombie(h)
    def move(self):
        super().move()
        self.formHorde()


class Horde(Enemy):
    def __init__(self, start_x, start_y, radius, color, n_zombies, speed=0.5, dmg=1):
        super().__init__(start_x, start_y, radius, color, speed, dmg)
        self.n_zombies = n_zombies
        self.speed = 0.5 + (self.n_zombies-1) * .2
        self.dmg = self.n_zombies * .5
        self.n_zombies = n_zombies
        self.label = Label(root, text=f'{self.n_zombies}', background='black', foreground='white', font=('Arial', 15, 'bold'))
        self.label.place(x=self.center_x, y=self.center_y, anchor='center')
    def absorb(self): 
        for zombie in list(filter(lambda x: self.distance(x) < self.radius * 2, w.zombies)):
            if self.distance(zombie) <= self.radius and type(zombie) == Zombie and zombie.alive == True:
                zombie.alive = False; self.alive = False
                radius = (sqrt(self.n_zombies) * 15)
                h = Horde(self.center_x, self.center_y, radius, 'black', n_zombies=self.n_zombies + 1)
                w.addZombie(h)
            elif self.distance(zombie) <= self.radius and type(zombie) == Horde and zombie != self:
                self.alive = False; zombie.alive = False
                start_x = (self.center_x + zombie.center_x) / 2
                start_y = (self.center_y + zombie.center_y) / 2
                radius =   sqrt(self.n_zombies + zombie.n_zombies) * 15
                h = Horde(start_x, start_y, radius, 'black', n_zombies=self.n_zombies + zombie.n_zombies)
    def move(self):
        super().move()
        self.absorb()
    def update(self):
        super().update()
        try:
            self.label.destroy()
            self.label = Label(root, text=f'{self.n_zombies}', background='black', foreground='white', font=('Arial', 15, 'bold'))
            self.label.place(x=self.center_x, y=self.center_y, anchor='center')
        except: pass


class Wave():
    def __init__(self,level):
        self.zombies = set()
        for _ in range(level * 3):
            x_start, y_start = randint(0, window.width), randint(0, window.height)
            zombie = Zombie(x_start,y_start, 15, 'green', .5, 1)
            self.zombies.add(zombie)
    def addZombie(self,zombie):
        self.zombies.add(zombie)
    def deleteZombie(self,zombie):
        try:
            zombie.label.destroy()
        except:
            pass
        finally:
            window.game.delete(zombie.shape)
            window.game.delete(zombie.health.shape)
            self.zombies.remove(zombie)
w = Wave(1)


root.mainloop()