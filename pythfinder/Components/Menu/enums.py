from enum import Enum, auto
 
# file containing the majority of enums used for the menus

class ButtonType(Enum):
    BOOL = auto()
    INT = auto()
    STRING = auto()
    UNDEFINED = auto()

class Selected(Enum):
    ON_MAIN_PAGE = auto()

    MENU_BUTTON = auto()
    HOME_BUTTON = auto()

    ROBOT = auto()
    INTERFACE = auto()
    DRAW = auto()
    PATHING = auto()
    OTHER = auto()

    ROBOT_IMG_SOURCE = auto()
    ROBOT_WIDTH = auto()
    ROBOT_HEIGHT = auto()
    ROBOT_SCALE = auto()

    FIELD_CENTRIC = auto()
    ROBOT_BORDER = auto()
    SCREEN_BORDER = auto()
    HAND_DRAWING  = auto()

    OTHER_NONE5 = auto()
    OTHER_NONE6 = auto()
    OTHER_NONE7 = auto()
    OTHER_NONE8 = auto()

# menus with their respective buttons
class MenuType(Enum):
    UPPER_BAR = [Selected.HOME_BUTTON, Selected.MENU_BUTTON]
    MAIN_MENU = [Selected.ON_MAIN_PAGE]
    SELECTION_MENU = [Selected.ROBOT, Selected.INTERFACE, 
                      Selected.DRAW, Selected.PATHING, Selected.OTHER]
    ROBOT_MENU = [Selected.ROBOT_IMG_SOURCE, Selected.ROBOT_WIDTH, Selected.ROBOT_HEIGHT, Selected.ROBOT_SCALE]
    OTHER_MENU = [Selected.FIELD_CENTRIC, Selected.ROBOT_BORDER, Selected.SCREEN_BORDER, Selected.HAND_DRAWING,
                  Selected.OTHER_NONE5, Selected.OTHER_NONE6, Selected.OTHER_NONE7, Selected.OTHER_NONE8]

    UNDEFINED = auto()

# inputs with their respective display extension
class InputType(Enum):
    DIMENSION = ' cm'
    PERCENT = '%'
    FONT = auto()
    COLOR = auto()
    IMAGE_PATH = auto()