from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Components.controls import *
from enum import Enum
 
 #(MIN, MAX)
class Range(Enum):
    MAIN_MENU = ((0, 1), (-1,0))
    SELECTION_MENU = ((0, 0), (0, 5))
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

    FIELD_CENTRIC = (50, 1)
    ROBOT_BORDER = (50, 2)
    SCREEN_BORDER = (50, 3)
    OTHER_NONE4  = (50, 4)

    OTHER_NONE5 = (51, 1)
    OTHER_NONE6 = (51, 2)
    OTHER_NONE7 = (51, 3)
    OTHER_NONE8 = (51, 4)






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
        self.range.setRange(Range.MAIN_MENU)
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

        self.__updateSelections()
        self.__updateClick()
        self.__setSelections()

        self.main_menu.onScreen(screen)
        self.upper_bar.onScreen(screen)

        self.robot_menu.onScreen(screen)
        self.interface_menu.onScreen(screen)
        self.trail_menu.onScreen(screen)
        self.pathing_menu.onScreen(screen)
        self.other_menu.onScreen(screen)

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
            
            if self.selection_menu.enabled.compare(False) and self.selected is Selected.ROBOT:
                raise Exception("wise words here")
        except: 
            if self.range.range is Range.MAIN_MENU:
                self.selected = Selected((x - 1, y))
            elif self.range.range is Range.OTHER_MENU:
                if x >= 50 and y == 0:
                    self.selected = Selected((0, 0))
                elif x < 50 and y == 1:
                    self.selected = Selected((50, 1))
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
                self.other_menu.enabled.set(False)
                self.main_menu.enabled.set(True)

                self.selected = Selected.ON_MAIN_PAGE
                self.selected_value = self.selected.value

                self.range.setRange(Range.MAIN_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(False)

            elif self.selected is Selected.MENU_BUTTON:

                self.selection_menu.enabled.negate()
                
                if self.selection_menu.enabled.compare():
                    self.last_range = self.range.range
                    self.last_invertedX = self.range.invertedX.get()
                    self.last_invertedY = self.range.invertedY.get()

                    self.range.setRange(Range.SELECTION_MENU)
                    self.range.invertedX.set(False)
                    self.range.invertedY.set(True)
                else:
                    self.range.setRange(self.last_range)
                    self.range.invertedX.set(self.last_invertedX)
                    self.range.invertedY.set(self.last_invertedY)

            elif self.selected is Selected.ROBOT:

                self.robot_menu.enabled.set(True)

                self.main_menu.enabled.set(False)
                self.selection_menu.enabled.set(False)
                self.interface_menu.enabled.set(False)
                self.trail_menu.enabled.set(False)
                self.pathing_menu.enabled.set(False)
                self.other_menu.enabled.set(False)

                self.range.setRange(Range.MAIN_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(False)

            elif self.selected is Selected.INTERFACE:

                self.interface_menu.enabled.set(True)

                self.main_menu.enabled.set(False)
                self.selection_menu.enabled.set(False)
                self.robot_menu.enabled.set(False)
                self.trail_menu.enabled.set(False)
                self.pathing_menu.enabled.set(False)
                self.other_menu.enabled.set(False)

                self.range.setRange(Range.MAIN_MENU)
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

                self.range.setRange(Range.MAIN_MENU)
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

                self.range.setRange(Range.MAIN_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(False)
            
            elif self.selected is Selected.OTHER:

                self.selected = Selected.FIELD_CENTRIC
                self.selected_value = self.selected.value

                self.other_menu.enabled.set(True)

                self.main_menu.enabled.set(False)
                self.selection_menu.enabled.set(False)
                self.interface_menu.enabled.set(False)
                self.trail_menu.enabled.set(False)
                self.pathing_menu.enabled.set(False)
                self.robot_menu.enabled.set(False)

                self.range.setRange(Range.OTHER_MENU)
                self.range.invertedX.set(False)
                self.range.invertedY.set(True)
            
            elif self.selected is Selected.FIELD_CENTRIC:
                self.constants.FIELD_CENTRIC.negate()
                if self.constants.FIELD_CENTRIC.compare(False):
                    self.constants.FORWARDS.set(True)
            
            elif self.selected is Selected.ROBOT_BORDER:
                self.constants.DRAW_ROBOT_BORDER.negate()
            
            elif self.selected is Selected.SCREEN_BORDER:
                self.constants.USE_SCREEN_BORDER.negate()
    


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

        self.recalculate()
    
    def setSelection(self, selected: Selected):
        self.selected = selected
    
    def recalculate(self):
        pass
    
    def onScreen(self, screen):
        if self.enabled.compare(False):
            return 0
        pass

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
        
        self.recalculate()
    
    def setSelection(self, selected: Selected):
        self.selected = selected

    def recalculate(self):
        self.field_centric_rect.center = (self.constants.screen_size.half_w - 190, self.constants.screen_size.half_h - 140)
        self.fc_quadrant_rect.center = (self.constants.screen_size.half_w - 190, self.constants.screen_size.half_h - 150)
        
        self.robot_border_rect.center = (self.constants.screen_size.half_w - 190, self.constants.screen_size.half_h - 10)
        self.rb_quadrant_rect.center = (self.constants.screen_size.half_w - 190, self.constants.screen_size.half_h - 20) 
        
        self.screen_border_rect.center = (self.constants.screen_size.half_w - 190, self.constants.screen_size.half_h + 120)
        self.sb_quadrant_rect.center = (self.constants.screen_size.half_w - 190, self.constants.screen_size.half_h + 110) 
        
        self.none4_rect.center = (self.constants.screen_size.half_w - 190, self.constants.screen_size.half_h + 250)
        self.n4_quadrant_rect.center = (self.constants.screen_size.half_w - 190, self.constants.screen_size.half_h + 240) 
        


        self.none5_rect.center = (self.constants.screen_size.half_w + 190, self.constants.screen_size.half_h - 145)
        self.n5_quadrant_rect.center = (self.constants.screen_size.half_w + 190, self.constants.screen_size.half_h - 150)

        self.none6_rect.center = (self.constants.screen_size.half_w + 190, self.constants.screen_size.half_h - 15)
        self.n6_quadrant_rect.center = (self.constants.screen_size.half_w + 190, self.constants.screen_size.half_h - 20)

        self.none7_rect.center = (self.constants.screen_size.half_w + 190, self.constants.screen_size.half_h + 115)
        self.n7_quadrant_rect.center = (self.constants.screen_size.half_w + 190, self.constants.screen_size.half_h + 110)

        self.none8_rect.center = (self.constants.screen_size.half_w + 190, self.constants.screen_size.half_h + 245)
        self.n8_quadrant_rect.center = (self.constants.screen_size.half_w + 190, self.constants.screen_size.half_h + 240)


    def __getFieldCentricImg(self):
        if self.selected is Selected.FIELD_CENTRIC:
            if self.constants.FIELD_CENTRIC.compare():
                return img_selected_field_centric_on
            return img_selected_field_centric_off
        
        if self.constants.FIELD_CENTRIC.compare():
                return img_field_centric_on
        return img_field_centric_off

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
    
    def onScreen(self, screen):
        if self.enabled.compare(False):
            return 0

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




