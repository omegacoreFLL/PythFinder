from pythfinder.Trajectory.Kinematics.generic import *

# assumes a square-like chassis structure with 4 omni wheels
class X_DriveKinematics(Kinematics):
    def __init__(self, 
                 center_to_wheel: float,
                 center_offset: None | Point = None):
        super().__init__()
        
        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.R = abs(center_to_wheel)

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        vx, vy, w = chassis_state.VEL.x, chassis_state.VEL.y, chassis_state.ANG_VEL

        FL = WheelState(vx - vy - w * self.R, 0)
        FR = WheelState(vx + vy + w * self.R, 0)
        BL = WheelState(vx - vy + w * self.R, 0)
        BR = WheelState(vx + vy - w * self.R, 0)
        
        return (FR, FL, BL, BR)

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        FR, FL, BL, BR = speeds

        velocity_x = (FR.VELOCITY + FL.VELOCITY + BL.VELOCITY + BR.VELOCITY) * 0.25
        velocity_y = (FR.VELOCITY - FL.VELOCITY - BL.VELOCITY + BR.VELOCITY) * 0.25
        angular_velocity = (+ FR.VELOCITY - FL.VELOCITY + BL.VELOCITY - BR.VELOCITY) * 0.25 / self.R

        return ChassisState(
            velocity = Point(velocity_x, velocity_y),
            angular_velocity = angular_velocity
        )

    def getType(self) -> ChassisType:
        return ChassisType.HOLONOMIC
    
    def copy(self):
        return X_DriveKinematics(self.R, self.center_offset)

