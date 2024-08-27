from pythfinder.Trajectory.Kinematics.generic import *

# center_offset = the vector from the center of the robot (0,0) to the turning center
# assumes a standard n-wheel tank chassis
class TankKinematics(Kinematics):
    def __init__(self, 
                 track_width,
                 center_offset: None | Point = None,
                 parallel_wheels: int = 2,
                 perpendicular_wheels: int = 0):
        super().__init__()
        
        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.track_width = abs(track_width)

        self.parallel_wheels = abs(parallel_wheels)
        self.perpendicular_wheels = abs(perpendicular_wheels)

        if self.parallel_wheels % 2 == 1:
            raise Exception('\n\nyou kinda forgot one wheel somewhere')


    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        velocity = chassis_state.VEL
        angular_velocity = chassis_state.ANG_VEL

        left_speed = velocity.x + self.track_width * 0.5 * angular_velocity
        right_speed = velocity.x - self.track_width * 0.5 * angular_velocity

        perpendicular_speed = velocity.y

        return (
            tuple(WheelState(left_speed, 0).copies(self.parallel_wheels // 2)) +
            tuple(WheelState(right_speed, 0).copies(self.parallel_wheels // 2)) +
            tuple(WheelState(perpendicular_speed, 0).copies(self.perpendicular_wheels))
        )
    
    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        midpoint = self.parallel_wheels // 2

        first_half = speeds[:midpoint]
        second_half = speeds[midpoint:self.parallel_wheels]
        perpendicular = speeds[self.parallel_wheels:]

        left_average = sum(state.VELOCITY for state in first_half) / midpoint
        right_average = sum(state.VELOCITY for state in second_half) / midpoint

        velocity_y = sum(state.VELOCITY for state in perpendicular) / self.perpendicular_wheels
        velocity_x = (left_average + right_average) / 2.0
        angular_velocity = (left_average - right_average) / self.track_width # rad / sec

        return ChassisState(
            velocity = Point(velocity_x, velocity_y),
            angular_velocity = angular_velocity
        )
    

    def get_type(self) -> ChassisType:
        if self.perpendicular_wheels == 0:
            return ChassisType.NON_HOLONOMIC
        return ChassisType.HOLONOMIC

    def angular_to_linear(self, angular_velocity):
        return self.track_width * 0.5 * angular_velocity
    
    def copy(self):
        return TankKinematics(self.track_width,
                              self.center_offset,
                              self.parallel_wheels,
                              self.perpendicular_wheels)
