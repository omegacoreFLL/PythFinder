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
        angular_to_linear = chassis_state.ANG_VEL * self.track_width
        velocity = chassis_state.VEL

        return (
            WheelState(velocity.x + velocity.y + angular_to_linear, 0), # FR
            WheelState(velocity.x - velocity.y - angular_to_linear, 0), # FL
            WheelState(velocity.x + velocity.y - angular_to_linear, 0), # BL
            WheelState(velocity.x - velocity.y + angular_to_linear, 0), # BR
        )

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        FR, FL, BL, BR = speeds
        
        velocity_x = (FR.VELOCITY + FL.VELOCITY + BL.VELOCITY + BR.VELOCITY) * 0.25
        velocity_y = (FR.VELOCITY - FL.VELOCITY + BL.VELOCITY - BR.VELOCITY) * 0.25
        angular_velocity = (FR.VELOCITY - FL.VELOCITY - BL.VELOCITY + BR.VELOCITY) * 0.25 / self.track_width

        return ChassisState(
                velocity = Point(velocity_x, velocity_y), 
                angular_velocity = angular_velocity
        )

    def getType(self) -> ChassisType:
        return ChassisType.HOLONOMIC
