from pythfinder.Components.Controllers.PIDCoefficients import *
from pythfinder.Components.Constants.constants import *
import pygame

# generic PID controller

class PIDController():
    def __init__(self, 
                 coefficients: PIDCoefficients):
        
        self.__coeff = coefficients

        self.__proportional = 0
        self.__derivative = 0
        self.__integral = 0

        self.__current_time = 0

        self.__past_error = 0
        self.__past_time = 0
    
    def set(self, 
            coefficients: PIDCoefficients):
        self.__coeff = coefficients

    def calculate(self, 
                  error: int | float):
        
        self.__current_time = pygame.time.get_ticks()

        self.__proportional = error
        self.__derivative = (error - self.__past_error) / (self.__current_time - self.__past_time)
        self.__integral += error

        power = self.__proportional * self.__coeff.kP + self.__integral * self.__coeff.kI + self.__derivative * self.__coeff.kD 

        self.__past_time = self.__current_time
        self.__past_error = error

        return power

