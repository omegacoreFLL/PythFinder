from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Components.controls import *
from enum import Enum
import pygame
 
 #(MIN, MAX)
class Range(Enum):
    MAIN_MENU = ((0, 1), (-1,0))
    SELECTION_MENU = ((0, 0), (0, 5))

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



class RangeManager():
    def __init__(self, range: Range):
        self.invertedX = BooleanEx(False)
        self.invertedY = BooleanEx(False)

        self.range = range
    
    def setRange(self, range: Range):
        self.range = range
    


    def getMinX(self):
        if self.range == None:
            return None
        return self.range.value[0][0]
    
    def getMaxX(self):
        if self.range == None:
            return None
        return self.range.value[0][1]
    
    def getMinY(self):
        if self.range == None:
            return None
        return self.range.value[1][0]
    
    def getMaxY(self):
        if self.range == None:
            return None
        return self.range.value[1][1]
    


    def increaseX(self, x):
        if self.invertedX.compare():
            return max(self.getMinX(), x - 1)
        return min(self.getMaxX(), x + 1)
    
    def decreaseX(self, x):
        if self.invertedX.compare():
            return min(self.getMaxX(), x + 1)
        return max(self.getMinX(), x - 1)

    def increaseY(self, y):
        if self.invertedY.compare():
            return max(self.getMinY(), y - 1)
        return min(self.getMaxY(), y + 1)

    def decreaseY(self, y):
        if self.invertedY.compare():
            return min(self.getMaxY(), y + 1)
        return max(self.getMinY(), y - 1)

        



class Menu():
    def __init__(self, constants: Constants):
        self.selected = Selected.ON_MAIN_PAGE
        self.range = RangeManager(Range.MAIN_MENU)
        self.selected_value = (0, -1)

        self.controls = None
        self.screen = None
        self.constants = constants

        self.main_menu = MainMenu(constants)
        self.selection_menu = SelectionMenu(constants)

    def reset(self):
        self.selected = Selected.ON_MAIN_PAGE
        self.range.setRange(Range.MAIN_MENU)
        self.selected_value = (0, -1)

        self.main_menu.enabled.set(True)
        self.selection_menu.enabled.set(False)

        self.range.invertedX.set(False)
        self.range.invertedY.set(False)


 
    def onScreen(self, screen, controls: Controls):  
        self.controls = controls
        self.screen = screen

        self.__updateSelections()
        self.__updateClick()
        self.__setSelections()

        self.main_menu.onScreen(screen)
        self.selection_menu.onScreen(screen)
    


    def __updateSelections(self):
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
        except: 
            if self.range.range is Range.MAIN_MENU:
                self.selected = Selected((x - 1, y))
            else: pass
        finally: 
            self.selected_value = self.selected.value

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
        else: return self.controls.keybinds.getKey(self.controls.joystick.get_hat(0))

        return None

    def __updateClick(self):
        if self.controls.joystick_detector[self.controls.keybinds.zero_button].rising:
            if self.selected is Selected.HOME_BUTTON:

                self.selection_menu.enabled.set(False)
                self.main_menu.enabled.set(True)

                self.selected = Selected.ON_MAIN_PAGE
                self.selected_value = self.selected.value

                self.range.setRange(Range.MAIN_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(False)

            elif self.selected is Selected.MENU_BUTTON:

                self.selection_menu.enabled.negate()
                
                if self.selection_menu.enabled.compare():
                    self.range.setRange(Range.SELECTION_MENU)
                    self.range.invertedX.set(False)
                    self.range.invertedY.set(True)
                else:
                    self.range.setRange(Range.MAIN_MENU)
                    self.range.invertedX.set(False)
                    self.range.invertedY.set(False)

            else:
                pass
    


    def __setSelections(self):
        self.main_menu.setSelection(self.selected)
        self.selection_menu.setSelection(self.selected)

    def setConstants(self, constants: Constants):
        self.constants = constants

        self.main_menu.setConstants(constants)
        self.selection_menu.setConstants(constants)





class MainMenu():
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(True)
        self.constants = None
        self.selected = None

        self.menu_img_rect = img_main_menu.get_rect()
        self.home_button_img_rect = img_home_button.get_rect()
        self.menu_button_img_rect = img_menu_button.get_rect()

        self.setConstants(constants)

    

    def setSelection(self, selected: Selected):
        self.selected = selected
    
    def setConstants(self, constants: Constants):
        self.constants = constants

        self.menu_img_rect.center = constants.screen_size.getHalf()
        self.home_button_img_rect.center = (constants.screen_size.half_w + 400,
                                     constants.screen_size.half_h - 300)
        self.menu_button_img_rect.center = (constants.screen_size.half_w - 400,
                                     constants.screen_size.half_h - 300)
    


    def onScreen(self, screen):
        if self.enabled.compare(False):
            return 0
        
        screen.blit(img_main_menu, self.menu_img_rect)

        if self.selected is Selected.HOME_BUTTON:
            home_button_image = img_selected_home_button
        else: home_button_image = img_home_button

        if self.selected is Selected.MENU_BUTTON:
            menu_button_image = img_selected_menu_button
        else: menu_button_image = img_menu_button

        screen.blit(home_button_image, self.home_button_img_rect)
        screen.blit(menu_button_image, self.menu_button_img_rect)

class SelectionMenu():
    def __init__(self, constants: Constants):
        self.enabled = BooleanEx(False)
        self.constants = None
        self.selected = None

        self.menu_img_rect = img_selection_menu.get_rect()
        self.robot_btn_rect = img_robot_button.get_rect()
        self.interface_btn_rect = img_interface_button.get_rect()
        self.trail_btn_rect = img_trail_button.get_rect()
        self.pathing_btn_rect = img_pathing_button.get_rect()
        self.other_btn_rect = img_other_button.get_rect()

        self.setConstants(constants)



    def setSelection(self, selected: Selected):
        self.selected = selected
    
    def setConstants(self, constants: Constants):
        self.constants = constants

        self.menu_img_rect.center = (constants.screen_size.half_w - 273,
                                     constants.screen_size.half_h - 7)
        self.robot_btn_rect.center = (constants.screen_size.half_w - 273,
                                     constants.screen_size.half_h - 150)
        self.interface_btn_rect.center = (constants.screen_size.half_w - 273,
                                     constants.screen_size.half_h - 60)
        self.trail_btn_rect.center = (constants.screen_size.half_w - 273,
                                     constants.screen_size.half_h + 27)
        self.pathing_btn_rect.center = (constants.screen_size.half_w - 273,
                                     constants.screen_size.half_h + 115)
        self.other_btn_rect.center = (constants.screen_size.half_w - 273,
                                     constants.screen_size.half_h + 200)



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
        

        

