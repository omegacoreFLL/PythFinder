
'''import pygame

pygame.init()
run = True
_input = 0

screen = pygame.display.set_mode((500, 400))

def isNumber(event):
    if event.key == pygame.K_0:
        return 0
    if event.key == pygame.K_1:
        return 1
    if event.key == pygame.K_2:
        return 2
    if event.key == pygame.K_3:
        return 3
    if event.key == pygame.K_4:
        return 4
    if event.key == pygame.K_5:
        return 5
    if event.key == pygame.K_6:
        return 6
    if event.key == pygame.K_7:
        return 7
    if event.key == pygame.K_8:
        return 8
    if event.key == pygame.K_9:
        return 9
    return None

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # do something with _input and then reset it
                _input = ""
            elif isNumber(event) is not None:
                new = _input * 10 + isNumber(event)
                if new < 101:
                    _input = new
            elif event.key is pygame.K_BACKSPACE and not _input == 0:
                _input = int(_input / 10)

    screen.fill("black")

    pygame.display.update()    
    
    print(_input)'''

from ev3sim.Components.BetterClasses.edgeDetectorEx import *
from ev3sim.Components.controls import *

DpadDetector = {
    Dpad.UP : EdgeDetectorEx(),
    Dpad.DOWN : EdgeDetectorEx()
}


DpadDetector[Dpad.UP].set(True)

for det in DpadDetector:
    DpadDetector[det].update()

print(DpadDetector[Dpad.UP].rising)