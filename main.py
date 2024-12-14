from tkinter import *
from random import choice, randint
from math import sqrt

root = Tk()

class Window:
    def __init__(self,height,width,color):
        # attributes
        self.height = height
        self.width = width
        self.midheight = self.height / 2
        self.midwidth = self.width / 2
        self.color = color
        # boundaries
        self.top_boundary = 2
        self.left_boundary = 2
        # tkinter
        self.game = Canvas(root, height=self.height, width=self.width, bg=self.color)
        self.game.pack()

window = Window(800,1200,'gray')

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
        # tkinter shape
        self.shape = window.game.create_oval(start_x-self.radius, start_y-self.radius,
        start_x+self.radius, start_y+self.radius, fill=self.color)
        # position
        self.x1,self.y1,self.x2,self.y2 = window.game.coords(self.shape)
    def draw(self):
        self.boundary_check()
        self.update()
        window.game.coords(self.shape,self.x1,self.y1,self.x2,self.y2)
        self.health.draw()
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
    def distance(self, other):
        return sqrt((self.center_x - other.center_x)**2 + (self.center_y - other.center_y)**2)


class HealthBar:
    def __init__(self, ent):
        self.ent = ent
        self.ent_x = self.ent.center_x; self.ent_y = self.ent.center_y; self.ent_r = self.ent.radius
        self.shape = window.game.create_rectangle(self.ent_x-self.ent_r, self.ent_y - self.ent_r - 7,
                                    self.ent_x+self.ent_r, self.ent_y-self.ent_r - 3, fill='red')
    def update_pos(self):
        self.ent_x = self.ent.center_x; self.ent_y = self.ent.center_y; self.ent_r = self.ent.radius   
    def draw(self):
        self.update_pos()
        window.game.coords(self.shape,self.ent_x-self.ent_r, self.ent_y - self.ent_r - 7,
                self.ent_x+self.ent_r, self.ent_y-self.ent_r - 3)




class Player(Node):
    def __init__(self, start_x, start_y, diameter, color, speed):
        super().__init__(start_x,start_y,diameter,color,speed)
        # async operations
        self.key_presses = set()
        root.bind('<KeyPress>', self.key_push)
        root.bind('<KeyRelease>', self.key_release)
    def key_push(self,event): 
        self.key_presses.add(event.keysym.lower())
    def key_release(self,event): 
        self.key_presses.remove(event.keysym.lower())
    def move(self):
        if not self.alive: return
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
        root.after(10,self.move)

player = Player(window.midwidth, window.midheight, 30, 'bisque', 2)


class Zombie(Node):
    def __init__(self, start_x, start_y, diameter, color, speed):
        super().__init__(start_x,start_y,diameter,color,speed)
        self.waypoint = None # (x,y) | None
    def move(self):
        if not self.alive: return
        if self.distance(player) < 200:
            self.waypoint = None
            self.persue()
        else:
            self.patrol()
        self.draw()
        root.after(10,self.move)
    def patrol(self):
        if not self.waypoint: self.create_waypoint()
        if self.center_x > self.waypoint[0]:
            self.center_x -= self.speed
        else:
            self.center_x += self.speed
        if self.center_y > self.waypoint[1]:
            self.center_y -= self.speed
        else:
            self.center_y += self.speed
        self.check_waypoint()
    def persue(self):
        if self.center_x > player.center_x:
            self.center_x -= self.speed
        elif self.center_x < player.center_x:
            self.center_x += self.speed
        if self.center_y > player.center_y:
            self.center_y -= self.speed
        elif self.center_y < player.center_y:
            self.center_y += self.speed
    def create_waypoint(self):
        new_x, new_y = randint(-200,200) + self.center_x, randint(-200,200) + self.center_y
        if new_x > window.width: new_x = window.width
        elif new_x < window.left_boundary: new_x = window.left_boundary
        if new_y > window.height: new_y = window.height
        elif new_y < window.top_boundary: new_y = window.top_boundary
        self.waypoint = (new_x,new_y)
    def check_waypoint(self):
        if abs(self.center_x - self.waypoint[0]) <= self.radius and abs(self.center_y - self.waypoint[1]) <= self.radius:
            self.waypoint = None

zombies = []
zombie_moves = []
def spawn(n_zombies):
    for i in range(n_zombies):
        x_start, y_start = randint(0, window.width), randint(0, window.height)
        zombie = Zombie(x_start,y_start,30,'green',.50)
        zombies.append(zombie)
        zombie_moves.append(root.after(10,zombie.move))
spawn(4)

root.after(10,player.move)
root.mainloop()