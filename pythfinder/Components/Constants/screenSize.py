# file containing screen size data
#
# used for ease of writing
#
# contains:
#       - default screen dimentions
#       - limits for the screen size (could depend on the monitor size)
#       - class to store and manage screen dimensions to satisfy the limits



default_screen_height = 1000
default_screen_width = 1500

fll_table_screen_height = 880
fll_table_screen_width = 1400

ftc_field_screen_height = 1000
ftc_field_screen_width = 1200


max_screen_height = 1000
max_screen_width = 1700
min_screen_height = 700
min_screen_width = 900

class Size():
    def __init__(self, width: int = 0, height: int = 0):
        self.width = width
        self.height = height
    
    def set(self, 
            width: None | int = None,
            height: None | int = None):
        
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
    
    def get(self):
        return (self.width, self.height)

    def getHalf(self):
        return (self.width // 2, self.height // 2)

    

class ScreenSize():
    def __init__(self, 
                 width: int = default_screen_width, 
                 height: int = default_screen_height):
        
        self.width = 0
        self.height = 0

        self.half_w = 0
        self.half_h = 0

        self.MAX_WIDTH = max_screen_width
        self.MAX_HEIGHT = max_screen_height

        self.MIN_WIDTH = min_screen_width
        self.MIN_HEIGHT = min_screen_height

        self.set(width, height)
    
    def set(self, 
            width: int | None = None, 
            height: int | None = None):
        
        #check width
        if width is None:
            self.width = default_screen_width
        elif width > max_screen_width:
            self.height = int(max_screen_width * height / width)
            self.width = max_screen_width
        elif width < min_screen_width:
            self.height = int(min_screen_width * height / width)
            self.width =  min_screen_width
        else: self.width = width
                
        #check height
        if height is None:
            self.height = default_screen_height
        elif height > max_screen_height:
            self.width = int(max_screen_height * width / height)
            self.height = max_screen_height
        elif height < min_screen_height:
            self.width = int(min_screen_height * width / height)
            self.height = min_screen_height
        else: self.height = height

        #recalculate if ratio isn't maintainable
        if self.width > max_screen_width:
            self.width = max_screen_width
        elif self.width < min_screen_width:
            self.width = min_screen_width

        if self.height > max_screen_height:
            self.height = max_screen_height
        elif self.height < min_screen_height:
            self.height = min_screen_height
        
        self.half_h = self.height / 2
        self.half_w = self.width / 2
    
    def get(self):
        return (self.width, self.height)
    
    def getHalf(self):
        return (self.half_w, self.half_h)

    def copy(self):
        return ScreenSize(self.width,
                          self.height)
    
    def isLike(self, other):
        return (self.width == other.width and self.height == other.height)