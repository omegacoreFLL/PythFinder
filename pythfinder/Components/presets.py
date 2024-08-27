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
        """
        Initialize a Preset object.

        Args:
            name (str): The name of the preset.
            constants (Constants): The current constants.
            preset_constants (Constants): The preset constants.
            image (pygame.Surface | None): The image associated with the preset.
            image_size (Size | None): The size of the image in centimeters.
        """
        
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
    
    def set_image(self,
                 image: None | pygame.Surface = None,
                 image_size: None | Size = None):
        """
        Set the image and its size for the preset.

        Args:
            image (pygame.Surface | None): The new image.
            image_size (Size | None): The new size of the image in centimeters.
        """
        if image is not None:
            self.img = image
        if image_size is not None:
            self.img_size_cm = image_size

    def recalculate(self):
        """
        Recalculate the image size in pixels and update the image and its rectangle.
        """
        try:
            self.get_img_size_in_pixels()

            self.img = pygame.transform.scale(self.original, 
                                              self.img_size_px.get())
            
            self.rectangle = self.img.get_rect()
            self.rectangle.center = (self.constants.screen_size.get_half()) 
        except:
            pass # no image found
    
    def get_img_size_in_pixels(self):
        """
        Convert the image size from centimeters to pixels.
        """
        self.img_size_px = Size(
                    self.constants.cm_to_pixels(self.img_size_cm.width),
                    self.constants.cm_to_pixels(self.img_size_cm.height)
        )


    def on_screen(self, screen: pygame.Surface):
        """
        Display the image on the screen if the edge detector is high.

        Args:
            screen (pygame.Surface): The screen to display the image on.
        """
        self.ON.update()

        if self.ON.high:
            try:
                screen.blit(self.img, self.rectangle)
            except: 
                pass # no image found
        
        elif self.ON.rising:
            self.constants.check(self.preset_constants)
    
    def off(self):
        """
        Reset the constants to their original values.
        """
        self.constants.check(self.original_constants)
        

class PresetManager():
    """
    Class to manage multiple presets.

    Attributes:
        presets (List[Preset | None]): List of presets.
        value (int | None): The current key value.
        previous (int): The previous preset number.
        WRITING (EdgeDetectorEx): Edge detector for writing.
        constants (Constants): The current constants.
    """
        
    def __init__(self, constants: Constants):
        """
        Initialize a PresetManager object.

        Args:
            constants (Constants): The current constants.
        """
        self.presets: List[Preset] = [None for _ in range(10)]

        self.value = None
        self.previous = -1
        self.WRITING = EdgeDetectorEx()

        self.constants = constants
    
    def add(self, preset: Preset, key: None | int = None):
        """
        Add a preset to the manager.

        Args:
            preset (Preset): The preset to add.
            key (int | None): The key to associate with the preset.
        """
        if key is None:
            hasSpace = False

            for i in range(len(self.presets)):
                if self.presets[i] is None:

                    self.presets[i] = preset
                    hasSpace = True
                    break
            
            if not hasSpace:
                print("\n\n you've reached the presets limit")
            return self
            
        if isinstance(key, int):
            if key > 0 and key < 10:

                if self.presets[key - 1] is not None:
                    print("\n\nyou already had a preset on key {0}".format(key))
                    print("I deleted it for you, no worries, but maybe you wanted that preset 🤷🏻‍♂️")

                self.presets[key - 1] = preset 
                return self
                
        print("\n\nnot a valid key")

        return self
    
    def recalculate(self):
        """
        Recalculate all presets.
        """
        for preset in self.presets:
            if preset is not None:
                preset.recalculate()
    
    def add_key(self, key):
        """
        Add a key to the manager.

        Args:
            key: The key to add.
        """
        self.value = key
    
    def on(self, number: int):
        """
        Activate a preset by its number.

        Args:
            number (int): The number of the preset to activate.
        """
        if self.presets[number - 1] is None and not number == 0:
            print("no preset for key {0}".format(number))
            return None

        for i in range(len(self.presets)):
            if self.presets[i] is None: 
                continue
            
            if i + 1 == number:
                self.presets[i].ON.set(True)
            else: self.presets[i].ON.set(False)

            if i + 1 == self.previous and not number == self.previous:
                self.presets[i].off()
        
        self.previous = number

    

    def on_screen(self, screen: pygame.Surface):
        """
        Display all active presets on the screen.

        Args:
            screen (pygame.Surface): The screen to display the presets on.
        """
        self.WRITING.update()

        for preset in self.presets:
            if preset is not None:
                preset.on_screen(screen)

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

        self.on(on)
            
    def get(self, number: int) -> Preset:
        """
        Get a preset by its number.

        Args:
            number (int): The number of the preset to get.

        Returns:
            Preset: The preset with the specified number.
        """
        if not in_open_interval(number, 0, 9):
            return None
        return self.presets[number - 1]
