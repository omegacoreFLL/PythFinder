
from pythfinder.Components.BetterClasses.edgeDetectorEx import *
from pythfinder.Components.Constants.constants import *

class ColorPicker():
    def __init__(self, constants: Constants,
                sv_square_side_px: int = 270,
                h_slider_height_px: int = 40):
        
        self.constants = constants

        self.LENGTH = sv_square_side_px
        self.H_HEIGHT = h_slider_height_px

        self.h_center = None
        self.sv_center = None

        self.hue = 0

        self.create_sv_surface()
        self.create_hue_surface()

        self.x = 0
        self.y = 0

        self.CIRCLE_RADIUS = 8
        self.sv_position = (0, 0)                          
        self.hue_position = (0, 0)        

        self.selected_color = pygame.Color(0)
        self.CLICK_DETECTOR = EdgeDetectorEx()


    def reset(self):
        self.hue = 0
        self.create_sv_surface()

        self.sv_position = (self.sv_center[0] - self.LENGTH // 2, self.sv_center[1] - self.LENGTH // 2)                          
        self.hue_position = (self.h_center[0] - self.LENGTH // 2, self.h_center[1])

        self.selected_color = pygame.Color(0) 
    

    def set_sv_center(self, center: Tuple[int, int]):
        self.sv_center = center
        self.SV_rectangle.center = center

        self.sv_position = (center[0] - self.LENGTH // 2, center[1] - self.LENGTH // 2)
    
    def set_h_center(self, center: Tuple[int, int]):
        self.h_center = center
        self.H_rectangle.center = center

        self.hue_position = (center[0] - self.LENGTH // 2, center[1])


    def create_sv_surface(self):
        self.SV = pygame.Surface((self.LENGTH, self.LENGTH))

        self.SV_rectangle = self.SV.get_rect()
        try: self.SV_rectangle.center = self.sv_center
        except: pass

        for y in range(self.LENGTH):
            value = 1 - (y / self.LENGTH)

            for x in range(self.LENGTH):
                saturation = x / self.LENGTH

                color = pygame.Color(0)
                color.hsva = (self.hue, saturation * 100, value * 100)

                self.SV.set_at((x, y), color)

    def create_hue_surface(self):
        self.H = pygame.Surface((self.LENGTH, self.H_HEIGHT))

        self.H_rectangle = self.H.get_rect()
        try: self.H_rectangle.center = self.h_center
        except: pass

        for x in range(self.LENGTH):
            hue = (x / self.LENGTH) * 360
            color = pygame.Color(0)
            color.hsva = (hue, 100, 100)

            pygame.draw.line(self.H, color, (x, 0), (x, self.H_HEIGHT))
    
    def set(self, color: pygame.Color):
        self.hue = color.hsva[0]
        self.create_sv_surface()

        saturation = color.hsva[1] / 100
        value = color.hsva[2] / 100

        self.sv_position = (self.sv_center[0] + int((saturation - 0.5) * self.LENGTH),
                            self.sv_center[1] + int((0.5 - value) * self.LENGTH))

        self.hue_position = (self.h_center[0] + int((self.hue / 360 - 0.5) * self.LENGTH),
                             self.h_center[1])

        self.selected_color = color

    def get(self, pose: Tuple[int, int]) -> pygame.Color:

        saturation = min(max((pose[0] - self.sv_center[0] + self.LENGTH // 2) / self.LENGTH, 0), 1)  # Clamping saturation to [0, 1]
        value = min(max(1 - (pose[1] - self.sv_center[1] + self.LENGTH // 2) / self.LENGTH, 0), 1)  # Clamping value to [0, 1]

        color = pygame.Color(0)
        color.hsva = (self.hue, saturation * 100, value * 100, 100)

        return color
    

    def in_hue_slider(self, pose: Tuple[int, int]) -> bool:
        return (self.h_center[0] - self.LENGTH // 2 <= pose[0] <= self.h_center[0] + self.LENGTH // 2 
                                                        and 
                self.h_center[1] - self.H_HEIGHT // 2 <= pose[1] <= self.h_center[1] + self.H_HEIGHT // 2)

    def in_sv_square(self, pose: Tuple[int, int]) -> bool:
        return (self.sv_center[0] - self.LENGTH // 2 <= pose[0] <= self.sv_center[0] + self.LENGTH // 2
                                                        and
                self.sv_center[1] - self.LENGTH // 2 <= pose[1] <= self.sv_center[1] + self.LENGTH // 2)

    def on_screen(self, screen: pygame.Surface):
        self.CLICK_DETECTOR.set(pygame.mouse.get_pressed()[0])
        self.CLICK_DETECTOR.update()



        mouse_position = pygame.mouse.get_pos()

        if self.CLICK_DETECTOR.high:
            if self.in_hue_slider(mouse_position):
                self.hue = min(max(((mouse_position[0] - self.sv_center[0] + self.LENGTH // 2) / self.LENGTH) * 360, 0), 360)
                self.create_sv_surface()
                self.hue_position = (mouse_position[0], self.h_center[1])

                self.selected_color = self.get(self.sv_position)

            if self.in_sv_square(mouse_position):
                self.selected_color = self.get(self.sv_position)
                self.sv_position = mouse_position



        screen.blit(self.SV, self.SV_rectangle)
        screen.blit(self.H, self.H_rectangle)

        # Draw the selected color preview
        pygame.draw.rect(screen, self.selected_color, (self.h_center[0] - self.LENGTH // 2, 
                                                       self.h_center[1] + self.H_HEIGHT, 
                                                       self.LENGTH, 50))
        
        # Draw the selection circle on the SV square
        pygame.draw.circle(screen, (255, 255, 255), self.sv_position, self.CIRCLE_RADIUS, 2)
        
        # Draw the selection circle on the Hue slider
        pygame.draw.circle(screen, (255, 255, 255), self.hue_position, self.CIRCLE_RADIUS, 2)
    