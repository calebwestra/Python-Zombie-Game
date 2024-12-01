from tkinter import *
from random import choice
from math import sqrt
from time import sleep

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
        # attributes
        self.diameter = diameter
        self.radius = self.diameter / 2
        self.speed = speed
        self.diagonal_speed = sqrt(self.speed**2 / 2)
        self.color = color
        # tkinter shape
        self.shape = window.game.create_oval(start_x-self.radius, start_y-self.radius,
        start_x+self.radius, start_y+self.radius, fill=self.color)
        # updating variables
        self.x1,self.y1,self.x2,self.y2 = window.game.coords(self.shape)
        self.center_x = start_x; self.center_y = start_y
    def draw(self):
        window.game.coords(self.shape,self.x1,self.y1,self.x2,self.y2)
    def distance(self, other):
        return sqrt((self.center_x - other.center_x)**2 + (self.center_y - other.center_y)**2)

class Player(Node):
    def __init__(self, start_x, start_y, diameter, color, speed):
        super().__init__(start_x,start_y,diameter,color,speed)
        # async operations
        self.key_presses = set()
        root.bind('<KeyPress>', self.key_push)
        root.bind('<KeyRelease>', self.key_release)
    def key_push(self,event): 
        self.key_presses.add(event.keysym)
    def key_release(self,event): 
        self.key_presses.remove(event.keysym)
    def move(self):
        if 'w' in self.key_presses and 'a' in self.key_presses:
            self.y1 -= self.diagonal_speed
            self.y2 -= self.diagonal_speed
            self.x1 -= self.diagonal_speed
            self.x2 -= self.diagonal_speed
        elif 'w' in self.key_presses and 'd' in self.key_presses:
            self.y1 -= self.diagonal_speed
            self.y2 -= self.diagonal_speed
            self.x1 += self.diagonal_speed
            self.x2 += self.diagonal_speed
        elif 's' in self.key_presses and 'a' in self.key_presses:
            self.y1 += self.diagonal_speed
            self.y2 += self.diagonal_speed
            self.x1 -= self.diagonal_speed
            self.x2 -= self.diagonal_speed
        elif 's' in self.key_presses and 'd' in self.key_presses:
            self.y1 += self.diagonal_speed
            self.y2 += self.diagonal_speed
            self.x1 += self.diagonal_speed
            self.x2 += self.diagonal_speed
        elif 'w' in self.key_presses:
            self.y1 -= self.speed
            self.y2 -= self.speed
        elif 's' in self.key_presses:
            self.y1 += self.speed
            self.y2 += self.speed
        elif 'a' in self.key_presses:
            self.x1 -= self.speed
            self.x2 -= self.speed
        elif 'd' in self.key_presses:
            self.x1 += self.speed
            self.x2 += self.speed
        # keep movement in boundary
        if self.y1 < window.top_boundary:
            self.y1 = window.top_boundary
            self.y2 = window.top_boundary + self.diameter
        elif self.y2 > window.height:
            self.y1 = window.height - self.diameter
            self.y2 = window.height
        if self.x1 < window.left_boundary:
            self.x1 = window.left_boundary
            self.x2 = window.left_boundary + self.diameter
        elif self.x2 > window.width:
            self.x1 = window.width - self.diameter
            self.x2 = window.width
        # update shape and set after
        self.center_x = (self.x2+self.x1)/2; self.center_y = (self.y2 + self.y1) / 2
        self.draw()
        root.after(10,self.move)

player = Player(window.midwidth, window.midheight, 30, 'bisque', 2)


class Zombie(Node):
    def __init__(self, start_x, start_y, diameter, color, speed):
        super().__init__(start_x,start_y,diameter,color,speed)
    def move(self):
        if self.distance(player) < 200:
            self.persue()
        self.center_x = (self.x2+self.x1)/2; self.center_y = (self.y2 + self.y1) / 2
        root.after(10,self.move)
        self.draw()
    def patrol(self):
        direction = choice(['W','A','S','D','WA','WD','SA','SD'])
    def persue(self):
        if self.center_x > player.center_x:
            self.x1 -= self.speed
            self.x2 -= self.speed
        elif self.center_x < player.center_x:
            self.x1 += self.speed
            self.x2 += self.speed
        if self.center_y > player.center_y:
            self.y1 -= self.speed
            self.y2 -= self.speed
        elif self.center_y < player.center_y:
            self.y1 += self.speed
            self.y2 += self.speed


zombie = Zombie(200,320,30,'green',.75)



root.after(10,player.move)
root.after(10,zombie.move)
root.mainloop()