from pythfinder.Trajectory.Kinematics.generic import *

# assumes a standard 4 wheel mecanum chassis
class MecanumKinematics(Kinematics):
    def __init__(self,
                 track_width: float,
                 center_offset: None | Point = None):
        super().__init__()
        
        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.track_width = abs(track_width)

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        angular_to_linear = chassis_state.ANG_VEL * (self.track_width / 2)
        velocity = chassis_state.VEL

        return (
            WheelState(velocity.y - velocity.x + angular_to_linear, 0),  # FR
            WheelState(velocity.y + velocity.x - angular_to_linear, 0),  # FL
            WheelState(velocity.y - velocity.x - angular_to_linear, 0),  # BL
            WheelState(velocity.y + velocity.x + angular_to_linear, 0),  # BR
        )

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        FR, FL, BL, BR = speeds
        
        velocity_y = (FR.VELOCITY + FL.VELOCITY + BL.VELOCITY + BR.VELOCITY) * 0.25
        velocity_x = (-FR.VELOCITY + FL.VELOCITY - BL.VELOCITY + BR.VELOCITY) * 0.25
        angular_velocity = (-FR.VELOCITY + FL.VELOCITY + BL.VELOCITY - BR.VELOCITY) / (self.track_width * 2)

        return ChassisState(
                velocity = Point(velocity_x, velocity_y), 
                angular_velocity = angular_velocity
        )

    def get_type(self) -> ChassisType:
        return ChassisType.HOLONOMIC

    def copy(self):
        return MecanumKinematics(self.track_width,
                                 self.center_offset)