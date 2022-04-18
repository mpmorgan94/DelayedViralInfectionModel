from queue import Queue
from turtle import width
from types import CellType
import pygame
import random
import numpy as np

pygame.init()

WIDTH = 1000
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60
font = pygame.font.Font(pygame.font.get_default_font(), 25)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#initial values
T_0 = 1000
I_0 = 1
V_0 = 0
Z_0 = 0

#ongoing values
T_n = T_0
I_n = I_0
V_n = V_0
Z_n = Z_0

r = .9 #growth rate of healthy cells
alpha = .5 #limitation coefficient of infected cells imposed on the growth of target cells
T_max = 1500 #max number of healthy cells
d1 = .9 #death rate of infected cells
d2 = .9 #death rate of free virus
d3 = .9 # death rate of immune (CTL) cells
p = 1 #killing rate of infected cells by CTL cells
k = .2 #rate free viral particals are released by infected cells
tau = 3 #time after infection that immune (CTL) cells can start growing    #occilation at .2
c = .9 #rate of immune (CTL) cell growth

delta_t = .00001 #the change in time for the computations

#Queue to store the prev I_n
prevI_nQueue = Queue(maxsize = 0)

#Assumption
## f1(x) = cx, this satisfies A1 in the paper
#viral infection rate
def f1(x):
    return 0.0037 * x

#Assumption
## f2(x) = cx, this satisfies A1 in the paper
#infected cell infection rate
def f2(x):
    return 0.002 * x

def T_next(T_nl):
    T_nl += delta_t * (r*T_nl*(1 - (T_nl + alpha*I_n)/T_max) - f1(V_n)*T_n - f2(I_n)*T_nl)
    if (T_nl < 1):
        return 0
    return T_nl

def I_next(I_nl):
    prevI_nQueue.put(I_nl)
    I_nl += delta_t * (f1(V_n)*T_n + f2(I_nl)*T_n - d1*I_nl - p*I_nl*Z_n)
    if (I_nl < 0):
        return 0
    if (I_n < 1 and I_n < prevI_n):
        return 0
    return I_nl

def V_next(V_nl):
    V_nl += delta_t * (k*I_n - d2*V_nl)
    if (V_n < 1 and V_n < prevV_n):
        return 0
    return V_nl

def Z_next(Z_nl):
    if (prevI_nQueue.qsize() >= round(tau/delta_t)):
        Z_nl += delta_t * (c*prevI_nQueue.get() - d3*Z_nl)
    else:
        Z_nl += delta_t * (0 - d3*Z_nl)
    if (Z_nl < 0):
        return 0
    return Z_nl

class Cell(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((7, 7))
        self.depth = random.randint(50, 100) / 100
        self.image.fill((255*self.depth, 255*self.depth, 255*self.depth))
        self.rect = self.image.get_rect()
        self.position = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
        self.velocity = [0, 0]
        self.next_pos_change = pygame.time.get_ticks() + 100
    
    def Infect(self):
        self.image.fill((102, 50, 0))
    
    def Viral(self):
        self.image = pygame.Surface((3, 3))
        self.depth = 1
        self.image.fill((255, 0, 0))
        self.velocity = [random.randint(-100, 100) / 100, random.randint(-100, 100) / 100]
    
    def Immune(self):
        self.image = pygame.Surface((3, 3))
        self.depth = 1
        self.image.fill((0, 255*self.depth, 0))
        self.velocity = [random.randint(-100, 100) / 100, random.randint(-100, 100) / 100]

    def ImmuneUpdate(self):
        if (self.position[1] > HEIGHT or self.position[1] < 0):
            self.velocity = [self.velocity[0], -1.0 * self.velocity[1]]
        if (self.position[0] > WIDTH or self.position[0] < 0):
            self.velocity = [-1.0 * self.velocity[0], self.velocity[1]]

        #if (abs(self.position[0] + abs(self.velocity[0])) < abs(self.position[0] + 0.5)):
        #    if (abs(self.position[1] + abs(self.velocity[1])) < abs(self.position[1] + 0.5)):
        if (pygame.time.get_ticks() >= self.next_pos_change):
            self.position[0] = self.position[0] + self.velocity[0]
            self.position[1] = self.position[1] + self.velocity[1]
            self.next_pos_change = pygame.time.get_ticks() + 5

    def ViralUpdate(self):
        if (self.position[1] > HEIGHT or self.position[1] < 0):
            self.velocity = [self.velocity[0], -1.0 * self.velocity[1]]
        if (self.position[0] > WIDTH or self.position[0] < 0):
            self.velocity = [-1.0 * self.velocity[0], self.velocity[1]]

        #if (abs(self.position[0] + abs(self.velocity[0])) < abs(self.position[0] + 0.5)):
        #    if (abs(self.position[1] + abs(self.velocity[1])) < abs(self.position[1] + 0.5)):
        if (pygame.time.get_ticks() >= self.next_pos_change):
            self.position[0] = self.position[0] + self.velocity[0]
            self.position[1] = self.position[1] + self.velocity[1]
            self.next_pos_change = pygame.time.get_ticks() + 5



allHealthyCells = []
for i in range(T_0):
    newCell = Cell()
    allHealthyCells.append(newCell)

allInfectedCells = []
for i in range(I_0):
    newCell = Cell()
    newCell.Infect()
    allInfectedCells.append(newCell)

allVirals = []
for i in range(V_0):
    newViral = Cell()
    newViral.Viral()
    allVirals.append(newViral)

allImmuneCells = []
for i in range(Z_0):
    newCell = Cell()
    newCell.Immune()
    allImmuneCells.append(newCell)

prevT_n = T_0
prevI_n = I_0
prevV_n = V_0
prevZ_n = Z_0
currTime = 0

running = True
while running:
    print('T count: ' + str(T_n) + '\n')
    print('I count: ' + str(I_n) + '\n')
    print('V count: ' + str(V_n) + '\n')
    print('Z count: ' + str(Z_n) + '\n\n\n\n\n')
    dt = clock.tick(FPS) / 1000  # Returns milliseconds between each call to 'tick'. The convert time to seconds.
    screen.fill(BLACK)  # Fill the screen with background color.

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                T_n += 1
            if event.key == pygame.K_i:
                I_n += 1
    

    if (round(I_n) > len(allInfectedCells)):
        #move appropriate number of oldest healthy cells from allhealthy cells array
        for i in range(round(I_n) - len(allInfectedCells)):
            #oldest cells will be at the front of the array
            #add infected cells to all infected cells array and change color to red
            allHealthyCells[0].Infect()
            allInfectedCells.append(allHealthyCells.pop(0))
    if (round(I_n) < len(allInfectedCells)):
        #simply remove the oldest infected cells from the allinfected cells array
        for i in range(len(allInfectedCells) - round(I_n)):
            allInfectedCells.pop(0)
    if (round(T_n) > len(allHealthyCells)):
        #add more healthycells
        for i in range(round(T_n) - len(allHealthyCells)):
            newCell = Cell()
            allHealthyCells.append(newCell)
    if (round(T_n) < len(allHealthyCells)):#round(prevT_n) + (round(I_n) - round(prevI_n))):
        #remove oldest healthy cells from healthy cells array
        for i in range(len(allHealthyCells) - round(T_n)):
            #change their color to a shade of red
            allHealthyCells[0].Infect()
            allInfectedCells.append(allHealthyCells.pop(0))
    if (round(V_n) > len(allVirals)):
        #make more virals
        for i in range(round(V_n) - len(allVirals)):
            newViral = Cell()
            newViral.Viral()
            allVirals.append(newViral)
    if (round(V_n) < len(allVirals)):
        #remove oldest virals
        for i in range(len(allVirals) - round(V_n)):
            allVirals.pop(0)
    if (round(Z_n) > len(allImmuneCells)):
        #add more immune cells
        for i in range(round(Z_n) - len(allImmuneCells)):
            newCell = Cell()
            newCell.Immune()
            allImmuneCells.append(newCell)
    if (round(Z_n) < len(allImmuneCells)):
        #remove oldest immune cells
        for i in range(len(allImmuneCells) - round(Z_n)):
            allImmuneCells.pop(0)

    for cell in allHealthyCells:
        screen.blit(cell.image, cell.position)
    for cell in allInfectedCells:
        screen.blit(cell.image, cell.position)
    for viral in allVirals:
        viral.ViralUpdate()
        screen.blit(viral.image, viral.position)
    for cell in allImmuneCells:
        cell.ImmuneUpdate()
        screen.blit(cell.image, cell.position)
    
    #print current stats to screen
    T_nText = font.render('T_n: ' + str(round(T_n, 1)), True, WHITE)
    I_nText = font.render('I_n: ' + str(round(I_n, 1)), True, (152, 100, 50))
    V_nText = font.render('V_n: ' + str(round(V_n, 1)), True, (225, 0, 0))
    Z_nText = font.render('Z_n: ' + str(round(Z_n, 1)), True, (0, 255, 0))
    timeText = font.render('time: ' + str(round(currTime, 1)), True, (255, 255, 255))
    screen.blit(T_nText, dest=(0,0))
    screen.blit(I_nText, dest=(0,30))
    screen.blit(V_nText, dest=(0,60))
    screen.blit(Z_nText, dest=(0,90))
    screen.blit(timeText, dest=(0,120))
    
    for i in range(400):
        newT = T_next(T_n)
        newI = I_next(I_n)
        newV = V_next(V_n)
        newZ = Z_next(Z_n)
        prevT_n = T_n
        prevI_n = I_n
        prevV_n = V_n
        prevZ_n = Z_n
        T_n = newT
        I_n = newI
        V_n = newV
        Z_n = newZ
        currTime += delta_t

    pygame.display.update()


quit()