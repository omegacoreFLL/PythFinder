class EdgeDetectorEx():
    """
    A class that detects edges based on the current and past values.
    Attributes:
        rising (bool): Indicates if the edge is rising.
        falling (bool): Indicates if the edge is falling.
        high (bool): Indicates if the signal is high.
        low (bool): Indicates if the signal is low.
    Methods:
        set(current: bool): Sets the current value.
        get() -> bool: Returns the current value.
        update(): Updates the edge detection based on the current and past values.
    """

    def __init__(self):
        self.__current = False
        self.__past = False

        self.rising = False
        self.falling = False
        self.high = False
        self.low = False
    
    def set(self, 
            current: bool):
        self.__current = current
    
    def get(self):
        return self.__current

    def update(self):
        self.rising = not self.__past and self.__current
        self.falling = self.__past and not self.__current
        self.high = self.__past and self.__current
        self.low = not self.__past and not self.__current

        self.__past = self.__current
    
    
