default_screen_height = 1000
default_screen_width = 1500

max_screen_height = 1000
max_screen_width = 1700
min_screen_height = 500
min_screen_width = 500


class ScreenSize():
    def __init__(self, width = default_screen_width, height = default_screen_height):
        self.width = 0
        self.height = 0

        self.half_w = 0
        self.half_h = 0

        self.MAX_WIDTH = max_screen_width
        self.MAX_HEIGHT = max_screen_height

        self.MIN_WIDTH = min_screen_width
        self.MIN_HEIGHT = min_screen_height

        self.set(width, height)
    
    def set(self, width = None, height = None):
        #check width
        if width == None:
            self.width = default_screen_width
        elif width > max_screen_width:
            self.height = int(max_screen_width * height / width)
            self.width = max_screen_width
        elif width < min_screen_width:
            self.height = int(min_screen_width * height / width)
            self.width =  min_screen_width
        else: self.width = width
                
        #check height
        if height == None:
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
    
