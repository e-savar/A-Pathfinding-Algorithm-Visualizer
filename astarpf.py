import pygame
import math
from queue import PriorityQueue

#Window Parameters
SIZE = 800
WIN = pygame.display.set_mode((SIZE, SIZE))
pygame.display.set_caption("A* Path Finding Algorithm Visualizer")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQOISE = (64, 224, 208)

#WHITE = we have not looked at it
#RED = we have looked at it
#BLACK = barrier
#ORANGE = start node
#GREEN = path

class Spot:
    def __init__(self, row, col, size, total_rows):
        self.row = row
        self.col = col
        self.size = size
        self.total_rows = total_rows
        self.x = row*size
        self.y = col*size
        self.color = WHITE
        self.neighbors = []
    
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQOISE
    
    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN
    
    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQOISE
    
    def make_path(self):
        self.color = GREEN

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))
    
    def update_neighbors(self, grid):
        self.neighbors = []
        #IF ABLE TO MOVE DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        #UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        #RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        #LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
    #Less than
    def __lt__(self, other):
        return False

#finds distance between points p1 and p2 using Manhattan Distance
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    #F-Score of start
    open_set.put((0, count, start))
    came_from = {}
    #Keeps track of the shortest distance from the start node to get to x node
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    #Keeps track of predicted distance to get to end node
    f_score = {spot: float("inf") for row in grid for spot in row}
    #estimate how far away the end score is from our start node which algo to know max distance
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        #make path
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            #if better path, than update it to make this the best option
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_closed()
        draw()

        if current != start:
            current.make_closed()
    return False

#makes grid
def make_grid(rows, size):
    grid = [] 
    gap = size // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot) #in grid row I, appends new spot
    return grid

#draws grid
def draw_grid(win, rows, size):
    gap = size // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (size, i*gap)) #draws horizontal lines at x = 0 and x = size
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, size)) #draws vertical lines at y = 0 and y = size
    
#Actually builds the screen
def draw(win, grid, rows, size):
    win.fill(WHITE)
        
    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, size)
    pygame.display.update() #UPDATE method similar in UNITY

#for drawing the mazes
def get_clicked_pos(pos, rows, size):
    gap = size // rows
    y,x = pos

    row = y // gap
    col = x // gap
    return row, col

def main(win, size):
    #dynamic sizing
    ROWS = 50
    grid = make_grid(ROWS, size)
        
    start = None
    end = None
        
    run = True
    started = False
    while run:
        draw(win, grid, ROWS, size)
        for event in pygame.event.get():
            #if closed out
            if event.type == pygame.QUIT:
                run = False
            #LEFT, allows for user to draw
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, size)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                    
                elif spot != end and spot != start:
                    spot.make_barrier()
            #RIGHT, allows for user to delete
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, size)
                spot = grid[row][col]
                spot.reset()

                if spot == start:
                    start = None
                if spot == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, size), grid, start, end)
                #resets Grid
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, SIZE)
    pygame.quit()


main(WIN, SIZE)
