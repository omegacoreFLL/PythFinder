from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Components.Menu.main import *
from ev3sim.Components.Menu.buttons import *
from ev3sim.Components.Menu.enums import *
from ev3sim.Components.controls import *

class RangeManager():
    def __init__(self, range: MenuType):
        self.invertedX = BooleanEx(False)
        self.invertedY = BooleanEx(False)

        self.setRange(range)
    
    def setRange(self, range: MenuType):
        self.range = range
        self.invertedX.set(range.value[2])
        self.invertedY.set(range.value[3])

    def getMinX(self):
        try: return self.range.value[0][0]
        except: return None
    
    def getMaxX(self):
        try: return self.range.value[0][1]
        except: return None
    
    def getMinY(self):
        try: return self.range.value[1][0]
        except: return None
    
    def getMaxY(self):
        try: return self.range.value[1][1]
        except: None
    

    def increaseX(self, x):
        if self.invertedX.compare():
            new = max(self.getMinX(), x - 1)

            if new == self.getMinX() and new != x - 1:
                return new, True
            return new, False
        
        new = min(self.getMaxX(), x + 1)

        if new == self.getMaxX() and new != x + 1:
            return new, True
        return new, False
    
    def decreaseX(self, x):
        if self.invertedX.compare():
            new = min(self.getMaxX(), x + 1)

            if new == min(self.getMaxX()) and new != x + 1:
                return new, True
            return new, False
        
        new = max(self.getMinX(), x - 1)

        if new == self.getMinX() and new != x - 1:
                return new, True
        return new, False
    

    def increaseY(self, y):
        if self.invertedY.compare():
            new = max(self.getMinY(), y - 1)
            if new == self.getMinY():
                return new, True
            return new, False
        
        new = min(self.getMaxY(), y + 1)
        if new == self.getMaxY():
            return new, True
        return new, False

    def decreaseY(self, y):
        if self.invertedY.compare():
            new = min(self.getMaxY(), y + 1)

            if new == min(self.getMaxY()) and new != y + 1:
                return new, True
            return new, False
        
        new = max(self.getMinY(), y - 1)

        if new == self.getMinY() and new != y - 1:
                return new, True
        return new, False

class Menu():
    def __init__(self, constants: Constants):
        self.selected = Selected.ON_MAIN_PAGE
        self.range = RangeManager(MenuType.MAIN_MENU)
        self.selected_value = (0, -1)

        self.input_text = "_"
        self.input_bool = BooleanEx(False)
        self.input_detector = EdgeDetectorEx()

        self.just_numbers = BooleanEx(False)

        self.last_range = None
        self.last_invertedX = None
        self.last_invertedY = None

        self.controls = None
        self.screen = None
        self.constants = constants

        self.upper_bar = UpperBar(constants)
        self.main_menu = MainMenu(constants)

        self.selection_menu = SelectionMenu(constants)
        self.robot_menu = RobotMenu(constants)
        self.interface_menu = InterfaceMenu(constants)
        self.trail_menu = TrailMenu(constants)
        self.pathing_menu = PathingMenu(constants)
        self.other_menu = OtherMenu(constants)

    def reset(self):
        self.selected = Selected.ON_MAIN_PAGE
        self.range.setRange(MenuType.MAIN_MENU)
        self.selected_value = (0, -1)

        self.main_menu.enabled.set(True)
        self.selection_menu.enabled.set(False)
        self.robot_menu.enabled.set(False)
        self.interface_menu.enabled.set(False)
        self.trail_menu.enabled.set(False)
        self.pathing_menu.enabled.set(False)
        self.other_menu.enabled.set(False)

        self.range.invertedX.set(False)
        self.range.invertedY.set(False)


 
    def onScreen(self, screen, controls: Controls):  
        self.controls = controls
        self.screen = screen

        self.input_detector.set(self.input_bool.get())
        self.input_detector.update()

        self.__updateSelections()
        self.__updateClick()
        self.__setSelections()
        self.__updateInputText()

        self.main_menu.onScreen(screen)
        self.upper_bar.onScreen(screen)

        self.robot_menu.onScreen(screen)
        self.interface_menu.onScreen(screen)
        self.trail_menu.onScreen(screen)
        self.pathing_menu.onScreen(screen)
        self.other_menu.onScreen(screen)

        self.selection_menu.onScreen(screen)
    


    def __updateSelections(self):
        if self.input_bool.compare():
            return 0
        
        key = self.__updatePressedDpad()
        x, y = self.selected_value

        if key is Dpad.UP:
            y = self.range.increaseY(y)
        elif key is Dpad.DOWN:
            y = self.range.decreaseY(y)
        elif key is Dpad.LEFT:
            x = self.range.decreaseX(x)
        elif key is Dpad.RIGHT:
            x = self.range.increaseX(x)
        
        try: 
            self.selected = Selected((x, y))
            
            if self.selection_menu.enabled.compare(False) and self.selected is Selected.ROBOT:
                raise Exception("wise words here")
        except: 
            if self.range.range is MenuType.MAIN_MENU:
                self.selected = Selected((x - 1, y))
            elif self.range.range is MenuType.OTHER_MENU:
                if x >= 50 and y == 0:
                    self.selected = Selected((0, 0))
                elif x < 50 and y == 1:
                    self.selected = Selected((50, 1))
            elif self.range.range is MenuType.ROBOT_MENU:
                if x >= 10 and y == 0:
                    self.selected = Selected((0, 0))
                elif y == 1:
                    self.selected = Selected((10, 1))
            
        finally: 
            self.selected_value = self.selected.value

    def __updateInputText(self):
        self.robot_menu.setText(self.input_text)

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
        else:
            return self.controls.keybinds.updateDpad(self.controls.joystick.get_hat(0))

        return None

    def __updateClick(self):
        if self.controls.joystick_detector[self.controls.keybinds.zero_button].rising:
            self.other_menu.setClick(True)
            if self.selected is Selected.HOME_BUTTON:

                self.selection_menu.enabled.set(False)
                self.robot_menu.enabled.set(False)
                self.interface_menu.enabled.set(False)
                self.trail_menu.enabled.set(False)
                self.pathing_menu.enabled.set(False)
                self.other_menu.enabled.set(False)
                self.main_menu.enabled.set(True)

                self.selected = Selected.ON_MAIN_PAGE
                self.selected_value = self.selected.value

                self.range.setRange(MenuType.MAIN_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(False)

            elif self.selected is Selected.MENU_BUTTON:

                self.selection_menu.enabled.negate()
                
                if self.selection_menu.enabled.compare():
                    self.last_range = self.range.range
                    self.last_invertedX = self.range.invertedX.get()
                    self.last_invertedY = self.range.invertedY.get()

                    self.range.setRange(MenuType.SELECTION_MENU)
                    self.range.invertedX.set(False)
                    self.range.invertedY.set(True)
                else:
                    self.range.setRange(self.last_range)
                    self.range.invertedX.set(self.last_invertedX)
                    self.range.invertedY.set(self.last_invertedY)

            elif self.selected is Selected.ROBOT:

                self.selected = Selected.ROBOT_PATH
                self.selected_value = self.selected.value

                self.robot_menu.enabled.set(True)
                self.other_menu.setClick(False)

                self.main_menu.enabled.set(False)
                self.selection_menu.enabled.set(False)
                self.interface_menu.enabled.set(False)
                self.trail_menu.enabled.set(False)
                self.pathing_menu.enabled.set(False)
                self.other_menu.enabled.set(False)

                self.range.setRange(MenuType.ROBOT_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(True)

            elif self.selected is Selected.INTERFACE:

                self.interface_menu.enabled.set(True)

                self.main_menu.enabled.set(False)
                self.selection_menu.enabled.set(False)
                self.robot_menu.enabled.set(False)
                self.trail_menu.enabled.set(False)
                self.pathing_menu.enabled.set(False)
                self.other_menu.enabled.set(False)

                self.range.setRange(MenuType.MAIN_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(False)

            elif self.selected is Selected.TRAIL:

                self.trail_menu.enabled.set(True)

                self.main_menu.enabled.set(False)
                self.selection_menu.enabled.set(False)
                self.interface_menu.enabled.set(False)
                self.robot_menu.enabled.set(False)
                self.pathing_menu.enabled.set(False)
                self.other_menu.enabled.set(False)

                self.range.setRange(MenuType.MAIN_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(False)
            
            elif self.selected is Selected.PATHING:

                self.pathing_menu.enabled.set(True)

                self.main_menu.enabled.set(False)
                self.selection_menu.enabled.set(False)
                self.interface_menu.enabled.set(False)
                self.trail_menu.enabled.set(False)
                self.robot_menu.enabled.set(False)
                self.other_menu.enabled.set(False)

                self.range.setRange(MenuType.MAIN_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(False)
            
            elif self.selected is Selected.OTHER:

                self.selected = Selected.FIELD_CENTRIC
                self.selected_value = self.selected.value

                self.other_menu.enabled.set(True)
                self.other_menu.setClick(False)

                self.main_menu.enabled.set(False)
                self.selection_menu.enabled.set(False)
                self.interface_menu.enabled.set(False)
                self.trail_menu.enabled.set(False)
                self.pathing_menu.enabled.set(False)
                self.robot_menu.enabled.set(False)

                self.range.setRange(MenuType.OTHER_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(True)
            
            elif self.selected is Selected.FIELD_CENTRIC:
                #self.constants.FIELD_CENTRIC.negate()
                if self.constants.FIELD_CENTRIC.compare(False):
                    self.constants.FORWARDS.set(True)
            
            elif self.selected is Selected.ROBOT_BORDER:
                self.constants.DRAW_ROBOT_BORDER.negate()
            
            elif self.selected is Selected.SCREEN_BORDER:
                self.constants.USE_SCREEN_BORDER.negate()
    
            elif self.selected is Selected.ROBOT_PATH:
                self.robot_menu.input_source_bool.negate()
                self.input_bool.negate()

                if self.robot_menu.input_source_bool.compare():
                    self.input_text = "_"
                    self.just_numbers.set(False)
                
            elif self.selected is Selected.ROBOT_WIDTH:
                self.robot_menu.input_width_bool.negate()
                self.input_bool.negate()

                if self.robot_menu.input_width_bool.compare():
                    self.input_text = "_"
                    self.just_numbers.set(True)
            
            elif self.selected is Selected.ROBOT_HEIGHT:
                self.robot_menu.input_height_bool.negate()
                self.input_bool.negate()

                if self.robot_menu.input_height_bool.compare():
                    self.input_text = "_"
                    self.just_numbers.set(True)

            elif self.selected is Selected.ROBOT_SCALE:
                self.robot_menu.input_scale_bool.negate()
                self.input_bool.negate()

                if self.robot_menu.input_scale_bool.compare():
                    self.input_text = "_"
                    self.just_numbers.set(True)
        else: self.other_menu.setClick(False)

        if self.controls.joystick_detector[self.controls.keybinds.erase_trail_button].rising:
            if self.selected is Selected.FIELD_CENTRIC:
                self.constants.FIELD_CENTRIC.set(default_field_centric)

            elif self.selected is Selected.ROBOT_BORDER:
                self.constants.DRAW_ROBOT_BORDER.set(default_draw_robot_border)
            
            elif self.selected is Selected.SCREEN_BORDER:
                self.constants.USE_SCREEN_BORDER.set(default_use_screen_border)
            
            elif self.selected is Selected.ROBOT_PATH:
                self.constants.ROBOT_IMG_SOURCE = default_robot_image_source
                self.constants.recalculate.set(True)
            
            elif self.selected is Selected.ROBOT_WIDTH:
                self.constants.ROBOT_WIDTH = default_robot_width_cm
                self.constants.recalculate.set(True)

            elif self.selected is Selected.ROBOT_HEIGHT:
                self.constants.ROBOT_HEIGHT = default_robot_height_cm
                self.constants.recalculate.set(True)
            
            elif self.selected is Selected.ROBOT_SCALE:
                self.constants.ROBOT_SCALE = default_robot_scaling_factor
                self.constants.recalculate.set(True)
            

    
    def stopTextReciever(self):
        self.robot_menu.input_source_bool.set(False)
        self.robot_menu.input_height_bool.set(False)
        self.robot_menu.input_width_bool.set(False)
        self.robot_menu.input_scale_bool.set(False)

    def __setSelections(self):
        self.upper_bar.setSelection(self.selected)
        self.main_menu.setSelection(self.selected)

        self.selection_menu.setSelection(self.selected)
        self.robot_menu.setSelection(self.selected)
        self.interface_menu.setSelection(self.selected)
        self.trail_menu.setSelection(self.selected)
        self.pathing_menu.setSelection(self.selected)
        self.other_menu.setSelection(self.selected)

    def recalculate(self):
        self.upper_bar.recalculate()
        self.main_menu.recalculate()

        self.selection_menu.recalculate()
        self.robot_menu.recalculate()
        self.interface_menu.recalculate()
        self.trail_menu.recalculate()
        self.pathing_menu.recalculate()
        self.other_menu.recalculate()

    def isDigit(self, value):
        return (value == pygame.K_0 or 
                value == pygame.K_1 or
                value == pygame.K_2 or
                value == pygame.K_3 or
                value == pygame.K_4 or 
                value == pygame.K_5 or
                value == pygame.K_6 or
                value == pygame.K_7 or
                value == pygame.K_8 or 
                value == pygame.K_9)


class UpperBar():
    def __init__(self, constants: Constants):
        self.constants = constants
        self.selected = None

        self.home_button_img_rect = img_home_button.get_rect()
        self.menu_button_img_rect = img_menu_button.get_rect()

        self.recalculate()

    def setSelection(self, selected: Selected):
        self.selected = selected

    def recalculate(self):
        self.home_button_img_rect.center = (self.constants.screen_size.half_w + 400, self.constants.screen_size.half_h - 300)
        self.menu_button_img_rect.center = (self.constants.screen_size.half_w - 400, self.constants.screen_size.half_h - 300)

    def onScreen(self, screen):
        if self.selected is Selected.HOME_BUTTON:
            home_button_image = img_selected_home_button
        else: home_button_image = img_home_button

        if self.selected is Selected.MENU_BUTTON:
            menu_button_image = img_selected_menu_button
        else: menu_button_image = img_menu_button

        screen.blit(home_button_image, self.home_button_img_rect)
        screen.blit(menu_button_image, self.menu_button_img_rect)

class MainMenu():
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(False)
        self.constants = constants
        self.selected = None

        self.main_menu_img_rect = img_main_menu.get_rect()
        self.general_menu_img_rect = img_general_menu.get_rect()

        self.recalculate()
    
    def setSelection(self, selected: Selected):
        self.selected = selected

    def recalculate(self):
        self.main_menu_img_rect.center = self.constants.screen_size.getHalf()
        self.general_menu_img_rect.center = self.constants.screen_size.getHalf()
    
    def onScreen(self, screen):
        if self.enabled.compare():
            screen.blit(img_main_menu, self.main_menu_img_rect)
        else: screen.blit(img_general_menu, self.general_menu_img_rect)
    


class SelectionMenu():
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(False)
        self.constants = constants
        self.selected = None

        self.menu_img_rect = img_selection_menu.get_rect()
        self.robot_btn_rect = img_robot_button.get_rect()
        self.interface_btn_rect = img_interface_button.get_rect()
        self.trail_btn_rect = img_trail_button.get_rect()
        self.pathing_btn_rect = img_pathing_button.get_rect()
        self.other_btn_rect = img_other_button.get_rect()

        self.recalculate()



    def setSelection(self, selected: Selected):
        self.selected = selected
    
    def recalculate(self):
        self.menu_img_rect.center = (self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 7)
        self.robot_btn_rect.center = (self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 150)
        self.interface_btn_rect.center = (self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h - 60)
        self.trail_btn_rect.center = (self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h + 27)
        self.pathing_btn_rect.center = (self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h + 115)
        self.other_btn_rect.center = (self.constants.screen_size.half_w - 273, self.constants.screen_size.half_h + 200)



    def onScreen(self, screen):
        if self.enabled.compare(False):
            return 0

        screen.blit(img_selection_menu, self.menu_img_rect)

        if self.selected is Selected.ROBOT:
            robot_img = img_selected_robot_button
        else: robot_img = img_robot_button

        if self.selected is Selected.INTERFACE:
            interface_img = img_selected_interface_button
        else: interface_img = img_interface_button

        if self.selected is Selected.TRAIL:
            trail_img = img_selected_trail_button
        else: trail_img = img_trail_button

        if self.selected is Selected.PATHING:
            pathing_img = img_selected_pathing_button
        else: pathing_img = img_pathing_button

        if self.selected is Selected.OTHER:
            other_img = img_selected_other_button
        else: other_img = img_other_button

        screen.blit(robot_img, self.robot_btn_rect)
        screen.blit(interface_img, self.interface_btn_rect)
        screen.blit(trail_img, self.trail_btn_rect)
        screen.blit(pathing_img, self.pathing_btn_rect)
        screen.blit(other_img, self.other_btn_rect)

class RobotMenu():  
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(False)
        self.constants = constants
        self.selected = None
        self.text = None

        self.input_source_bool = BooleanEx(False)
        self.input_width_bool = BooleanEx(False)
        self.input_height_bool = BooleanEx(False)
        self.input_scale_bool = BooleanEx(False)

        self.input_source = EdgeDetectorEx()
        self.input_width = EdgeDetectorEx()
        self.input_height = EdgeDetectorEx()
        self.input_scale = EdgeDetectorEx()


        self.path_font = pygame.font.SysFont(default_system_font, 40)
        self.path_text = None
        self.path_text_rect = None

        self.size_font = pygame.font.SysFont(default_system_font, 70)
        self.width_text = None
        self.width_text_rect = None

        self.height_text = None
        self.height_text_rect = None

        self.scale_text = None
        self.scale_text_rect = None

        self.input_source_text = None
        self.input_width_text = None
        self.input_height_text = None
        self.input_scale_text = None

        self.scale_rect = img_scale.get_rect()
        self.width_rect = img_width.get_rect()
        self.height_rect = img_height.get_rect()

        self.path_quadrant_rect = img_path_quadrant.get_rect()
        self.scale_quadrant_rect = img_specs_quadrant.get_rect()
        self.width_quadrant_rect = img_specs_quadrant.get_rect()
        self.height_quadrant_rect = img_specs_quadrant.get_rect()

        self.robot_path_rect = img_robot_image_path.get_rect()
        self.robot_indicator_rect = img_robot_indicator.get_rect()

        self.recalculate()
    


    def setSelection(self, selected: Selected):
        self.selected = selected
    
    def setText(self, text: str):
        self.text = text



    def recalculate(self):

        self.robot_indicator_rect.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h - 297)
        self.path_quadrant_rect.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h - 110)
        self.height_quadrant_rect.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h + 170)
        self.width_quadrant_rect.center = (self.constants.screen_size.half_w - 260, self.constants.screen_size.half_h + 170)
        self.scale_quadrant_rect.center = (self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 170)

        self.robot_path_rect.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h - 155)

        self.height_rect.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h + 112)
        self.width_rect.center = (self.constants.screen_size.half_w - 256, self.constants.screen_size.half_h + 112)
        self.scale_rect.center = (self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 112)



    def inputSource(self):
        self.input_source.set(self.input_source_bool.get())
        self.input_source.update()

        if self.input_source.low:
            self.input_source_text = self.constants.ROBOT_IMG_SOURCE 
            return 0

        if self.input_source.falling:
            try:
                pygame.image.load(self.input_source_text)
                self.constants.ROBOT_IMG_SOURCE = self.input_source_text
                self.constants.recalculate.set(True)
            except:
                pass
        
        text_length = len(self.text)

        if text_length <= 40:
            self.input_source_text = self.text
        else: self.input_source_text = "..." + self.text[text_length - 40:]
        
    def inputWidth(self):
        self.input_width.set(self.input_width_bool.get())
        self.input_width.update()

        if self.input_width.low:
            self.input_width_text = str(self.constants.ROBOT_WIDTH)
            return 0
        
        if self.input_width.falling:
            try:
                if int(self.input_width_text) > 4:
                    self.constants.ROBOT_WIDTH = int(self.input_width_text)
                else: self.constants.ROBOT_WIDTH = 5
                
                self.constants.recalculate.set(True)
            except:
                pass
        
        try:
            if int(self.text) < 101:
                self.input_width_text = self.text
        except:
            self.input_width_text = self.text

    def inputHeight(self):
        self.input_height.set(self.input_height_bool.get())
        self.input_height.update()

        if self.input_height.low:
            self.input_height_text = str(self.constants.ROBOT_HEIGHT)
            return 0
        
        if self.input_height.falling:
            try:
                if int(self.input_height_text) > 4:
                    self.constants.ROBOT_HEIGHT = int(self.input_height_text)
                else: self.constants.ROBOT_HEIGHT = 5

                self.constants.recalculate.set(True)
            except:
                pass
        
        try:
            if int(self.text) < 101:
                self.input_height_text = self.text
        except:
            self.input_height_text = self.text

    def inputScale(self):
        self.input_scale.set(self.input_scale_bool.get())
        self.input_scale.update()

        if self.input_scale.low:
            self.input_scale_text = str(int(self.constants.ROBOT_SCALE * 100))
            return 0
        
        if self.input_scale.falling:
            try:
                if int(self.input_scale_text) > 9:
                    self.constants.ROBOT_SCALE = int(self.input_scale_text) / 100
                else: self.constants.ROBOT_SCALE = 0.1

                self.constants.recalculate.set(True)
            except:
                pass
        
        try:
            if int(self.text) < 201:
                self.input_scale_text = self.text
        except:
            self.input_scale_text = self.text
    


    def onScreen(self, screen):
        if self.enabled.compare(False):
            return 0
        
        self.inputSource()
        self.inputWidth()
        self.inputHeight()
        self.inputScale()

        self.path_text = self.path_font.render(self.input_source_text, True, default_text_color)
        self.path_text_rect = self.path_text.get_rect()
        self.path_text_rect.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h - 60)

        self.width_text = self.size_font.render(self.input_width_text + ' cm', True, default_text_color)
        self.width_text_rect =  self.width_text.get_rect()
        self.width_text_rect.center = (self.constants.screen_size.half_w - 260, self.constants.screen_size.half_h + 235)

        self.height_text = self.size_font.render(self.input_height_text + ' cm', True, default_text_color)
        self.height_text_rect = self.height_text.get_rect()
        self.height_text_rect.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h + 235)

        self.scale_text = self.size_font.render(self.input_scale_text + '%', True, default_text_color)
        self.scale_text_rect = self.scale_text.get_rect()
        self.scale_text_rect.center = (self.constants.screen_size.half_w + 260, self.constants.screen_size.half_h + 235)
        
        if self.selected is Selected.ROBOT_PATH:
            robot_path_img = img_selected_robot_image_path
        else: robot_path_img = img_robot_image_path

        if self.selected is Selected.ROBOT_WIDTH:
            robot_width_img = img_selected_width
        else: robot_width_img = img_width

        if self.selected is Selected.ROBOT_HEIGHT:
            robot_height_img = img_selected_height
        else: robot_height_img = img_height

        if self.selected is Selected.ROBOT_SCALE:
            robot_scale_img = img_selected_scale
        else: robot_scale_img = img_scale
        
        screen.blit(img_robot_indicator, self.robot_indicator_rect)
        screen.blit(img_path_quadrant, self.path_quadrant_rect)

        screen.blit(img_specs_quadrant, self.width_quadrant_rect)
        screen.blit(img_specs_quadrant, self.height_quadrant_rect)
        screen.blit(img_specs_quadrant, self.scale_quadrant_rect)

        screen.blit(robot_path_img, self.robot_path_rect)
        screen.blit(robot_width_img, self.width_rect)
        screen.blit(robot_height_img, self.height_rect)
        screen.blit(robot_scale_img, self.scale_rect)

        screen.blit(self.path_text, self.path_text_rect)
        screen.blit(self.width_text, self.width_text_rect)
        screen.blit(self.height_text, self.height_text_rect)
        screen.blit(self.scale_text, self.scale_text_rect)



class InterfaceMenu():  
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(False)
        self.constants = constants
        self.selected = None

        self.recalculate()
    
    def setSelection(self, selected: Selected):
        self.selected = selected
    
    def recalculate(self):
        pass
    
    def onScreen(self, screen):
        if self.enabled.compare(False):
            return 0
        pass

class TrailMenu():  
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(False)
        self.constants = constants
        self.selected = None

        self.recalculate()
    
    def setSelection(self, selected: Selected):
        self.selected = selected
    
    def recalculate(self):
        pass
    
    def onScreen(self, screen):
        if self.enabled.compare(False):
            return 0
        pass

class PathingMenu():  
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(False)
        self.constants = constants
        self.selected = None

        self.recalculate()
    
    def setSelection(self, selected: Selected):
        self.selected = selected
    
    def recalculate(self):
        pass
    
    def onScreen(self, screen):
        if self.enabled.compare(False):
            return 0
        pass

class OtherMenu():
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(False)
        self.constants = constants
        self.selected = None

        self.fc_quadrant_rect = img_other_quadrant.get_rect()
        self.field_centric_rect = img_field_centric_on.get_rect()

        self.rb_quadrant_rect = img_other_quadrant.get_rect()
        self.robot_border_rect = img_robot_border_on.get_rect()

        self.sb_quadrant_rect = img_other_quadrant.get_rect()
        self.screen_border_rect = img_screen_border_on.get_rect()

        self.n4_quadrant_rect = img_other_quadrant.get_rect()
        self.n5_quadrant_rect = img_other_quadrant.get_rect()
        self.n6_quadrant_rect = img_other_quadrant.get_rect()
        self.n7_quadrant_rect = img_other_quadrant.get_rect()
        self.n8_quadrant_rect = img_other_quadrant.get_rect()

        self.none4_rect = img_none.get_rect()
        self.none5_rect = img_none.get_rect()
        self.none6_rect = img_none.get_rect()
        self.none7_rect = img_none.get_rect()
        self.none8_rect = img_none.get_rect()

        self.other_indicator_rect = img_other_indicator.get_rect()

        self.recalculate()
    
    def setSelection(self, selected: Selected):
        self.selected = selected

    def recalculate(self):
        self.other_indicator_rect.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h - 297)

        self.field_centric_rect.center = (self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 140)
        self.fc_quadrant_rect.center = (self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 150)
        
        self.robot_border_rect.center = (self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 10)
        self.rb_quadrant_rect.center = (self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h - 20) 
        
        self.screen_border_rect.center = (self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 120)
        self.sb_quadrant_rect.center = (self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 110) 
        
        self.none4_rect.center = (self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 250)
        self.n4_quadrant_rect.center = (self.constants.screen_size.half_w - 173, self.constants.screen_size.half_h + 240) 
        


        self.none5_rect.center = (self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 145)
        self.n5_quadrant_rect.center = (self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 150)

        self.none6_rect.center = (self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 15)
        self.n6_quadrant_rect.center = (self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h - 20)

        self.none7_rect.center = (self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 115)
        self.n7_quadrant_rect.center = (self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 110)

        self.none8_rect.center = (self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 245)
        self.n8_quadrant_rect.center = (self.constants.screen_size.half_w + 173, self.constants.screen_size.half_h + 240)


    def __getFieldCentricImg(self):
        if self.selected is Selected.FIELD_CENTRIC:
            if self.constants.FIELD_CENTRIC.compare():
                return img_selected_field_centric_on
            return img_selected_field_centric_off
        
        if self.constants.FIELD_CENTRIC.compare():
                return img_field_centric_on
        return img_field_centric_off

    def setClick(self, val: bool):
        self.click = val

    def __getRobotBorderImg(self):
        if self.selected is Selected.ROBOT_BORDER:
            if self.constants.DRAW_ROBOT_BORDER.compare():
                return img_selected_robot_border_on
            return img_selected_robot_border_off
        
        if self.constants.DRAW_ROBOT_BORDER.compare():
            return img_robot_border_on
        return img_robot_border_off

    def __getScreenBorderImg(self):
        if self.selected is Selected.SCREEN_BORDER:
            if self.constants.USE_SCREEN_BORDER.compare():
                return img_selected_screen_border_on
            return img_selected_screen_border_off
        
        if self.constants.USE_SCREEN_BORDER.compare():
            return img_screen_border_on
        return img_screen_border_off
    
    def __getNone(self, number: int):
        if self.selected is Selected["OTHER_NONE{0}".format(number)]:
            return img_selected_none
        return img_none
    
    def onScreen(self, screen: pygame.Surface):
        if self.enabled.compare(False):
            return 0
        
        screen.blit(img_other_indicator, self.other_indicator_rect)

        screen.blit(self.__getFieldCentricImg(), self.field_centric_rect)
        screen.blit(img_other_quadrant, self.fc_quadrant_rect)

        screen.blit(self.__getRobotBorderImg(), self.robot_border_rect)
        screen.blit(img_other_quadrant, self.rb_quadrant_rect)

        screen.blit(self.__getScreenBorderImg(), self.screen_border_rect)
        screen.blit(img_other_quadrant, self.sb_quadrant_rect)

        screen.blit(self.__getNone(4), self.none4_rect)
        screen.blit(img_other_quadrant, self.n4_quadrant_rect)
        screen.blit(self.__getNone(5), self.none5_rect)
        screen.blit(img_other_quadrant, self.n5_quadrant_rect)
        screen.blit(self.__getNone(6), self.none6_rect)
        screen.blit(img_other_quadrant, self.n6_quadrant_rect)
        screen.blit(self.__getNone(7), self.none7_rect)
        screen.blit(img_other_quadrant, self.n7_quadrant_rect)
        screen.blit(self.__getNone(8), self.none8_rect)
        screen.blit(img_other_quadrant, self.n8_quadrant_rect)




