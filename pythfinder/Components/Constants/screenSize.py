import screeninfo

"""
File containing screen size data for ease of writing.

Contains:
    - Default screen dimensions
    - Limits for the screen size (could depend on the monitor size)
    - Class to store and manage screen dimensions to satisfy the limits
"""

def __get_full_screen_resolution():
    """
    Get the full screen resolution of the primary monitor.
    
    Returns:
        tuple: Width and height of the primary monitor.
    """
    try:
        monitors = screeninfo.get_monitors()
        primary_monitor = monitors[0]
        return primary_monitor.width, primary_monitor.height - 63
    except Exception as e:
        print(f"Error getting screen resolution: {e}")
        return 1920, 1017  # Default fallback resolution


DEFAULT_SCREEN_HEIGHT = 1000
DEFAULT_SCREEN_WIDTH = 1500

FLL_TABLE_SCREEN_HEIGHT = 880
FLL_TABLE_SCREEN_WIDTH = 1400

FTC_FIELD_SCREEN_HEIGHT = 1000
FTC_FIELD_SCREEN_WIDTH = 1200

MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT = __get_full_screen_resolution()
MIN_SCREEN_WIDTH = 900
MIN_SCREEN_HEIGHT = 700


class Size:
    def __init__(self, width: int = 0, height: int = 0):
        """
        Initialize the Size object.
        
        Args:
            width (int): Width of the size.
            height (int): Height of the size.
        """
        self.width = width
        self.height = height
    
    def set(self, width: int | None = None, height: int | None = None):
        """
        Set the width and height of the size.
        
        Args:
            width (int | None): New width.
            height (int | None): New height.
        """
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
    
    def get(self) -> tuple[int, int]:
        """
        Get the width and height of the size.
        
        Returns:
            tuple: Width and height.
        """
        return self.width, self.height

    def get_half(self) -> tuple[int, int]:
        """
        Get half of the width and height.
        
        Returns:
            tuple: Half of the width and height.
        """
        return self.width // 2, self.height // 2


class ScreenSize:
    def __init__(self, width: int = DEFAULT_SCREEN_WIDTH, height: int = DEFAULT_SCREEN_HEIGHT):
        """
        Initialize the ScreenSize object.
        
        Args:
            width (int): Width of the screen.
            height (int): Height of the screen.
        """
        self.width = 0
        self.height = 0

        self.half_w = 0
        self.half_h = 0

        self.MAX_WIDTH = MAX_SCREEN_WIDTH
        self.MAX_HEIGHT = MAX_SCREEN_HEIGHT

        self.MIN_WIDTH = MIN_SCREEN_WIDTH
        self.MIN_HEIGHT = MIN_SCREEN_HEIGHT

        self.set(width, height)
    
    def set(self, width: int | None = None, height: int | None = None):
        """
        Set the width and height of the screen, ensuring they are within limits.
        
        Args:
            width (int | None): New width.
            height (int | None): New height.
        """
        if width is None:
            self.width = DEFAULT_SCREEN_WIDTH
        elif width > self.MAX_WIDTH:
            self.width = self.MAX_WIDTH
        elif width < self.MIN_WIDTH:
            self.width = self.MIN_WIDTH
        else:
            self.width = width
                
        if height is None:
            self.height = DEFAULT_SCREEN_HEIGHT
        elif height > self.MAX_HEIGHT:
            self.height = self.MAX_HEIGHT
        elif height < self.MIN_HEIGHT:
            self.height = self.MIN_HEIGHT
        else:
            self.height = height
        
        self.half_h = self.height / 2
        self.half_w = self.width / 2
    
    def get(self) -> tuple[int, int]:
        """
        Get the width and height of the screen.
        
        Returns:
            tuple: Width and height.
        """
        return self.width, self.height
    
    def get_half(self) -> tuple[float, float]:
        """
        Get half of the width and height.
        
        Returns:
            tuple: Half of the width and height.
        """
        return self.half_w, self.half_h

    def copy(self) -> 'ScreenSize':
        """
        Create a copy of the ScreenSize object.
        
        Returns:
            ScreenSize: A new ScreenSize object with the same dimensions.
        """
        return ScreenSize(self.width, self.height)
    
    def is_like(self, other: 'ScreenSize') -> bool:
        """
        Check if another ScreenSize object has the same dimensions.
        
        Args:
            other (ScreenSize): Another ScreenSize object.
        
        Returns:
            bool: True if dimensions are the same, False otherwise.
        """
        return self.width == other.width and self.height == other.height