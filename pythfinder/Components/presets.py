from pythfinder.Components.BetterClasses.edgeDetectorEx import *
from pythfinder.Components.Constants.constants import *


# file containing the Preset class


class Preset():
    def __init__(self, 
                 name: str,
                 constants: Constants,
                 preset_constants: Constants,
                 image: None | pygame.Surface = None,
                 image_size: None | Size = None):
        
        self.name = name
        
        self.constants = constants
        self.ON = EdgeDetectorEx()

        self.original_constants = constants.copy() # deep copy
        self.preset_constants = preset_constants

        self.img = self.original = image
        self.img_size_cm: ScreenSize = image_size
        self.img_size_px: ScreenSize = None
        self.rectangle = None

        self.recalculate()
    
    def setImage(self,
                 image: None | pygame.Surface = None,
                 image_size: None | Size = None):
        
        if image is not None:
            self.img = image
        if image_size is not None:
            self.img_size_cm = image_size

    def recalculate(self):
        try:
            self.getImgSizeInPixels()

            self.img = pygame.transform.scale(self.original, 
                                              self.img_size_px.get())
            
            self.rectangle = self.img.get_rect()
            self.rectangle.center = (self.constants.screen_size.getHalf()) 
        except:
            pass # no image found
    
    def getImgSizeInPixels(self):
        self.img_size_px = Size(
                    self.constants.cmToPixels(self.img_size_cm.width),
                    self.constants.cmToPixels(self.img_size_cm.height)
        )


    def onScreen(self, screen: pygame.Surface):
        self.ON.update()

        if self.ON.high:
            try:
                screen.blit(self.img, self.rectangle)
            except: 
                pass # no image found
        
        elif self.ON.rising:
            self.constants.check(self.preset_constants)
        
        elif self.ON.falling:
            self.constants.check(self.original_constants)

class PresetManager():
    def __init__(self, presets: None | List[Preset] = None):
        if presets is not None:
            self.presets = presets
        else: self.presets = []

        self.value = None
        self.WRITING = EdgeDetectorEx()
    
    def add(self, preset: Preset, key: None | int = None):
        if key is None:
            if len(self.presets) == 9:
                print("\n\n you've reached the presets limit")
            else: self.presets.append(preset)
        else:
            if key > 0 and key < 10 and isinstance(key, int):
                self.presets[key - 1] = preset
            else: print("\n\nnot a valid key")

        return self
    
    def recalculate(self):
        for preset in self.presets:
            preset.recalculate()
    
    def addKey(self, key):
        self.value = key
    
    def on(self, number: int):
        self.presets[number-1].ON.set(True)

    def onScreen(self, screen: pygame.Surface):
        self.WRITING.update()
    
        for preset in self.presets:
            preset.onScreen(screen)

       
        if self.value is None or not self.WRITING.high:
                return None
        on = None


        match self.value.key:
            case pygame.K_1:
                on = 1
            case pygame.K_2:
                on = 2
            case pygame.K_3:
                on = 3
            case pygame.K_4:
                on = 4
            case pygame.K_5:
                on = 5
            case pygame.K_6:
                on = 6
            case pygame.K_7:
                on = 7
            case pygame.K_8:
                on = 8
            case pygame.K_9:
                on = 9
            case pygame.K_0:
                on = 0 # reset key


        if on is None:
            return None
        
        index = 0
        for preset in self.presets:
            if index + 1 == on:
                preset.ON.set(True)
            else: preset.ON.set(False)
            index += 1

