from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Components.Menu.buttons import *
from ev3sim.Components.Menu.menus import *
from ev3sim.Components.Menu.enums import *
from ev3sim.Components.controls import *
import pygame



class Menu(AbsMenu):
    def __init__(self, name: MenuType, constants: Constants, background: pygame.Surface | None, 
                 always_display: bool = False, overlap: bool = False):
        super().__init__(name, constants, background, always_display, overlap)

        self.selected = Selected.ON_MAIN_PAGE

        self.clicked = False
        self.value = '_'

        self.create()
        self.recalculate()

        self.menus = [self.main_menu, self.robot_menu, self.other_menu, self.upper_bar, self.selection_menu] 
        self.main_menu.ENABLED.set(True)

    
    def createMainMenu(self):
        self.MAIN_PAGE = EmptyButton(name = Selected.ON_MAIN_PAGE,
                                    quadrant_surface = None,
                                    title_surface = None, 
                                    selected_title_surface = None)
        
        self.MAIN_PAGE.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.MENU_BUTTON, None, None, None))
        
        self.main_menu = Submenu(MenuType.MAIN_MENU, self.constants, img_main_menu)
    
    def recalculateMainMenu(self):
        self.main_menu.setButtons([self.MAIN_PAGE])
        self.main_menu.backgroundCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h))
    

    def createUpperBar(self):
        self.MENU = ToggleButton(name = Selected.MENU_BUTTON,
                                quadrant_surface = None,
                                title_surface = img_menu_button,
                                selected_title_surface = img_selected_menu_button,
                                toggle = MenuType.SELECTION_MENU)
        
        self.HOME = DynamicButton(name = Selected.HOME_BUTTON,
                                quadrant_surface = None,
                                title_surface = img_home_button,
                                selected_title_surface = img_selected_home_button)
        
        
        self.MENU.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (None, Selected.HOME_BUTTON, Selected.ON_MAIN_PAGE, None))
        self.HOME.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (None, None, Selected.ON_MAIN_PAGE, Selected.MENU_BUTTON),
                        next = Selected.ON_MAIN_PAGE)
        

        
        self.MENU.linkToggle(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (None, None, Selected.ROBOT, None))
        
        self.MENU.remember(key = Dpad.DOWN, value = Selected.ON_MAIN_PAGE)
        self.HOME.rememberAsButton(self.MENU)
    

        self.upper_bar = Submenu(MenuType.UPPER_BAR, self.constants, None, always_display = True)
        self.upper_bar.ENABLED.set(True)
    
    def recalculateUpperBar(self):
        self.MENU.titleCenter((self.constants.screen_size.half_w - 400, self.constants.screen_size.half_h - 300))
        self.HOME.titleCenter((self.constants.screen_size.half_w + 400, self.constants.screen_size.half_h - 300))

        self.upper_bar.setButtons([self.MENU, self.HOME])


    def createSelectionMenu(self):
        self.ROBOT = DynamicButton(name = Selected.ROBOT,
                                quadrant_surface = None,
                                title_surface = img_robot_button,
                                selected_title_surface = img_selected_robot_button)
        
        self.INTERFACE = DynamicButton(name = Selected.INTERFACE,
                                quadrant_surface = None,
                                title_surface = img_interface_button,
                                selected_title_surface = img_selected_interface_button)

        self.TRAIL = DynamicButton(name = Selected.TRAIL,
                                quadrant_surface = None,
                                title_surface = img_trail_button,
                                selected_title_surface = img_selected_trail_button)
    
        self.PATHING = DynamicButton(name = Selected.PATHING,
                                quadrant_surface = None,
                                title_surface = img_pathing_button,
                                selected_title_surface = img_selected_pathing_button)

        self.OTHER = DynamicButton(name = Selected.OTHER,
                                quadrant_surface = None,
                                title_surface = img_other_button,
                                selected_title_surface = img_selected_other_button)

        self.ROBOT.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.MENU_BUTTON, None, Selected.INTERFACE, None),
                        next = Selected.ROBOT_PATH)
        self.INTERFACE.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.ROBOT, None, Selected.TRAIL, None),
                        next = None)
        self.TRAIL.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.INTERFACE, None, Selected.PATHING, None),
                        next = None)
        self.PATHING.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.TRAIL, None, Selected.OTHER, None),
                        next = None)
        self.OTHER.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.PATHING, None, Selected.ROBOT, None),
                        next = Selected.FIELD_CENTRIC)
        
        self.selection_menu = Submenu(MenuType.SELECTION_MENU, self.constants, img_selection_menu, overlap = True)
        
    def recalculateSelectionMenu(self):
        self.ROBOT.titleCenter((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 150))
        self.INTERFACE.titleCenter((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 60))
        self.TRAIL.titleCenter((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h + 27))
        self.PATHING.titleCenter((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h + 115))
        self.OTHER.titleCenter((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h + 200))

        self.selection_menu.setButtons([self.ROBOT, self.INTERFACE, self.TRAIL, self.PATHING, self.OTHER])
        self.selection_menu.backgroundCenter((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 7))


    def createRobotMenu(self):
        self.ROBOT_PATH = InputButton(name = Selected.ROBOT_PATH,
                                quadrant_surface = img_path_quadrant,
                                title_surface = img_robot_image_path,
                                selected_title_surface = img_selected_robot_image_path,
                                size = 40, value = self.constants.ROBOT_IMG_SOURCE)
        
        self.ROBOT_WIDTH = InputButton(name = Selected.ROBOT_WIDTH,
                                quadrant_surface = img_specs_quadrant,
                                title_surface = img_width,
                                selected_title_surface = img_selected_width,
                                size = 70, value = self.constants.ROBOT_WIDTH)
        
        self.ROBOT_HEIGHT = InputButton(name = Selected.ROBOT_HEIGHT,
                                quadrant_surface = img_specs_quadrant,
                                title_surface = img_height,
                                selected_title_surface = img_selected_height,
                                size = 70, value = self.constants.ROBOT_HEIGHT)

        self.ROBOT_SCALE = InputButton(name = Selected.ROBOT_SCALE,
                                quadrant_surface = img_specs_quadrant,
                                title_surface = img_scale,
                                selected_title_surface = img_selected_scale,
                                size = 70, value = self.constants.ROBOT_SCALE * 100)
        

        self.ROBOT_PATH.setInputType(InputType.IMAGE_PATH, dimension = 70)
        self.ROBOT_WIDTH.setInputType(InputType.DIMENSION, dimension = (0, 100))
        self.ROBOT_HEIGHT.setInputType(InputType.DIMENSION, dimension = (0, 100))
        self.ROBOT_SCALE.setInputType(InputType.PERCENT, dimension = (0, 200))


        self.ROBOT_PATH.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.MENU_BUTTON, None, Selected.ROBOT_WIDTH, None))
        self.ROBOT_WIDTH.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.ROBOT_PATH, Selected.ROBOT_HEIGHT, None, None))
        self.ROBOT_HEIGHT.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.ROBOT_PATH, Selected.ROBOT_SCALE, None, Selected.ROBOT_WIDTH))
        self.ROBOT_SCALE.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.ROBOT_PATH,None, None, Selected.ROBOT_HEIGHT))
        
        self.robot_menu = Submenu(MenuType.ROBOT_MENU, self.constants, img_general_menu)

    def recalculateRobotMenu(self):
        self.ROBOT_PATH.titleCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h - 155))
        self.ROBOT_WIDTH.titleCenter((self.constants.screen_size.half_w - 256, self.constants.screen_size.half_h + 112))
        self.ROBOT_HEIGHT.titleCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h + 112))
        self.ROBOT_SCALE.titleCenter((self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 112))

        self.ROBOT_PATH.quadrantCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h - 110))
        self.ROBOT_WIDTH.quadrantCenter((self.constants.screen_size.half_w - 260, self.constants.screen_size.half_h + 170))
        self.ROBOT_HEIGHT.quadrantCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h + 170))
        self.ROBOT_SCALE.quadrantCenter((self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 170))
                                        
        self.ROBOT_PATH.valueCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h - 60))
        self.ROBOT_WIDTH.valueCenter((self.constants.screen_size.half_w - 260, self.constants.screen_size.half_h + 235))
        self.ROBOT_HEIGHT.valueCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h + 235))
        self.ROBOT_SCALE.valueCenter((self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 235))

        self.robot_menu.setButtons([self.ROBOT_PATH, self.ROBOT_WIDTH, self.ROBOT_HEIGHT, self.ROBOT_SCALE])
        self.robot_menu.backgroundCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h))



    def createOtherMenu(self):
        self.FIELD_CENTRIC = BoolButton(name = Selected.FIELD_CENTRIC,
                                    value = self.constants.FIELD_CENTRIC,
                                    quadrant_surface = img_other_quadrant,
                                    title_surface = [img_field_centric_off, img_field_centric_on],
                                    selected_title_surface = [img_selected_field_centric_off, img_selected_field_centric_on])

        self.ROBOT_BORDER = BoolButton(name = Selected.ROBOT_BORDER,
                                    value = self.constants.DRAW_ROBOT_BORDER,
                                   quadrant_surface = img_other_quadrant,
                                    title_surface = [img_robot_border_off, img_robot_border_on],
                                    selected_title_surface = [img_selected_robot_border_off, img_selected_robot_border_on])
        
        self.SCREEN_BORDER = BoolButton(name = Selected.SCREEN_BORDER,
                                    value = self.constants.USE_SCREEN_BORDER,
                                    quadrant_surface = img_other_quadrant,
                                    title_surface = [img_screen_border_off, img_screen_border_on],
                                    selected_title_surface = [img_selected_screen_border_off, img_selected_screen_border_on])

        self.NONE4 = EmptyButton(name = Selected.OTHER_NONE4,
                                quadrant_surface = img_other_quadrant,
                                title_surface = img_none,
                                selected_title_surface = img_selected_none)
        
        self.NONE5 = EmptyButton(name = Selected.OTHER_NONE5,
                                quadrant_surface = img_other_quadrant,
                                title_surface = img_none,
                                selected_title_surface = img_selected_none)

        self.NONE6 = EmptyButton(name = Selected.OTHER_NONE6,
                                quadrant_surface = img_other_quadrant,
                                title_surface = img_none,
                                selected_title_surface = img_selected_none)

        self.NONE7 = EmptyButton(name = Selected.OTHER_NONE7,
                                quadrant_surface = img_other_quadrant,
                                title_surface = img_none,
                                selected_title_surface = img_selected_none)

        self.NONE8 = EmptyButton(name = Selected.OTHER_NONE8,
                                quadrant_surface = img_other_quadrant,
                                title_surface = img_none,
                                selected_title_surface = img_selected_none)
        
        
        self.FIELD_CENTRIC.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.MENU_BUTTON, Selected.OTHER_NONE5, Selected.ROBOT_BORDER, None))
        self.ROBOT_BORDER.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.FIELD_CENTRIC, Selected.OTHER_NONE6, Selected.SCREEN_BORDER, None))
        self.SCREEN_BORDER.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.ROBOT_BORDER, Selected.OTHER_NONE7, Selected.OTHER_NONE4, None))
        self.NONE4.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.SCREEN_BORDER, Selected.OTHER_NONE8, None, None))
        
        self.NONE5.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.MENU_BUTTON, None, Selected.OTHER_NONE6, Selected.FIELD_CENTRIC))
        self.NONE6.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.OTHER_NONE5, None, Selected.OTHER_NONE7, Selected.ROBOT_BORDER))
        self.NONE7.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.OTHER_NONE6, None, Selected.OTHER_NONE8, Selected.SCREEN_BORDER))
        self.NONE8.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.OTHER_NONE7, None, None, Selected.OTHER_NONE4))

        self.other_menu = Submenu(MenuType.OTHER_MENU, self.constants, img_general_menu)

    def recalculateOtherMenu(self):

        self.FIELD_CENTRIC.titleCenter((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 140))
        self.ROBOT_BORDER.titleCenter((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 10))
        self.SCREEN_BORDER.titleCenter((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 120))

        self.NONE4.titleCenter((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 250))
        self.NONE5.titleCenter((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 145))
        self.NONE6.titleCenter((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 15))
        self.NONE7.titleCenter((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 115))
        self.NONE8.titleCenter((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 245))


        self.FIELD_CENTRIC.quadrantCenter((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 150))
        self.ROBOT_BORDER.quadrantCenter((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 20))
        self.SCREEN_BORDER.quadrantCenter((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 110))

        self.NONE4.quadrantCenter((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 240))
        self.NONE5.quadrantCenter((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 150))
        self.NONE6.quadrantCenter((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 20))
        self.NONE7.quadrantCenter((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 110))
        self.NONE8.quadrantCenter((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 240))


        self.other_menu.setButtons([self.FIELD_CENTRIC, self.ROBOT_BORDER, self.SCREEN_BORDER, self.NONE4,
                                    self.NONE5, self.NONE6, self.NONE7, self.NONE8])
        self.other_menu.backgroundCenter((self.constants.screen_size.half_w, self.constants.screen_size.half_h))



    def reset(self):
        self.selected = Selected.ON_MAIN_PAGE
        self.enable()

    def create(self):
        self.createMainMenu()
        self.createRobotMenu()
        self.createOtherMenu()
        self.createUpperBar()
        self.createSelectionMenu()

    def recalculate(self):
        self.recalculateMainMenu()
        self.recalculateRobotMenu()
        self.recalculateOtherMenu()
        self.recalculateUpperBar()
        self.recalculateSelectionMenu()

    def update(self):
        ...



    def enable(self):
        #first check in overlapping is allowed
        for menu in self.menus:
            if self.selected in menu.name.value and (menu.always_display or menu.overlap):
                return 0

        for menu in self.menus:
            menu.resetToggles()

            if self.selected in menu.name.value:
                menu.ENABLED.set(True)
                
            else: menu.ENABLED.set(False)

    def shouldRecalculate(self):
        for menu in self.menus:
            for button in menu.buttons:
                try: 
                    if button.recalculate.get():
                        button.recalculate.set(False)
                        self.recalculate()
                except: pass

    def addControls(self, controls: Controls):
        self.controls = controls

    def addKey(self, key):
        self.value = key

    def onScreen(self, screen: pygame.Surface):
        self.clicked = self.controls.joystick_detector[self.controls.keybinds.zero_button].rising
        self.default = self.controls.joystick_detector[self.controls.keybinds.erase_trail_button].rising

        self.shouldRecalculate()
        key = self.__updatePressedDpad()
        moved = False

        for menu in self.menus:
            menu.update(self.selected, self.clicked, self.value)
            toggles = menu.getToggles()

            for item in toggles:
                for each in self.menus:
                    if item[0] is each.name:
                        each.ENABLED.set(item[1])
                

            next = menu.updateSelections(key)
            if not next == None and not moved: 
                
                if not key == None:
                    inverse = Controls.Keybinds.inverse(key)
                    for each in self.menus:
                        for button in each.buttons:
                            if button.remember_links[inverse][0] and button.name is next:
                                try: 
                                    if not button.on()[1]:
                                     raise("wise words here")
                                except: button.remember_links[inverse][1] = self.selected

                self.selected = next
                self.enable()
                moved = True

            menu.onScreen(screen)


    def __updatePressedDpad(self):
        if self.controls.keybinds.state is JoyType.PS4:
                if self.controls.joystick_detector[self.controls.keybinds.turn_0].rising:
                    return Dpad.UP
                elif self.controls.joystick_detector[self.controls.keybinds.turn_90].rising:
                    return Dpad.RIGHT
                elif self.controls.joystick_detector[self.controls.keybinds.turn_180].rising:
                    return Dpad.DOWN
                elif self.controls.joystick_detector[self.controls.keybinds.turn_270].rising:
                    return Dpad.LEFT

        return self.controls.keybinds.updateDpad(self.controls.joystick.get_hat(0))
