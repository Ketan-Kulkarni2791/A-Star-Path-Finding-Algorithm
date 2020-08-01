import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


# These spots are the actual cubes/nodes.
class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE  # In the beginning, all the cubes will be white.
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    # For indexing each cube.
    def get_pos(self):
        return self.row, self.col

    # These are red cubes as we would have considered/visited them already
    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    # To draw the cube on the screen.
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        # Here I will check whether the neighbor cube is barrier, and if not, add it to neighbors list.
        self.neighbors = []

        # Here we are going same column but one row DOWN.
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        # Here we are going same column but one row UP.
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        # Here we are going same row but one col RIGHT.
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        # Here we are going same row but one col LEFT.
        if self.col < 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    # This is less than function which compares two cube objects.
    def __lt__(self, other):
        return False


# This is my heuristic function
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
    # Here I am going to put start node/cube with its original F-score which is initially zero into the open_set.
    # The reason of putting count is to keep track of when we inserted these items into queue so that we an break ties
    # if two values that have the same F-score.
    # And start is the actual number here.
    open_set.put((0, count, start))
    # To keep the track of from which node did this node come from, I will use this dictionary.
    came_from = {}
    # Let's make a table to store all the g scores.
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    # Let's make a table to store all the f scores.
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    # since PriorityQueue doesn't have anything to tell us if node is in it or not. So I am taking this set here.
    # It will keep track of all the nodes that are in this PriorityQueue.
    # I can put or remove items from the PriorityQueue but can't check whether the value is in PriorityQueue.
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # I am going to start at the very beginning  of these lops by popping the lowest value f-score from my open_set.
        # The values with same f-score will look at the count like which one was inserted first.
        # This is where the current node is looking at.
        current = open_set.get()[2]  # Since the start node is at 2nd index after f-score and count in set.
        open_set_hash.remove(current)  # Immediately pop up the current node from here as well.

        # If I found the end, I have found the path and then close it by drawing the path.
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        # Now let's consider the neighbors of the current nodes
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1  # since we are going 1 node/cube over.

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()  # Thia will tel us that we have already considered this neighbor.
        draw()

        if current != start:
            current.make_closed()

    return False


# I should have a data structure to hold all these grids so that I can actually use them, manipulate them, traverse them
def make_grid(rows, width):
    grid = []
    gap = width // rows  # This will decide size/shape of the single cube or will decide width of the cubes.
    # Here I am creating a 2D rows like this :
    # [[][][]]
    # [[][]]
    for i in range(rows):  # i is row
        grid.append([])
        for j in range(rows):  # j is col.
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


# Above method is just creating white cube blocks. But I need to provide them grid lines to separate them.
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):  # For horizontal lines
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    # I have filled the grid.
    win.fill(WHITE)
    # I have drawn the cubes.
    for row in grid:
        for spot in row:
            # Here I just have to pass win. Other parameters are taken by itself like color and axis.
            spot.draw(win)
    # On top of that let's draw grid lines.
    draw_grid(win, rows, width)
    # Take whatever I've drawn and update that.
    pygame.display.update()


# To figure out which spot is going to changes its color after user clicks it
# For that I have to figure out where is my mouse pointer in this screen.
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None

    # This is to keep track whether we are using main.make_closed
    run = True
    # This is to keep track whether we are using algorithm.
    started = False

    while run:
        # Otherwise I will see a black screen.
        draw(win, grid, ROWS, width)
        # At the beginning of this while loop, let's loop through all the events that have happened and check what
        # they are. e.g. mouse is pressed down, or timer went off etc.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # This is to restrict user from clicking any thing other than quit button.
            if started:
                continue

            # If user pressed down on the mouse, I need to potentially draw barrier/start/goal position.
            # [0] if you pressed down left mouse button.
            if pygame.mouse.get_pressed()[0]:
                # This will give me the x and y co-ordinates where exactly our mouse is.
                pos = pygame.mouse.get_pos()
                # Using those x and y axis, my helper function will give me exact row and col.
                row, col = get_clicked_pos(pos, ROWS, width)
                # So now I can access that spot/cube.
                spot = grid[row][col]
                # Now we can manipulate it whatever like we want to do.
                # If not start, then make the one start.
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != start and spot != end:
                    spot.make_barrier()
            # [2] if you pressed down right most button.
            elif pygame.mouse.get_pressed()[2]:
                # This will give me the x and y co-ordinates where exactly our mouse is.
                pos = pygame.mouse.get_pos()
                # Using those x and y axis, my helper function will give me exact row and col.
                row, col = get_clicked_pos(pos, ROWS, width)
                # So now I can access that spot/cube.
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            # The event if user has clicked any keyboard key.
            if event.type == pygame.KEYDOWN:
                # If user hits space key.
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    # Here, if I do x = lambda : print("Hello World !") and x(), it will call print function.
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)
