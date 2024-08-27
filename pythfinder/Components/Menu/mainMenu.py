from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Components.Constants.constants import *
from pythfinder.Components.Menu.buttons import *
from pythfinder.Components.Menu.menus import *
from pythfinder.Components.Menu.enums import *
from pythfinder.Components.controls import *


# file combining all the logic for the menu


class Menu(AbsMenu):
    def __init__(self, 
                 name: MenuType, 
                 constants: Constants, 
                 controls: Controls,
                 background: pygame.Surface | None, 
                 always_display: bool = False, 
                 overlap: bool = False):

        super().__init__(name, constants, background, always_display, overlap)

        self.controls = controls
        self.selected = Selected.ON_MAIN_PAGE # default selection when entering the menu

        self.clicked = False
        self.value = '_'

        self.create() # creates each button for each menu
        self.recalculate() # calculates the dimension of each button's afferent image

        self.menus = [self.main_menu, self.robot_menu, self.other_menu, self.upper_bar, self.selection_menu] 
        self.main_menu.ENABLED.set(True)




    def create_main_menu(self):
        self.MAIN_PAGE = EmptyButton(name = Selected.ON_MAIN_PAGE,
                                    quadrant_surface = None,
                                    title_surface = None, 
                                    selected_title_surface = None)
        
        self.MAIN_PAGE.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.MENU_BUTTON, None, None, None))
        
        self.main_menu = Submenu(MenuType.MAIN_MENU, self.constants, img_main_menu)
    
    def recalculate_main_menu(self):
        self.main_menu.set_buttons([self.MAIN_PAGE])
        self.main_menu.background_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h))
    

    def create_upper_bar(self):
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
        

        
        self.MENU.link_toggle(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (None, None, Selected.ROBOT, None))
        
        self.MENU.remember(key = Dpad.DOWN, value = Selected.ON_MAIN_PAGE)
        self.HOME.remember_as_button(self.MENU)
    

        self.upper_bar = Submenu(MenuType.UPPER_BAR, self.constants, None, always_display = True)
        self.upper_bar.ENABLED.set(True)
    
    def recalculate_upper_bar(self):
        self.MENU.title_center((self.constants.screen_size.half_w - 400, self.constants.screen_size.half_h - 300))
        self.HOME.title_center((self.constants.screen_size.half_w + 400, self.constants.screen_size.half_h - 300))

        self.upper_bar.set_buttons([self.MENU, self.HOME])


    def create_selection_menu(self):
        self.ROBOT = DynamicButton(name = Selected.ROBOT,
                                quadrant_surface = None,
                                title_surface = img_robot_button,
                                selected_title_surface = img_selected_robot_button)
        
        self.INTERFACE = DynamicButton(name = Selected.INTERFACE,
                                quadrant_surface = None,
                                title_surface = img_interface_button,
                                selected_title_surface = img_selected_interface_button)

        self.DRAW = DynamicButton(name = Selected.DRAW,
                                quadrant_surface = None,
                                title_surface = img_draw_button,
                                selected_title_surface = img_selected_draw_button)
    
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
                        next = Selected.ROBOT_IMG_SOURCE)
        self.INTERFACE.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.ROBOT, None, Selected.DRAW, None),
                        next = None)
        self.DRAW.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.INTERFACE, None, Selected.PATHING, None),
                        next = None)
        self.PATHING.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.DRAW, None, Selected.OTHER, None),
                        next = None)
        self.OTHER.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                        value = (Selected.PATHING, None, Selected.ROBOT, None),
                        next = Selected.FIELD_CENTRIC)
        
        self.selection_menu = Submenu(MenuType.SELECTION_MENU, self.constants, img_selection_menu, overlap = True)
        
    def recalculate_selection_menu(self):
        self.ROBOT.title_center((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 145))
        self.INTERFACE.title_center((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 56))
        self.DRAW.title_center((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h + 27))
        self.PATHING.title_center((self.constants.screen_size.half_w - 271, self.constants.screen_size.half_h + 120))
        self.OTHER.title_center((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h + 207))

        self.selection_menu.set_buttons([self.ROBOT, self.INTERFACE, self.DRAW, self.PATHING, self.OTHER])
        self.selection_menu.background_center((self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 7))


    def create_robot_menu(self):
        self.ROBOT_IMG_SOURCE = InputButton(name = Selected.ROBOT_IMG_SOURCE,
                                quadrant_surface = img_path_quadrant,
                                title_surface = img_robot_image_path,
                                selected_title_surface = img_selected_robot_image_path,
                                size = 40, value = self.constants.ROBOT_IMG_SOURCE,
                                limit = 40,
                                constants = self.constants)
        
        self.ROBOT_WIDTH = InputButton(name = Selected.ROBOT_WIDTH,
                                quadrant_surface = img_specs_quadrant,
                                title_surface = img_width,
                                selected_title_surface = img_selected_width,
                                size = 70, value = self.constants.ROBOT_WIDTH,
                                constants = self.constants)
        
        self.ROBOT_HEIGHT = InputButton(name = Selected.ROBOT_HEIGHT,
                                quadrant_surface = img_specs_quadrant,
                                title_surface = img_height,
                                selected_title_surface = img_selected_height,
                                size = 70, value = self.constants.ROBOT_HEIGHT,
                                constants = self.constants)

        self.ROBOT_SCALE = InputButton(name = Selected.ROBOT_SCALE,
                                quadrant_surface = img_specs_quadrant,
                                title_surface = img_scale,
                                selected_title_surface = img_selected_scale,
                                size = 70, value = self.constants.ROBOT_SCALE,
                                constants = self.constants)
        

        self.ROBOT_IMG_SOURCE.set_input_type(InputType.IMAGE_PATH, dimension = 70)
        self.ROBOT_WIDTH.set_input_type(InputType.DIMENSION, dimension = (0, 100))
        self.ROBOT_HEIGHT.set_input_type(InputType.DIMENSION, dimension = (0, 100))
        self.ROBOT_SCALE.set_input_type(InputType.PERCENT, dimension = (0, 201))


        self.ROBOT_IMG_SOURCE.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.MENU_BUTTON, None, Selected.ROBOT_WIDTH, None))
        self.ROBOT_WIDTH.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.ROBOT_IMG_SOURCE, Selected.ROBOT_HEIGHT, None, None))
        self.ROBOT_HEIGHT.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.ROBOT_IMG_SOURCE, Selected.ROBOT_SCALE, None, Selected.ROBOT_WIDTH))
        self.ROBOT_SCALE.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                            value = (Selected.ROBOT_IMG_SOURCE,None, None, Selected.ROBOT_HEIGHT))
        
        self.robot_menu = Submenu(MenuType.ROBOT_MENU, self.constants, img_general_menu, indicator = img_robot_indicator)

    def recalculate_robot_menu(self):
        self.ROBOT_IMG_SOURCE.title_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h - 155))
        self.ROBOT_WIDTH.title_center((self.constants.screen_size.half_w - 256, self.constants.screen_size.half_h + 112))
        self.ROBOT_HEIGHT.title_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h + 112))
        self.ROBOT_SCALE.title_center((self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 112))

        self.ROBOT_IMG_SOURCE.quadrant_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h - 110))
        self.ROBOT_WIDTH.quadrant_center((self.constants.screen_size.half_w - 260, self.constants.screen_size.half_h + 170))
        self.ROBOT_HEIGHT.quadrant_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h + 170))
        self.ROBOT_SCALE.quadrant_center((self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 170))
                                        
        self.ROBOT_IMG_SOURCE.value_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h - 60))
        self.ROBOT_WIDTH.value_center((self.constants.screen_size.half_w - 260, self.constants.screen_size.half_h + 235))
        self.ROBOT_HEIGHT.value_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h + 235))
        self.ROBOT_SCALE.value_center((self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 235))

        self.robot_menu.set_buttons([self.ROBOT_IMG_SOURCE, self.ROBOT_WIDTH, self.ROBOT_HEIGHT, self.ROBOT_SCALE])
        self.robot_menu.background_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h))
        self.robot_menu.indicator_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h - 300))


    def create_other_menu(self):
        self.FIELD_CENTRIC = BoolButton(name = Selected.FIELD_CENTRIC,
                                    constants = self.constants,
                                    value = self.constants.FIELD_CENTRIC,
                                    quadrant_surface = img_other_quadrant,
                                    title_surface = [img_field_centric_off, img_field_centric_on],
                                    selected_title_surface = [img_selected_field_centric_off, img_selected_field_centric_on])

        self.ROBOT_BORDER = BoolButton(name = Selected.ROBOT_BORDER,
                                    constants = self.constants,  
                                    value = self.constants.ROBOT_BORDER,
                                    quadrant_surface = img_other_quadrant,
                                    title_surface = [img_robot_border_off, img_robot_border_on],
                                    selected_title_surface = [img_selected_robot_border_off, img_selected_robot_border_on])
        
        self.SCREEN_BORDER = BoolButton(name = Selected.SCREEN_BORDER,
                                    constants = self.constants,
                                    value = self.constants.SCREEN_BORDER,
                                    quadrant_surface = img_other_quadrant,
                                    title_surface = [img_screen_border_off, img_screen_border_on],
                                    selected_title_surface = [img_selected_screen_border_off, img_selected_screen_border_on])

        self.HAND_DRAWING = BoolButton(name = Selected.HAND_DRAWING,
                                 constants = self.constants,
                                 value = self.constants.HAND_DRAWING,
                                 quadrant_surface = img_other_quadrant,
                                 title_surface = [img_hand_drawing_off, img_hand_drawing_on],
                                 selected_title_surface = [img_selected_hand_drawing_off, img_selected_hand_drawing_on])
        
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
                                value = (Selected.ROBOT_BORDER, Selected.OTHER_NONE7, Selected.HAND_DRAWING, None))
        self.HAND_DRAWING.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.SCREEN_BORDER, Selected.OTHER_NONE8, None, None))
        

        self.NONE5.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.MENU_BUTTON, None, Selected.OTHER_NONE6, Selected.FIELD_CENTRIC))
        self.NONE6.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.OTHER_NONE5, None, Selected.OTHER_NONE7, Selected.ROBOT_BORDER))
        self.NONE7.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.OTHER_NONE6, None, Selected.OTHER_NONE8, Selected.SCREEN_BORDER))
        self.NONE8.link(key = (Dpad.UP, Dpad.RIGHT, Dpad.DOWN, Dpad.LEFT),
                                value = (Selected.OTHER_NONE7, None, None, Selected.HAND_DRAWING))

        self.other_menu = Submenu(MenuType.OTHER_MENU, self.constants, img_general_menu, indicator = img_other_indicator)

    def recalculate_other_menu(self):

        self.FIELD_CENTRIC.title_center((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 140))
        self.ROBOT_BORDER.title_center((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 10))
        self.SCREEN_BORDER.title_center((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 120))
        self.HAND_DRAWING.title_center((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 244))

        self.NONE5.title_center((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 145))
        self.NONE6.title_center((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 15))
        self.NONE7.title_center((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 115))
        self.NONE8.title_center((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 245))


        self.FIELD_CENTRIC.quadrant_center((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 150))
        self.ROBOT_BORDER.quadrant_center((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 20))
        self.SCREEN_BORDER.quadrant_center((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 110))
        self.HAND_DRAWING.quadrant_center((self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 240)) 

        self.NONE5.quadrant_center((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 150))
        self.NONE6.quadrant_center((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 20))
        self.NONE7.quadrant_center((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 110))
        self.NONE8.quadrant_center((self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 240))


        self.other_menu.set_buttons([self.FIELD_CENTRIC, self.ROBOT_BORDER, self.SCREEN_BORDER, self.HAND_DRAWING,
                                    self.NONE5, self.NONE6, self.NONE7, self.NONE8])
        self.other_menu.background_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h))
        self.other_menu.indicator_center((self.constants.screen_size.half_w, self.constants.screen_size.half_h - 295))




    # called everytime when reentering the menu
    def reset(self):
        self.selected = Selected.ON_MAIN_PAGE
        self.enable()

    def create(self):
        self.create_main_menu()
        self.create_robot_menu()
        self.create_other_menu()
        self.create_upper_bar()
        self.create_selection_menu()

    def recalculate(self):
        self.recalculate_main_menu()
        self.recalculate_robot_menu()
        self.recalculate_other_menu()
        self.recalculate_upper_bar()
        self.recalculate_selection_menu()

    def check(self):
        for menu in self.menus:
            menu.check()
    
    def update(self):
        return None


    def enable(self):
        
        for menu in self.menus: # first check in overlapping is allowed
            if self.selected in menu.name.value and (menu.always_display or menu.overlap):
                return 0

        for menu in self.menus: # else shut down every other menu, keep the selected one
            menu.reset_toggles()

            if self.selected in menu.name.value:
                menu.ENABLED.set(True)
                
            else: menu.ENABLED.set(False)

    def add_key(self, key):
        self.value = key

    def on_screen(self, screen: pygame.Surface):
        self.__reset_buttons_default()

        try: self.clicked = self.controls.joystick_detector[self.controls.keybinds.zero_button].rising
        except: self.clicked = False                                            
        self.clicked = self.clicked or self.controls.keyboard_detector[pygame.K_RETURN].rising

        try: self.default = self.controls.joystick_detector[self.controls.keybinds.erase_trail_button].rising
        except: self.default = False
        self.default = self.default or self.controls.keyboard_detector[pygame.K_TAB].rising

        key = self.__update_pressed_dpad()
        moved = False

        for menu in self.menus: # loop through each menu
            menu.update(self.selected, self.clicked, default = self.default, value = self.value)
            toggles = menu.get_toggles()

            for item in toggles: # enable all the menus the toggle buttons say you to do
                for each in self.menus:
                    if item[0] is each.name:
                        each.ENABLED.set(item[1])
                

            next = menu.update_selections(key) # gets the next button to move to
            if next is not None and not moved: # you can move only once / loop, because otherwise things go boom
                
                if key is not None:
                    inverse = Controls.Keybinds.inverse(key)
                    for each in self.menus: # check in all the menus, in all the buttons
                        for button in each.buttons: # the desired next button, to see if has to remember the move
                            if button.remember_links[inverse][0] and button.name is next: 
                                try: 
                                    if not button.on()[1]:
                                        raise("wise words here")
                                except: button.remember_links[inverse][1] = self.selected

                self.selected = next
                self.enable() # update menus
                moved = True

            menu.on_screen(screen)


    def __update_pressed_dpad(self):
        if self.controls.joystick is not None:
            if self.controls.keybinds.state is JoyType.PS4:
                    if self.controls.joystick_detector[self.controls.keybinds.turn_0].rising:
                        return Dpad.UP
                    elif self.controls.joystick_detector[self.controls.keybinds.turn_90].rising:
                        return Dpad.RIGHT
                    elif self.controls.joystick_detector[self.controls.keybinds.turn_180].rising:
                        return Dpad.DOWN
                    elif self.controls.joystick_detector[self.controls.keybinds.turn_270].rising:
                        return Dpad.LEFT

            else:
                key = self.controls.keybinds.update_dpad(self.controls.joystick.get_hat(0))

                if key is not None:
                    return key
                return self.controls.get_arrow()
        
        return self.controls.get_arrow()
    
    def __reset_buttons_default(self):
        if not self.constants.reset_buttons_default:
            return None
        
        for menu in self.menus:
            menu.reset_buttons_default()
        
        self.constants.reset_buttons_default = False
