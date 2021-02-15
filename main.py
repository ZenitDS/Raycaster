import pygame
import bin.colors as colors
import math
import sys
from PIL import Image
PI = math.pi
pygame.init()

screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()

# ---------- GAME VARIABLES -----------
class Ray:
    def __init__(self,distance,texture_idx,texture_offset_x,x,y):
        self.distance = distance
        self.texture_index = texture_idx
        self.texture_offset_x = texture_offset_x
        self.x = x
        self.y = y

tile_size = 50
texture_size = 16
textures = []
pygtextures = []
def AddTexture(path):
    textures.append(Image.open(f"bin/textures/{path}").convert("RGB"))
    img = pygame.image.load(f"bin/textures/{path}")
    img = pygame.transform.scale(img,(tile_size,tile_size))
    pygtextures.append(img)

AddTexture("WallLinesHorizontal.png")
AddTexture("WallLinesVertical.png")
AddTexture("Machine.png")
AddTexture("Door.png")



fov = 85
speed = 0.03
px = 3.5
py = 1.5

pdir = PI/2
mapWidth = 8
mapHeight = 8
map = [
    [1,1,1,1,1,1,1,1],
    [1,3,3,3,3,2,0,1],
    [1,0,0,0,0,2,0,1],
    [1,0,0,0,0,2,0,1],
    [1,0,0,0,0,4,0,1],
    [1,0,0,0,0,2,0,1],
    [1,3,3,0,3,2,0,1],
    [1,1,1,3,1,1,1,1],
]


def CheckPointCollision(x, y):
    if x > mapWidth-1 or x < 0:
        return [True,0]
    elif y > mapHeight-1 or y < 0:
        return [True, 0]
    return [map[math.floor(x)][math.floor(y)] != 0,map[math.floor(x)][math.floor(y)]]


def degtorad(degrees):
    return degrees * PI / 180


def adjustrad(rad):
    if rad > 2*PI:
        rad -= 2*PI
    elif rad < 0:
        rad += 2*PI
    return rad


def CalculateRay(x, y, direction):
    if direction == 0:
        return [px, py]
    last_index = 0
    index = 0
    # ------ CALCULATE X == 1 ------
    x_mult = 0
    y_mult = 0
    if degtorad(90) >= direction and direction > 0:
        x_mult = 1
        y_mult = 1
    elif degtorad(180) >= direction and direction > degtorad(90):
        x_mult = -1
        y_mult = -1
    elif degtorad(270) >= direction and direction > degtorad(180):
        x_mult = -1
        y_mult = -1
    elif degtorad(360) >= direction and direction > degtorad(270):
        x_mult = 1
        y_mult = 1

    current_x = 0
    current_y = 0

    if (degtorad(90) > direction) or (direction > degtorad(270)):
        current_x = (x - x % 1 + 1)
        current_y = y + (math.tan(direction) * (1 - x % 1))
    elif (degtorad(90) < direction) or (direction < degtorad(270)):
        current_x = (x - x % 1)
        current_y = y + (math.tan(direction) * -(x % 1))

    dx = 1 * x_mult
    dy = math.tan(direction) * y_mult

    for i in range(10):
        fcurrent_x = round(current_x)
        fcurrent_y = math.floor(current_y)
        if CheckPointCollision(fcurrent_x, fcurrent_y)[0]:
            last_index = CheckPointCollision(fcurrent_x, fcurrent_y)[1]
            break
        elif CheckPointCollision(fcurrent_x-1,fcurrent_y)[0]:
            last_index = CheckPointCollision(fcurrent_x-1, fcurrent_y)[1]
            break
        current_x += dx
        current_y += dy

    x_lastx = current_x
    x_lasty = current_y
    distance = math.sqrt((current_x-px)**2 + (current_y-py)**2)

    # ------ CALCULATE Y = 1
    x_mult = 0
    y_mult = 0
    if degtorad(90) >= direction and direction > 0:
        x_mult = 1
        y_mult = 1
    elif degtorad(180) >= direction and direction > degtorad(90):
        x_mult = 1
        y_mult = 1
    elif degtorad(270) >= direction and direction > degtorad(180):
        x_mult = -1
        y_mult = -1
    elif degtorad(360) >= direction and direction > degtorad(270):
        x_mult = -1
        y_mult = -1

    current_x = 0
    current_y = 0

    if direction <= degtorad(180):
        current_y = (y - y % 1 + 1)
        current_x = x + ((1 - y % 1) / math.tan(direction))
    elif direction > degtorad(180):
        current_y = (y - y % 1)
        current_x = x + (-(y % 1) / math.tan(direction))

    dx = 1 / math.tan(direction) * x_mult
    dy = 1 * y_mult

    for i in range(10):
        fcurrent_x = math.floor(current_x)
        fcurrent_y = round(current_y)
        if CheckPointCollision(fcurrent_x, fcurrent_y)[0]:
            index = CheckPointCollision(fcurrent_x, fcurrent_y)[1]
            break
        elif CheckPointCollision(fcurrent_x,fcurrent_y-1)[0]:
            index = CheckPointCollision(fcurrent_x, fcurrent_y-1)[1]
            break
        current_x += dx
        current_y += dy
    second_distance = math.sqrt((current_x-px)**2 + (current_y-py)**2)

    fx = 0
    fy = 0
    foffset = 0
    if distance < second_distance:
        fx = x_lastx
        fy = x_lasty
        index = last_index
        foffset = fy%1
        fdir = 1
    else:
        fx = current_x
        fy = current_y
        foffset = fx%1
        fdir = 2
    foffset = math.floor(foffset*texture_size)
    fdistance = (fx - px) * math.cos(pdir) + (fy - py) * math.sin(pdir)
    if fdistance == 0:
        fdistance = 0.01

    return Ray(fdistance,index,foffset,fx,fy)
    # ---------------------------------


print("GAME START")
keys = []

while 1:
    keysDown = []
    keysUp = []
    # ------ PYGAME EVENTS ------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # ---------- INPUT -----------
        if event.type == pygame.KEYDOWN:
            if event.key not in keys:
                keys.append(event.key)

            keysDown.append(event.key)

        if event.type == pygame.KEYUP:
            if event.key in keys:
                keys.remove(event.key)

            keysUp.append(event.key)
    if pygame.K_ESCAPE in keysDown:
        pygame.quit()
        sys.exit()
    # ----------- UPDATE ------------
    key_right = pygame.K_RIGHT in keys
    key_left = pygame.K_LEFT in keys
    key_W = pygame.K_w in keys
    key_S = pygame.K_s in keys
    key_A = pygame.K_a in keys
    key_D = pygame.K_d in keys

    rotspd = speed * (key_right - key_left)
    pdir += rotspd
    pdir = adjustrad(pdir)
    if(pdir == 0):
        pdir = 0.01

    hsp = 0
    vsp = 0
    hsp += (key_W - key_S) * math.cos(pdir)
    vsp += (key_W - key_S) * math.sin(pdir)
    hsp += math.cos(pdir + degtorad(90 * (key_D - key_A))) * abs(key_D - key_A)
    vsp += math.sin(pdir + degtorad(90 * (key_D - key_A))) * abs(key_D - key_A)

    hsp *= speed
    vsp *= speed

    px += hsp

    if (CheckPointCollision(px, py)[0]):
        while(CheckPointCollision(px, py)[0]):
            sign = hsp / abs(hsp)
            px -= sign * 0.01

    py += vsp

    if (CheckPointCollision(px, py)[0]):
        while(CheckPointCollision(px, py)[0]):
            sign = vsp / abs(vsp)
            py -= sign * 0.01

    check_x = px + math.cos(pdir) * 0.5
    check_y = py + math.sin(pdir) * 0.5
    check_result = CheckPointCollision(check_x,check_y)

    if (check_result[0]) and (check_result[1] == 4) and (pygame.K_e in keysDown):
        map[math.floor(check_x)][math.floor(check_y)] = 0


    # RAYS INFO
    rays = []
    for i in range(fov):
        frad = degtorad(fov)
        rays.append(CalculateRay(px, py, adjustrad(pdir - (frad/2) + degtorad(i))))

    # -------------------------------

    # ----------- DRAW -------------
    screen.fill(colors.DARK_GREY)

    # DRAW MAP
    for x in range(mapWidth):
        for y in range(mapHeight):
            if(map[x][y] != 0):
                texture = pygtextures[map[x][y] - 1]
                screen.blit(texture,(x*tile_size,y*tile_size))

    # DRAW RAYS
    for ray in rays:
        pygame.draw.line(screen, colors.GREEN, (px*tile_size, py*tile_size),
                         (ray.x*tile_size, ray.y*tile_size), 1)
    # DRAW 3D
    line_width = int(450/fov)
    x_pos = 400
    for ray in rays:
        line_height = 200/ray.distance
        texture = textures[ray.texture_index-1]

        for i in range(texture_size):
            color = texture.getpixel((ray.texture_offset_x,i))

            pygame.draw.line(screen, color,
                (x_pos,400/2 - line_height/2 + i*(line_height/texture_size)),
                (x_pos,400/2 - line_height/2 + (i+1)*(line_height/texture_size))
                ,line_width)

        x_pos = x_pos+line_width

    # DRAW PLAYER
    pygame.draw.rect(
        screen, colors.RED, (px * tile_size-4, py * tile_size-4, 10, 10))
    pygame.draw.line(screen, colors.RED, (
        px * tile_size, py * tile_size),
        (px * tile_size + math.cos(pdir) * 15, py * tile_size + math.sin(pdir) * 15), 3)

    # FLIP SCREEN
    pygame.display.flip()
    # ------------------------------
    clock.tick(60.0)
