from enum import Enum, auto
 

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
    TRAIL = auto()
    PATHING = auto()
    OTHER = auto()

    ROBOT_PATH = auto()
    ROBOT_WIDTH = auto()
    ROBOT_HEIGHT = auto()
    ROBOT_SCALE = auto()

    FIELD_CENTRIC = auto()
    ROBOT_BORDER = auto()
    SCREEN_BORDER = auto()
    OTHER_NONE4  = auto()

    OTHER_NONE5 = auto()
    OTHER_NONE6 = auto()
    OTHER_NONE7 = auto()
    OTHER_NONE8 = auto()

class MenuType(Enum):
    UPPER_BAR = [Selected.HOME_BUTTON, Selected.MENU_BUTTON]
    MAIN_MENU = [Selected.ON_MAIN_PAGE]
    SELECTION_MENU = [Selected.ROBOT, Selected.INTERFACE, 
                      Selected.TRAIL, Selected.PATHING, Selected.OTHER]
    ROBOT_MENU = [Selected.ROBOT_PATH, Selected.ROBOT_WIDTH, Selected.ROBOT_HEIGHT, Selected.ROBOT_SCALE]
    OTHER_MENU = [Selected.FIELD_CENTRIC, Selected.ROBOT_BORDER, Selected.SCREEN_BORDER, Selected.OTHER_NONE4,
                  Selected.OTHER_NONE5, Selected.OTHER_NONE6, Selected.OTHER_NONE7, Selected.OTHER_NONE8]

    UNDEFINED = auto()

class InputType(Enum):
    DIMENSION = ' cm'
    PERCENT = '%'
    FONT = ''
    COLOR = ''
    IMAGE_PATH = ''