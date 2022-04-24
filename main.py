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
font = pygame.font.Font(pygame.font.get_default_font(), 30)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#initial values
T_0 = 780
I_0 = 1
V_0 = 0
Z_0 = 0

#ongoing values
T_n = T_0
I_n = I_0
V_n = V_0
Z_n = Z_0

r = 1 #growth rate of healthy cells
alpha = 1.2 #limitation coefficient of infected cells imposed on the growth of target cells
T_max = 1000 #max number of healthy cells
d1 = 0.4 #death rate of infected cells
d2 = 2.4 #death rate of free virus
d3 = 1.618 # death rate of immune (CTL) cells
p = .812 #killing rate of infected cells by CTL cells
k = 20 #rate free viral particals are released by infected cells
tau = 1.2 #time after infection that immune (CTL) cells can start growing    #occilation at .2
c = 0.05 #rate of immune (CTL) cell growth

delta_t = .00001 #the change in time for the computations

#Queue to store the prev I_n
prevI_nQueue = Queue(maxsize = 0)

#Assumption
## f1(x) = cx, this satisfies A1 in the paper
#viral infection rate
def f1(x):
    return 0.0005 * x

#Assumption
## f2(x) = cx, this satisfies A1 in the paper
#infected cell infection rate
def f2(x):
    return 0.000065 * x

def T_next(T_nl):
    T_nl += delta_t * (r*T_nl*(1 - (T_nl + alpha*I_n)/T_max) - f1(V_n)*T_nl - f2(I_n)*T_nl)
    if (T_nl <= 0):
        return 0
    return T_nl

def I_next(I_nl):
    prevI_nQueue.put(I_nl)
    I_nl += delta_t * (f1(V_n)*T_n + f2(I_nl)*T_n - d1*I_nl - p*I_nl*Z_n)
    if (I_nl < 0):
        return 0
    #if (I_n < 1 and I_n < prevI_n):
    #    return 0
    return I_nl

def V_next(V_nl):
    V_nl += delta_t * (k*I_n - d2*V_nl)
    if (V_n < 0):
        return 0
    #if (V_n < 1 and V_n < prevV_n):
    #    return 0
    return V_nl

def Z_next(Z_nl):
    if (prevI_nQueue.qsize() >= round(tau/delta_t)):
        Z_nl += delta_t * (c*prevI_nQueue.get() - d3*Z_nl)
    else:
        Z_nl += delta_t * (0 - d3*Z_nl)
    if (Z_nl < 0):
        return 0
    return Z_nl

class Bar(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.width = 25
        self.maxHeight = 120
        self.height = 120
        self.totalCells = T_n + I_n + V_n + Z_n
        self.image = pygame.Surface((self.width, self.height))
        self.border = pygame.Surface((self.width+4, self.maxHeight+4))
        self.border.fill(WHITE)
        self.border.fill(BLACK, self.border.get_rect().inflate(-2, -2))
        self.rect = self.image.get_rect()
        self.xpos = 250
        self.ypos = 15
        self.position = []
        self.type = type

        if (type == 'T_n'):
            self.height = (T_n / self.totalCells) * self.maxHeight
            self.image = pygame.Surface((self.width, self.height))
            self.rect = self.image.get_rect()
            self.image.fill(WHITE)
            #self.image.fill(BLACK), self.image.get_rect().inflate(-2, -2))
            #self.image.fill(WHITE, self.image.get_rect().inflate(-2, -border))
            self.position = [self.xpos, self.ypos]
        
        if (type == 'I_n'):
            self.height = (I_n / self.totalCells) * self.maxHeight
            self.image = pygame.Surface((self.width, self.height))
            self.rect = self.image.get_rect()
            self.image.fill((102, 50, 0))
            self.position = [self.xpos + (1 * 20) + 15, self.ypos]
        
        if (type == 'V_n'):
            self.height = (V_n / self.totalCells) * self.maxHeight
            self.image = pygame.Surface((self.width, self.height))
            self.rect = self.image.get_rect()
            self.image.fill((255, 0, 0))
            self.position = [self.xpos + (2 * 20) + 30, self.ypos]

        if (type == 'Z_n'):
            self.height = (Z_n / self.totalCells) * self.maxHeight
            self.image = pygame.Surface((self.width, self.height))
            self.rect = self.image.get_rect()
            self.image.fill((0, 255, 0))
            self.position = [self.xpos + (3 * 20) + 45, self.ypos]
        
    def Update(self):
        self.totalCells = T_n + I_n + V_n + Z_n

        if (self.type == 'T_n'):
            self.height = (T_n / self.totalCells) * self.maxHeight
            self.image = pygame.Surface((self.width, self.height))
            self.rect = self.image.get_rect()
            self.image.fill(WHITE)

        if (self.type == 'I_n'):
            self.height = (I_n / self.totalCells) * self.maxHeight
            self.image = pygame.Surface((self.width, self.height))
            self.rect = self.image.get_rect()
            self.image.fill((102, 50, 0))

        if (self.type == 'V_n'):
            self.height = (V_n / self.totalCells) * self.maxHeight
            self.image = pygame.Surface((self.width, self.height))
            self.rect = self.image.get_rect()
            self.image.fill((255, 0, 0))

        if (self.type == 'Z_n'):
            self.height = (Z_n / self.totalCells) * self.maxHeight
            self.image = pygame.Surface((self.width, self.height))
            self.rect = self.image.get_rect()
            self.image.fill((0, 255, 0))
        
    def movingBarPos(self):
        yOffset = self.maxHeight - self.height
        return [self.position[0], self.position[1] + yOffset]


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

        if (pygame.time.get_ticks() >= self.next_pos_change):
            self.position[0] = self.position[0] + self.velocity[0]
            self.position[1] = self.position[1] + self.velocity[1]
            self.next_pos_change = pygame.time.get_ticks() + 5

    def ViralUpdate(self):
        if (self.position[1] > HEIGHT or self.position[1] < 0):
            self.velocity = [self.velocity[0], -1.0 * self.velocity[1]]
        if (self.position[0] > WIDTH or self.position[0] < 0):
            self.velocity = [-1.0 * self.velocity[0], self.velocity[1]]

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

#create porportion bars
T_nBar = Bar('T_n')
I_nBar = Bar('I_n')
V_nBar = Bar('V_n')
Z_nBar = Bar('Z_n')

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
    textBG = pygame.Surface((230, 165), pygame.SRCALPHA)
    textBG.fill((0, 0, 0, 190))
    screen.blit(textBG, dest=(0, 0))
    T_nText = font.render('Healthy: ' + str(round(T_n)), True, WHITE)
    I_nText = font.render('Infected: ' + str(round(I_n, 1)), True, (162, 110, 60))
    V_nText = font.render('Viral: ' + str(round(V_n, 1)), True, (225, 0, 0))
    Z_nText = font.render('Immune: ' + str(round(Z_n, 1)), True, (0, 255, 0))
    timeText = font.render('Time: ' + str(round(currTime, 1)), True, (255, 255, 255))
    screen.blit(T_nText, dest=(10,10))
    screen.blit(I_nText, dest=(10,40))
    screen.blit(V_nText, dest=(10,70))
    screen.blit(Z_nText, dest=(10,100))
    screen.blit(timeText, dest=(10,130))

    #update and print porportion bars to screen
    T_nBar.Update()
    screen.blit(T_nBar.border, [T_nBar.position[0] - 2, T_nBar.position[1] - 2])
    screen.blit(T_nBar.image, T_nBar.movingBarPos())

    I_nBar.Update()
    screen.blit(T_nBar.border, [I_nBar.position[0] - 2, I_nBar.position[1] - 2])
    screen.blit(I_nBar.image, I_nBar.movingBarPos())

    V_nBar.Update()
    screen.blit(V_nBar.border, [V_nBar.position[0] - 2, V_nBar.position[1] - 2])
    screen.blit(V_nBar.image, V_nBar.movingBarPos())

    Z_nBar.Update()
    screen.blit(Z_nBar.border, [Z_nBar.position[0] - 2, Z_nBar.position[1] - 2])
    screen.blit(Z_nBar.image, Z_nBar.movingBarPos())

    #compute next 400 time steps but do not render them for speed
    for i in range(10000):
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
