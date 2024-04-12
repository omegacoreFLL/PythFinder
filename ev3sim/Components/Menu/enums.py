from enum import Enum
 
 #(MIN, MAX)
class Range(Enum):
    MAIN_MENU = ((0, 1), (-1,0))
    SELECTION_MENU = ((0, 0), (0, 5))
    ROBOT_MENU = ((10, 12), (0, 2))
    OTHER_MENU = ((50, 51), (0, 4))

# FIRST value: LEFT -> RIGHT
# SECOND value: DOWN -> UP
class Selected(Enum):
    ON_MAIN_PAGE = (0, -1)

    MENU_BUTTON = (0, 0)
    HOME_BUTTON = (1, 0)

    ROBOT = (0, 1)
    INTERFACE = (0, 2)
    TRAIL = (0, 3)
    PATHING = (0, 4)
    OTHER = (0, 5)

    ROBOT_PATH = (10, 1)
    ROBOT_WIDTH = (10, 2)
    ROBOT_HEIGHT = (11, 2)
    ROBOT_SCALE = (12, 2)

    FIELD_CENTRIC = (50, 1)
    ROBOT_BORDER = (50, 2)
    SCREEN_BORDER = (50, 3)
    OTHER_NONE4  = (50, 4)

    OTHER_NONE5 = (51, 1)
    OTHER_NONE6 = (51, 2)
    OTHER_NONE7 = (51, 3)
    OTHER_NONE8 = (51, 4)
