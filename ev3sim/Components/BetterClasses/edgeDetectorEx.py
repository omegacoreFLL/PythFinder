from BetterClasses.ErrorEx import *

#general edge detector class
class EdgeDetectorEx():
    def __init__(self):
        self.__current = False
        self.__past = False

        self.rising = False
        self.falling = False
        self.high = False
        self.low = False
    
    def set(self, current):
        isType([current], ["current"], [bool])
        self.__current = current

    def update(self):
        self.rising = not self.__past and self.__current
        self.falling = self.__past and not self.__current
        self.high = self.__past and self.__current
        self.low = not self.__past and not self.__current

        self.__past = self.__current
    
    
