from ev3sim.Components.BetterClasses.booleanEx import *
from ev3sim.Components.Constants.constants import *

import pygame 


class Segment():
    def __init__(self, constants: Constants, points = None):
        if exists(points):
            self.points = points
        else: self.points = []

        self.hide = BooleanEx(False)

        self.constants = 0
        self.setConstants(constants)
    


    def setConstants(self, constants: Constants):
        self.constants = constants
    
    def draw(self, screen):
        if self.hide.compare(False):
            for point in range(1, len(self.points)):     
                pygame.draw.line(screen, self.constants.TRAIL_COLOR, 
                self.points[point - 1], self.points[point], width = self.constants.TRAIL_WIDTH)


class Trail():
    def __init__(self, constants: Constants):
        self.segments = [Segment(constants)]
        self.draw_trail = BooleanEx(False)
        self.hide_trail = BooleanEx(False)
        self.erase_trail = 0

        self.pop_trail_loop = 0
        self.past_trail_length = 0
        self.current_segment = 0

        self.constants = 0
        self.setConstants(constants)
    
    def setConstants(self, constants: Constants):
        self.constants = constants
        self.erase_trail = constants.ERASE_TRAIL

        for segment in self.segments:
            segment.setConstants(constants)

    '''def setColor(self, segment_number: int, color = default_trail_color):
        self.segments[segment_number].color = color
    
    def setWidth(self, segment_number: int, width = default_trail_width):
        self.segments[segment_number].width = width
    '''
    def hide(self, segment_number: int, hide = False):
        self.segments[segment_number].hide.set(hide)
    


    def eraseSegment(self, number):
        self.segments.pop(number - 1)
        self.current_segment -= 1
    
    def eraseTrail(self):
        self.segments = [Segment(self.constants)]
        self.current_segment = 0



    def drawTrail(self, screen, pose):
        if self.draw_trail.compare():
            self.buildTrail(pose)

        if self.hide_trail.compare():
            self.eraseTrail()
            self.hide_trail.set(False)
        else:
            for segment in self.segments:
                segment.draw(screen)
    
    def buildTrail(self, pose):
        trail_length = 0

        for segment in self.segments:
            trail_length += len(segment.points)

        if self.shouldErasePoint(trail_length):
            if len(self.segments[0].points) == 0:
                self.segments.pop(0)
                self.current_segment -= 1
            self.segments[0].points.pop(0)
            trail_length -= 1

        segment_length = len(self.segments[self.current_segment].points)

        if segment_length == 0:
            self.segments[self.current_segment].points.append((int(pose.x), int(pose.y)))

        elif self.segments[self.current_segment].points[segment_length - 1] != (int(pose.x), int(pose.y)):
            last_point = self.segments[self.current_segment].points[segment_length - 1]

            if distance(last_point, (int(pose.x), int(pose.y))) > self.constants.DRAW_TRAIL_THRESHOLD:
                self.segments.append(Segment(self.constants))
                self.current_segment += 1

            self.segments[self.current_segment].points.append((int(pose.x), int(pose.y)))
        
        self.past_trail_length = trail_length

    def shouldErasePoint(self, length):
        if self.erase_trail.compare(False):
            return False
        
        if length == self.past_trail_length:
            self.pop_trail_loop += 1
        else: self.pop_trail_loop = 0

        if length == self.constants.MAX_TRAIL_LEN:
            return True
        if self.pop_trail_loop >= self.constants.TRAIL_LOOPS:
            return True
    
        return False

      