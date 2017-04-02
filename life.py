"""LIFE, but not as we know it."""

# Project initiation March 2017, just got my Raspberry Pi SenseHat.
# Becomming a mad hatter....

# Developing a script which runs LIFE on a Raspberry Pi 8x8 grid.
# Using colors

# http://www.python-course.eu/tkinter_labels.php
# https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
#   1. Any live cell with fewer than two live neighbours dies, as if caused by underpopulation.
#   2. Any live cell with two or three live neighbours lives on to the next generation.
#   3. Any live cell with more than three live neighbours dies, as if by overpopulation.
#   4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

import math
import random
import time
from sense_hat import SenseHat

sense = SenseHat()

# Some basic colors
r = [255, 0, 0]     # Red
o = [255, 127, 0]   # Orange
y = [255, 255, 0]   # Yellow
g = [0, 255, 0]     # Green
b = [0, 0, 255]     # Blue
i = [75, 0, 130]    # Indigo
v = [159, 0, 255]   # Violet
w = [255, 255, 255] # White
e = [0, 0, 0]       # e stands for empty/black

# An Array of three LIFE playfields, using a grid of 8x8

ACTIVEFIELD = 0
BIRTHFIELD = 1
STAYINGALIVE = 2
COLORS = 3
NEWCOLORS = 4

DEAD = 0
ALIVE = 1
BIRTH = 2

PLAYFIELD = [
    [0, 0, 0, 1, 0, 0, 0, 0,
     0, 0, 0, 1, 1, 1, 0, 0,
     0, 0, 0, 0, 1, 0, 0, 0,
     0, 0, 0, 0, 1, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     1, 0, 0, 0, 0, 0, 1, 1,
     0, 0, 0, 0, 0, 1, 1, 0,
     0, 0, 0, 1, 0, 0, 0, 0
    ],
    [0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0
    ],
    [0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0
    ],
    [e, e, e, b, e, e, e, e,
     e, e, e, b, b, b, e, e,
     e, e, e, e, b, e, e, e,
     e, e, e, e, b, e, e, e,
     e, e, e, e, e, e, e, e,
     y, e, e, e, e, e, y, y,
     e, e, e, e, e, y, y, e,
     e, e, e, b, e, e, e, e
    ],
    [e, e, e, r, e, e, e, e,
     e, e, e, r, r, r, e, e,
     e, e, e, e, r, e, e, e,
     e, e, e, e, r, e, e, e,
     e, e, e, e, e, e, e, e,
     y, e, e, e, e, e, y, y,
     e, e, e, e, e, y, y, e,
     e, e, e, r, e, e, e, e
    ]
]

# Icons

ICON_READY = [
    e, e, e, e, e, e, e, e,
    e, e, y, y, y, y, e, e,
    e, y, w, y, y, w, y, e,
    e, y, w, y, y, w, y, e,
    e, y, y, y, y, y, y, e,
    e, y, e, y, y, e, y, e,
    e, e, y, e, e, y, e, e,
    e, e, e, y, y, e, e, e
    ]

def print_field(field):
    """ Just a debug function to display a LIFE playfield
        Field is an Array of 8x8 cells
        """
    cell = 0

    while cell < 64:
        print(field[cell], end="") # No EOL, end of line
        cell += 1

        if cell % 8 == 0:
            print("")   # End of the line

    print("")   # just a newline


def is_life_frozen():
    """ is LIFE frozen? No cell generation?
        """
    cell = 0
    frozen = True

    while cell < 64 and frozen == True:
        if PLAYFIELD[0][cell] != PLAYFIELD[1][cell]:
            frozen = False
        cell += 1

    return frozen


def render_life(image):
    """ Render LIFE on Sense Hat matrix """
    sense.set_pixels(image)


def give_birth(field):
    """ Just a debug function to display a LIFE playfield """
    column = 0
    cell = 0
    row = 0

    while cell < 64:
        column = cell % 8
        row = math.floor(cell / 8)

        # Build new PLAYFIELD
        set_cell_birth(column, row, 0)
        neighborCount = count_cells_alive(field, column, row)

        # Rule 1. Any live cell with fewer than two live neighbours dies,
        #         as if caused by underpopulation.
        if neighborCount < 2 and field[cell] == ALIVE:
            set_cell_birth(column, row, DEAD)

        # Rule 2. Any live cell with two or three live neighbours lives on
        #         to the next generation.
        if 1 < neighborCount < 4 and field[cell] == ALIVE:
            set_cell_birth(column, row, ALIVE)

        # Rule 3. Any live cell with more than three live neighbours dies,
        #         as if by overpopulation.
        if neighborCount > 3 and field[cell] == ALIVE:
            set_cell_birth(column, row, DEAD)

        # Rule 4. Any dead cell with exactly three live neighbours becomes a live cell,
        #         as if by reproduction.
        if neighborCount == 3 and field[cell] == DEAD:
            set_cell_birth(column, row, BIRTH)

        cell += 1

def random_color(color):
    color = color + random.randint(0, round((255 - color) * 0.5)) - round((255 - color) * 0.25) 
    if color > 255 :
        color = 255
    if color < 0:
        color = 0
    return color
    
def set_cell_birth(x_pos, y_pos, value):
    """Birth of cells"""
    idx = x_pos + y_pos * 8

    
    PLAYFIELD[NEWCOLORS][idx] = b # White

    if value > 0:
        # Cell is alive
        PLAYFIELD[BIRTHFIELD][idx] = ALIVE
        
        if PLAYFIELD[STAYINGALIVE][idx] > 0:
            print ("found", PLAYFIELD[STAYINGALIVE][idx]);
            
        PLAYFIELD[STAYINGALIVE][idx] += 1 # Number of ticks alive

        if value == BIRTH:
            # Birth of a new cell, change colors slightly
            # Mixed colors of 3 parents
            colorRGB = mix_color_cells_alive(x_pos, y_pos)

            colorRGB[0] = random_color(colorRGB[0])
            colorRGB[1] = random_color(colorRGB[1])
            colorRGB[2] = random_color(colorRGB[2])
 
        else :
            # Cell was already alive
            colorRGB = mix_color_cells_alive(x_pos, y_pos)

        #colorRGB[0] = round(colorRGB[0] / PLAYFIELD[STAYINGALIVE][idx])
        #colorRGB[1] = round(colorRGB[1] / PLAYFIELD[STAYINGALIVE][idx])
        #colorRGB[2] = round(colorRGB[2] / PLAYFIELD[STAYINGALIVE][idx])
        
        PLAYFIELD[NEWCOLORS][idx] = colorRGB
     
    else:
        # Cell is dead
        PLAYFIELD[BIRTHFIELD][idx] = DEAD
        PLAYFIELD[STAYINGALIVE][idx] = round(PLAYFIELD[STAYINGALIVE][idx] / 2) # reset LIFE
        PLAYFIELD[NEWCOLORS][idx] = e # Empty


def boundary_overflow(posX, posY):
    """ Correct coordinates for boudary overflow
        Treating the 8x8 boundaries as if they don't exist.
        (8,8) is the same as (0,0), (-1,-1) same as (7,7)
        """
    x_field = posX
    y_field = posY
    
    if x_field > 7:
        x_field = 0
    if x_field < 0:
        x_field = 7
    if y_field > 7:
        y_field = 0
    if y_field < 0:
        y_field = 7
        
    return [x_field, y_field]


def count_cells_alive(field, posX, posY):
    """ cell the number of life cells around this cell (in total 8 cells) """
    lifeones = 0
    neigbours = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
    for neigbour in neigbours:

        coordinate = boundary_overflow(neigbour[0] + posX, neigbour[1] + posY)
        if field[coordinate[0] + coordinate[1] * 8] == 1:
            lifeones += 1

    return lifeones


def mix_color_cells_alive(x_pos, y_pos):
    """ Check for life cells around this cell (in total 8 cells)
        count the colors RGB mix
        """
    lifeones = 0
    r = 0       # Red color 0..255
    g = 0       # Green color 0..255
    b = 0       # Blue color 0..255
    
    neigbours = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
    for neigbour in neigbours:

        # Coordinates always with the 8x8 grid boundaries.
        coordinate = boundary_overflow(neigbour[0] + x_pos, neigbour[1] + y_pos)
        idx = coordinate[0] + coordinate[1] * 8

        if PLAYFIELD[ACTIVEFIELD][idx] == 1:
            lifeones += 1
            r += PLAYFIELD[COLORS][idx][0]
            g += PLAYFIELD[COLORS][idx][1]
            b += PLAYFIELD[COLORS][idx][2]

    if lifeones:
        r = int(round(r / lifeones))
        g = int(round(g / lifeones))
        b = int(round(b / lifeones))
    
    return [r, g, b]


#
# loop LIFE
#

MAXTICKS = 200 # 86

while MAXTICKS > 0:
    MAXTICKS -= 1
    # print_field(PLAYFIELD[ACTIVEFIELD])
    render_life(PLAYFIELD[COLORS])
    give_birth(PLAYFIELD[ACTIVEFIELD])

    if ACTIVEFIELD == 0:
        ACTIVEFIELD = 1
        BIRTHFIELD = 0
        COLORS = 4
        NEWCOLORS = 3
    else:
        ACTIVEFIELD = 0
        BIRTHFIELD = 1
        COLORS = 3
        NEWCOLORS = 4

    if is_life_frozen():
        print("FROZEN")

        cell = random.randint(0, 63)
        PLAYFIELD[ACTIVEFIELD][cell] = 1
        colorRGB = mix_color_cells_alive(cell % 8, math.floor(cell / 8))

        colorRGB[0] = random_color(colorRGB[0])
        colorRGB[1] = random_color(colorRGB[1])
        colorRGB[2] = random_color(colorRGB[2])
        PLAYFIELD[COLORS][cell] = colorRGB
        
        cell = random.randint(0, 63)
        PLAYFIELD[ACTIVEFIELD][cell] = 1
        colorRGB = mix_color_cells_alive(cell % 8, math.floor(cell / 8))

        colorRGB[0] = random_color(colorRGB[0])
        colorRGB[1] = random_color(colorRGB[1])
        colorRGB[2] = random_color(colorRGB[2])
        PLAYFIELD[COLORS][cell] = colorRGB
        
    time.sleep(0.1)


time.sleep(1)
sense.set_rotation(180)
render_life(ICON_READY)
time.sleep(3)
sense.clear()
print_field(PLAYFIELD[ACTIVEFIELD])
