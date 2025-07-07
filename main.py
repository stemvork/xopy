import sys
import pygame
from pygame.locals import *

TILE_COUNT = 4
TILE_SIZE = 200
TILE_GAP = 20

def init_pygame():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.font.init()

    success = True
    if not pygame.display.get_init:
        success = False
    if not pygame.font.get_init():
        success = False
    if not pygame.mixer.get_init():
        success = False
    return success
assert init_pygame()

SCREEN_SIZE = (TILE_COUNT * TILE_SIZE, TILE_COUNT * TILE_SIZE)
game_screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('XOXO (Python)')
clock = pygame.time.Clock()

def handle_input(key_name):
    if(key_name == "q"):
       sys.exit()
def draw_grid():
    # NOTE: DRAWING ON [EXCALIDRAW](https://excalidraw.com/#json=bVlSRVxR6XCVYOoNvSSwr,YyqsxgNER24hgmbZ98famA)
    TILE_INNER_SIZE = (SCREEN_SIZE[0] - (TILE_COUNT+1)*TILE_GAP)/TILE_COUNT
    for i in range(0, TILE_COUNT+1):
        for j in range(0, TILE_COUNT+1):
            pygame.draw.rect(
                game_screen, 
                [255, 255, 255], 
                [TILE_GAP + (TILE_INNER_SIZE+TILE_GAP) * i, 
                 TILE_GAP + (TILE_INNER_SIZE+TILE_GAP) * j, 
                 TILE_INNER_SIZE, 
                 TILE_INNER_SIZE],
            )
def update(screen, time):
    draw_grid()
    pygame.display.update()

FRAME_RATE = 60.0
def main():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                key_name = pygame.key.name(event.key)
                handle_input(key_name)

        milliseconds = clock.tick(FRAME_RATE)
        seconds = milliseconds / 1000.0
        update(game_screen, seconds)

        sleep_time = (1000.0 / FRAME_RATE) - milliseconds
        if sleep_time > 0.0:
            pygame.time.wait(int(sleep_time))
        else:
            pygame.time.wait(1)
main()
