import pygame

class CursorEx():
    """
    A class that represents an extended cursor functionality.
    Attributes:
        current_cursor (pygame.Cursor): The current cursor.
        previous_cursor (pygame.Cursor): The previous cursor.
    Methods:
        __init__(): Initializes the CursorEx object.
        apply(cursor: pygame.Cursor): Applies a custom cursor.
        apply_system(system_cursor: int): Applies a system cursor.
        throwback(): Reverts back to the previous cursor.
        compare_cursors(cursor1: pygame.Cursor, cursor2: pygame.Cursor) -> bool: Compares two cursors.
    """

    def __init__(self) -> None:
        self.current_cursor = pygame.mouse.get_cursor()
        self.previous_cursor = pygame.mouse.get_cursor()
    
    def apply(self, cursor: pygame.Cursor, remember: bool = True):
        if remember:
            self.previous_cursor = pygame.mouse.get_cursor()
        
        pygame.mouse.set_cursor(cursor)
        self.current_cursor = pygame.mouse.get_cursor()
    
    def apply_system(self, system_cursor: int, remember: bool = True):
        if remember:
            self.previous_cursor = pygame.mouse.get_cursor()

        pygame.mouse.set_system_cursor(system_cursor)
        self.current_cursor = pygame.mouse.get_cursor()
    
    def throwback(self):
        self.current_cursor = self.previous_cursor.copy()

        pygame.mouse.set_cursor(self.current_cursor)
    
    @staticmethod
    def compare_cursors(cursor: pygame.Cursor) -> bool:
        return pygame.mouse.get_cursor().data == cursor.data
