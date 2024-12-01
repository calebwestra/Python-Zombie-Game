from tkinter import *

root = Tk()

class Window:
    def __init__(self):
        # independant variables
        self.height = 800
        self.width = 1200
        self.color = 'gray'
        # boundaries
        self.top_boundary = 2
        self.left_boundary = 2
        # dependant variables
        self.midheight = self.height / 2
        self.midwidth = self.width / 2
        # tkinter tops
        self.game = Canvas(root, height=self.height, width=self.width, bg=self.color)
        # tkinter placement
        self.game.pack()

window = Window()


class Player:
    def __init__(self):
        # dependant variables
        self.diameter = 30
        self.color = 'green'
        self.movement_increment = 2
        # independant variables
        self.radius = self.diameter / 2
        self.half_movement_increment = self.movement_increment / 2
        # tkinter tops
        self.shape = window.game.create_oval(window.midwidth-self.radius, window.midheight-self.radius,
        window.midwidth+self.radius, window.midheight+self.radius, fill=self.color)
        # updating variables
        self.x1,self.y1,self.x2,self.y2 = window.game.coords(self.shape)
        # async operations
        self.key_presses = set()
        root.bind('<KeyPress>', self.key_push)
        root.bind('<KeyRelease>', self.key_release)
    def draw(self): window.game.coords(self.shape,self.x1,self.y1,self.x2,self.y2)
    def key_push(self,event): self.key_presses.add(event.keysym)
    def key_release(self,event): self.key_presses.remove(event.keysym)
    def move(self):
        if 'w' in self.key_presses and 'a' in self.key_presses:
            self.y1 -= self.half_movement_increment
            self.y2 -= self.half_movement_increment
            self.x1 -= self.half_movement_increment
            self.x2 -= self.half_movement_increment
        elif 'w' in self.key_presses and 'd' in self.key_presses:
            self.y1 -= self.half_movement_increment
            self.y2 -= self.half_movement_increment
            self.x1 += self.half_movement_increment
            self.x2 += self.half_movement_increment
        elif 's' in self.key_presses and 'a' in self.key_presses:
            self.y1 += self.half_movement_increment
            self.y2 += self.half_movement_increment
            self.x1 -= self.half_movement_increment
            self.x2 -= self.half_movement_increment
        elif 's' in self.key_presses and 'd' in self.key_presses:
            self.y1 += self.half_movement_increment
            self.y2 += self.half_movement_increment
            self.x1 += self.half_movement_increment
            self.x2 += self.half_movement_increment
        elif 'w' in self.key_presses:
            self.y1 -= self.movement_increment
            self.y2 -= self.movement_increment
        elif 's' in self.key_presses:
            self.y1 += self.movement_increment
            self.y2 += self.movement_increment
        elif 'a' in self.key_presses:
            self.x1 -= self.movement_increment
            self.x2 -= self.movement_increment
        elif 'd' in self.key_presses:
            self.x1 += self.movement_increment
            self.x2 += self.movement_increment
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
        self.draw()
        root.after(10,self.move)

player = Player()

root.after(10,player.move)
root.mainloop()
