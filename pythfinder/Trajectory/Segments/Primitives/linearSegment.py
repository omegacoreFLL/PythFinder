from pythfinder.Trajectory.Segments.Primitives.generic import *
from pythfinder.Trajectory.Control.feedforward import *


class LinearSegment(MotionSegment):
    def __init__(self, 
                 last_state: MotionState,
                 constraints: Constraints,
                 point_cm: Point | float):
        
        self.last_state = last_state
        self.constraints = constraints
        self.target = point_cm
        self.built = False


        if last_state is None:
            return None
        super().__init__(last_state)
        
        self.target = (point_cm if isinstance(point_cm, Point) 
                                            else 
                       self.__pointFromDistance(point_cm, self.last_state.pose.copy()))
        
        
        self.diff = self.target - last_state.pose.point()
        self.distance = round(self.diff.hypot(), 3)  # cm
        self.angle = self.diff.atan2()  # rad

        self.start_dis = self.last_state.displacement

        self.profiles.append(MotionProfile(self.distance, constraints,
                                           start_velocity = self.last_state.velocities.getVelocityMagnitude(),
                                           end_velocity = 0,
                                           start_time_ms = self.start_time,
                                           start_distance = self.last_state.displacement)
        )
        


    def addConstraintsSegmTime(self, time: int, constraints2d: Constraints2D, auto_build: bool = True):
        if not self.built:
            print("\n\ncan't add profile without generating")
            return None

        new_start_time = self.states[time].time
        new_start_distance = self.states[time].displacement
        new_start_velocity = self.states[time].velocities.getVelocityMagnitude()

        previous = 0
        for i in range(len(self.profiles) - 1):
            previous += self.profiles[i].distance
        distance = self.profiles[-1].distance - (new_start_distance - self.states[0].displacement - previous)

        self.profiles.append(MotionProfile(distance, constraints2d.linear,
                                           new_start_velocity,
                                           0,
                                           new_start_time,
                                           new_start_distance)
        )

        if self.profiles[-1].NOT_DEFINED:
            print("\n\nconstraints impossible to satisfy without compromising continuity")
            print("'PROFILE NOT DEFINED' error")
            self.profiles.pop()

        else:
            # update the previous profile to end when the new one starts
            self.profiles[-2] = self.profiles[-2].copy(
                distance = new_start_distance -self.states[0].displacement - previous,
                end_velocity = new_start_velocity
            )

            if time == 0:
                self.profiles.pop(-2)

            self.built = False
            if auto_build: self.generate()

    def motionFromProfileState(self, t: int, profile_state: ProfileState) -> MotionState:
        dis, vel, acc = profile_state.tuple()

         # Calculate the current pose based on the start pose and distance
        self.current_pose = self.last_state.pose + Pose(x = math.cos(self.angle) * (dis - self.start_dis),
                                                        y = math.sin(self.angle) * (dis - self.start_dis),
                                                        head = 0)
            
        # Decompose the velocity
        VEL = Point(x = math.cos(self.angle) * vel,
                    y = math.sin(self.angle) * vel)
        ANG_VEL = 0

        return MotionState(time = t,
                           field_vel = ChassisState(VEL, ANG_VEL),
                           displacement = dis,
                           pose = self.current_pose.copy().round(4))



    def getAction(self) -> MotionAction:
        return MotionAction.LINE
    
    def copy(self, last_state: MotionState, constraints2d: Constraints2D):
        return LinearSegment(last_state,
                             constraints2d.linear,
                             self.target)

    def addCM(self, cm: int):
        if isinstance(self.target, Point):
            print("\n\ncan't add a distance to a point :<")
            return self
        
        return LinearSegment(self.last_state,
                             self.constraints,
                             self.target + cm)
        
        
            

    def __pointFromDistance(self, cm: float, pose: Pose):
        return Point(x = pose.x + math.cos(pose.rad()) * cm,
                     y = pose.y + math.sin(pose.rad()) * cm)
    
    