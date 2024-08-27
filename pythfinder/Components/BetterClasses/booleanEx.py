from enum import Enum, auto
from typing import Union

class Fun(Enum):
    SET = auto()
    GET = auto()
    NEGATE = auto()
    COMPARE = auto()


class BooleanEx():
    """
    A class representing a boolean value with additional operations.
    Attributes:
        value (bool): The boolean value.
    Methods:
        __init__(self, value: bool): Initializes the BooleanEx object with the given value.
        get(self) -> bool: Returns the current boolean value.
        set(self, new: bool): Sets the boolean value to the given new value.
        negate(self): Negates the boolean value.
        compare(self, other: bool = True) -> bool: Compares the boolean value with the given other value.
        choose(self, fun: Fun, value: bool | None = None) -> Union[None, bool]: Performs an operation based on the given function.
        Exception: If the function in choose() is not one of Fun.SET, Fun.GET, Fun.NEGATE, or Fun.COMPARE and value is not None.
    """

    def __init__(self, 
                 value: bool):
        self.__value = value
    
    def get(self):
        return self.__value
    
    def set(self, 
            new: bool):
        self.__value = new
    
    def negate(self):
        self.__value = not self.__value
    
    def compare(self, 
                other: bool = True):
        return self.__value == other
    

    def choose(self, fun: Fun, value: bool | None = None) -> Union[None, bool]:
        """
        Perform an operation based on the given function.
        Args:
            fun (Fun): The function to perform. Must be one of Fun.SET, Fun.GET, Fun.NEGATE, or Fun.COMPARE.
            value (bool | None, optional): The value to use for comparison or setting. Defaults to None.
        Returns:
            Union[None, bool]: The result of the operation. Returns None for Fun.SET, Fun.NEGATE, and invalid functions.
            Returns bool for Fun.GET and Fun.COMPARE.
        Raises:
            Exception: If the function is not one of Fun.SET, Fun.GET, Fun.NEGATE, or Fun.COMPARE and value is not None.
        """

        match fun:
            case Fun.SET:
                if value is None:
                    raise Exception("choose a boolean to be SET")
                self.set(value)
            case Fun.GET:
                return self.get()
            case Fun.NEGATE:
                self.negate()
            case Fun.COMPARE:
                if value is None:
                    return self.compare()
                else: return self.compare(value)
            case _:
                raise Exception("not a valid function")

