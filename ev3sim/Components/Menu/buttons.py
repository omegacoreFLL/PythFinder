from ev3sim.Components.BetterClasses.edgeDetectorEx import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Components.Menu.enums import *
from ev3sim.Components.controls import *
from abc import ABC, abstractmethod

from typing import List
import pygame

#CONVENTION: surface list goes from smaller -> larger value (ex: FALSE -> TRUE )
class AbsButton(ABC):
    def __init__(self, name: Selected,
                 quadrant_surface: pygame.Surface | None, 
                 title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 selected_title_surface: List[pygame.Surface] | pygame.Surface | None,
                 value = None, size: int | None = None, font = default_system_font) -> None:
        self.name = name
        self.selected = None
        self.index = 0

        self.remember_other = None

        try: self.font = pygame.font.SysFont(font, size)
        except: self.font = None

        try: self.display_quadrant = quadrant_surface[self.index]
        except: self.display_quadrant = quadrant_surface

        try: self.display_title = title_surface[self.index]
        except: self.display_title = title_surface

        self.raw_value = value
        try: self.display_value = self.font.render(str(value), True, default_text_color)
        except: self.display_value = None

        try: self.display_quadrant_rect = self.display_quadrant.get_rect()
        except: self.display_quadrant_rect = None

        try: self.display_title_rect = self.display_title.get_rect()
        except: self.display_title_rect = None

        try: self.display_value_rect = self.display_value.get_rect()
        except: self.display_value_rect = None

        self.title = title_surface
        self.quadrant = quadrant_surface
        self.selected_title = selected_title_surface

        self.quadrant_center = None
        self.title_center = None
        self.value_center = None

        self.SELECTED = EdgeDetectorEx()
        self.type = self.getType()

        self.next = None
        self.links = {
            Dpad.UP: None,
            Dpad.RIGHT: None,
            Dpad.DOWN: None,
            Dpad.LEFT: None
        }
        self.remember_links = {
            Dpad.UP: [False, None],
            Dpad.RIGHT: [False, None],
            Dpad.DOWN: [False, None],
            Dpad.LEFT: [False, None]
        }



    def getType(self) -> ButtonType:
        if isinstance(self.raw_value, (int, float)):
            return ButtonType.INT
        if isinstance(self.raw_value, (bool, BooleanEx)):
            return ButtonType.BOOL
        if isinstance(self.raw_value, str):
            return ButtonType.STRING
        return ButtonType.UNDEFINED

    def link(self, key: Dpad | List[Dpad], value: Selected | List[Selected], next = None):
        try:
            if len(key) == len(value):
                for each in range(len(key)):
                    self.links[key[each]] = value[each]
        except: self.links[key] = value

        if isinstance(next, Selected):
            self.next = next
    
    def remember(self, key: Dpad | List[Dpad], value: Selected | List[Selected]):
        try:
            if len(key) == len(value):
                for each in range(len(key)):

                    if value[each] == None:
                        self.remember_links[key[each]][0] = False
                    else: self.remember_links[key[each]][0] = True

                    self.remember_links[key[each]][1] = value[each]
        except: 
            if value == None:
                self.remember_links[key][0] = False
            else: self.remember_links[key][0] = True

            self.remember_links[key][1] = value

    def rememberAsButton(self, other):
        if isinstance(other, AbsButton):
            self.remember_other = other

    def quadrantCenter(self, center: tuple):
        try: self.display_quadrant_rect.center = center
        except: pass
        finally: self.quadrant_center = center

    def titleCenter(self, center: tuple):
        try: self.display_title_rect.center = center
        except: pass
        finally: self.title_center = center
    
    def valueCenter(self, center: tuple):
        try: self.display_value_rect.center = center
        except: pass
        finally: self.value_center = center

    @abstractmethod
    def change(self):
        ...
    
    @abstractmethod
    def update(self, selected: Selected, clicked: bool, value = None):
        self.selected = selected
        ...
    
    def move(self, direction: Dpad | None) -> Selected:
        if self.selected is self.name:
            try: 
                if self.on()[1]:
                    return self.toggle_links[direction]
                raise Exception("wise words here")
            except:
                try:
                    if not self.remember_other == None:
                        if self.remember_other.remember_links[direction][0]:
                            return self.remember_other.remember_links[direction][1]
                    elif self.remember_links[direction][0]:
                        return self.remember_links[direction][1]
                
                    return self.links[direction]
                except: pass
        return None
    
    def display(self, screen: pygame.Surface):    
        try: screen.blit(self.display_quadrant, self.display_quadrant_rect) 
        except: pass

        try: screen.blit(self.display_title, self.display_title_rect)
        except: pass

        try: screen.blit(self.display_value, self.display_value_rect)
        except: pass



class EmptyButton(AbsButton):
    def __init__(self, name: Selected, quadrant_surface: pygame.Surface | None, 
                 title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 selected_title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 value=None, size=None, font=default_system_font) -> None:
        super().__init__(name, quadrant_surface, title_surface, selected_title_surface, value, size, font)
    
    def change(self):
        ...
    
    def update(self, selected, clicked: bool, value = None):
        super().update(selected, clicked, value)

        if selected is self.name:
            self.SELECTED.set(True)
        else: self.SELECTED.set(False)

        self.SELECTED.update()

        if self.SELECTED.rising:
            self.display_title = self.selected_title
        elif self.SELECTED.falling:
            self.display_title = self.title

class DynamicButton(AbsButton):
    def __init__(self, name: Selected, quadrant_surface: pygame.Surface | None, 
                 title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 selected_title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 value=None, size=None, font=default_system_font) -> None:
        super().__init__(name, quadrant_surface, title_surface, selected_title_surface, value, size, font)

        self.go_next = False
    
    def getNext(self):
        if self.go_next:
            self.go_next = False
            return self.next
        return None
    
    def change(self):
        self.go_next = True
        
    def update(self, selected: Selected, clicked: bool, value = None):
        super().update(selected, clicked, value)

        if selected is self.name:
            if clicked:
                self.change()
            self.SELECTED.set(True)
        else: self.SELECTED.set(False)

        self.SELECTED.update()

        if self.SELECTED.rising:
            self.display_title = self.selected_title
        if self.SELECTED.falling:
            self.display_title = self.title

class ToggleButton(AbsButton):
    def __init__(self, name: Selected, quadrant_surface: pygame.Surface | None, 
                 title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 selected_title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 toggle, value=None, size=None, font=default_system_font) -> None:
        super().__init__(name, quadrant_surface, title_surface, selected_title_surface, value, size, font)

        self.toggle = toggle
        self.ON = BooleanEx(False)
        self.toggle_links = {
            Dpad.UP: None,
            Dpad.RIGHT: None,
            Dpad.DOWN: None,
            Dpad.LEFT: None
        }
        if not isinstance(self.toggle, MenuType):
            raise Exception("please select a MenuType")


    def change(self):
        self.ON.negate()
    
    def linkToggle(self, key: Dpad | List[Dpad], value: Selected | List[Selected]):
        try:
            if len(key) == len(value):
                for each in range(len(key)):
                    self.toggle_links[key[each]] = value[each]
        except: self.toggle_links[key] = value

    
    def on(self):
        return (self.toggle, self.ON.get())
    
    def reset(self):
        self.ON.set(False)
    
    def update(self, selected: Selected, clicked: bool, value=None):
        super().update(selected, clicked, value)

        if selected is self.name:
            if clicked:
                self.change()
            self.SELECTED.set(True)
        else: self.SELECTED.set(False)

        self.SELECTED.update()

        if self.SELECTED.rising:
            self.display_title = self.selected_title
        if self.SELECTED.falling:
            self.display_title = self.title

class InputButton(AbsButton):
    def __init__(self, name: Selected, quadrant_surface: pygame.Surface | None, title_surface: List[pygame.Surface] | pygame.Surface | None, selected_title_surface: List[pygame.Surface] | pygame.Surface | None, value=None, size=None, font=default_system_font) -> None:
        super().__init__(name, quadrant_surface, title_surface, selected_title_surface, value, size, font)

        self.WRITING = EdgeDetectorEx()
        self.write = BooleanEx(False)

        self.type = None
        self.dimension = None
        self.input = '_'

        self.recalculate = BooleanEx(False)
    
    def setInputType(self, type: InputType, dimension: tuple | int):
        self.type = type
        self.dimension = dimension

        self.display_value = self.font.render(str(self.raw_value) + self.type.value, True, default_text_color)
        self.display_value_rect = self.display_value.get_rect()
        try: self.display_value_rect.center = self.value_center
        except: pass
    
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

    def inRange(self, value):
        try: return self.dimension[0] < value and value < self.dimension[1]
        except: pass

    def change(self):
        self.write.negate()

        if self.WRITING.rising:
            self.input = '_'
        elif self.WRITING.falling:
            match self.type:
                case InputType.DIMENSION:
                    self.raw_value = int(self.input)
                    self.recalculate.set(True)
                case InputType.PERCENT:
                    self.raw_value = int(self.input)
                    self.recalculate.set(True)
                case InputType.FONT:
                    ...
                    self.recalculate.set(True)
                case InputType.COLOR:
                    ...
                    self.recalculate.set(True)
                case InputType.IMAGE_PATH:
                    try: 
                        pygame.image.load(self.input)
                        self.raw_value = self.input
                        self.recalculate.set(True)
                    except: pass
            
            self.display_value = self.font.render(str(self.raw_value) + self.type.value, True, default_text_color)
            self.display_quadrant_rect = self.display_value.get_rect()
            self.display_title_rect.center = self.value_center

    
    def update(self, selected: Selected, clicked: bool, value = None):
        if not isinstance(self.type, InputType):
            raise Exception("please initialize {0}'s input type".format(self.name))
        super().update(selected, clicked, value)
        
        if selected is self.name:
            if clicked:
                self.change()
                self.display_title = self.selected_title
            self.SELECTED.set(True)
        else: self.SELECTED.set(False)
            

        self.WRITING.set(self.write.get())

        self.WRITING.update()
        self.SELECTED.update()

        if self.SELECTED.rising:
            self.display_title = self.selected_title
        elif self.SELECTED.falling:
            self.change()
            self.display_title = self.title
        
        if self.WRITING.high and not value == None:
            match value.key:
                case pygame.K_RETURN:
                    self.change()
                case pygame.K_BACKSPACE:
                    if len(self.input) > 1:
                        self.input = self.input[:-1]
                    else: self.input = '_'
                case _:
                    key_val = value.unicode

                    if self.input == '_':
                        match self.type:
                            case InputType.DIMENSION:
                                if self.inRange(int(key_val)):
                                    self.input = key_val
                            case InputType.PERCENT:
                                if self.inRange(int(key_val)):
                                    self.input = key_val
                            case InputType.FONT:
                                ...
                            case InputType.COLOR:
                                ...
                            case InputType.IMAGE_PATH:
                                self.input = key_val
                    else: 
                        match self.type:
                            case InputType.DIMENSION:
                                if self.inRange(int(self.input + key_val)):
                                    self.input += key_val
                            case InputType.PERCENT:
                                if self.inRange(int(self.input + key_val)):
                                    self.input += key_val
                            case InputType.FONT:
                                ...
                            case InputType.COLOR:
                                ...
                            case InputType.IMAGE_PATH:
                                if len(self.input) + 1 <= self.dimension:
                                    self.input += key_val

            self.display_value = self.font.render(str(self.input) + self.type.value, True, default_text_color)
            self.display_quadrant_rect = self.display_value.get_rect()
            self.display_title_rect.center = self.value_center
    
#must always give the 'value' as BooleanEx
class BoolButton(AbsButton):
    def __init__(self, name: Selected, quadrant_surface: pygame.Surface | None, 
                 title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 selected_title_surface: List[pygame.Surface] | pygame.Surface | None, 
                 value=None, size=None, font=default_system_font) -> None:
        super().__init__(name, quadrant_surface, title_surface, selected_title_surface, value, size, font)

        try: 
            if self.raw_value.compare():
                self.index = 1
            else: self.index = 0
        except:
            if self.raw_value:
                self.index = 1
            else: self.index = 0

        finally:
            self.display_title = self.title[self.index]

    def change(self): 
        try:
            self.raw_value.negate()

            if self.raw_value.compare():
                self.index = 1
            else: self.index = 0
        except:
            self.raw_value = not self.raw_value
            if self.raw_value:
                self.index = 1
            else: self.index = 0

    def update(self, selected, clicked: bool, value = None):
        super().update(selected, clicked, value)

        if selected is self.name:
            if clicked:
                self.change()
                self.display_title = self.selected_title[self.index]
            self.SELECTED.set(True)
        else: self.SELECTED.set(False)

        self.SELECTED.update()

        if self.SELECTED.rising:
            self.display_title = self.selected_title[self.index]
        elif self.SELECTED.falling:
            self.display_title = self.title[self.index]
