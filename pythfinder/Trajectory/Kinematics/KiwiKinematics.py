from pythfinder.Trajectory.Kinematics.generic import *

# assumes a standard 3 omni wheels kiwi chassis
#    front wheel of coords (R, 0)
#    left wheel of coords  (-R/2, -√3*R/2)
#    right wheel of coords (-R/2, √3*R/2)
class KiwiKinematics(Kinematics):
    def __init__(self, 
                 center_to_wheel: float,
                 center_offset: None | Point = None):
        super().__init__()

        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.R = abs(center_to_wheel)

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        # FW, LW, RW
        vx, vy, w = chassis_state.VEL.x, chassis_state.VEL.y, chassis_state.ANG_VEL

        forward_wheel = WheelState(velocity = vx - w * self.R,
                                   angle = 0)
        left_wheel = WheelState(velocity = - vx * 0.5 - vy * 0.5 * math.sqrt(3) - w * self.R,
                                angle = 0)
        right_wheel = WheelState(velocity = - vx * 0.5 + vy * 0.5 * math.sqrt(3) - w * self.R,
                                 angle = 0)
        
        return (forward_wheel, left_wheel, right_wheel)

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        FW, LW, RW = speeds

        return ChassisState(velocity = Point(x = 2 / 3 * (FW.VELOCITY - 0.5 * (LW.VELOCITY + RW.VELOCITY)),
                                             y = (RW.VELOCITY - LW.VELOCITY) / math.sqrt(3)).round(5),
                            angular_velocity = round(-(FW.VELOCITY + LW.VELOCITY + RW.VELOCITY) / (3 * self.R), 5))
    
    def getType(self) -> ChassisType:
        return ChassisType.HOLONOMIC
