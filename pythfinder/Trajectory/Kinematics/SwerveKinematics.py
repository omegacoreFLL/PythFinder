from pythfinder.Trajectory.Kinematics.generic import *


class SwerveLockStates(Enum):
    X = auto()
    DIAMOND = auto()
    DEFAULT = auto()
    ZERO = auto()

class SwerveModules(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4


# assumes a standard 4 module chassis (for now)
class SwerveKinematics(Kinematics):
    def __init__(self,
                 track_width: float,
                 track_length: float,
                 center_to_module: None | float = None,
                 center_offset: None | Point = None,
                 module_number: SwerveModules = SwerveModules.FOUR):
        
        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.modules = module_number

        if self.modules is not SwerveModules.THREE:
            self.track_width = abs(track_width)
        else: self.track_width = 0 # you can't define the width of a triangle lol

        if self.modules is not SwerveModules.FOUR:
            self.track_length = abs(track_length)
        else: self.track_length = 0 # with 2 modules you don't need this value. Neither with 3

        if center_to_module is None:
            if self.modules is SwerveModules.THREE:
                raise Exception("\n\nprovide the center to module distance\n\n")
            self.R = math.hypot(self.track_width, self.track_length) * 0.5
        else: self.R = abs(center_to_module)

        self.ANGULAR_VELOCITY_X = self.track_length / self.R
        self.ANGULAR_VELOCITY_Y = self.track_width / self.R

        self.LOCKED: bool = False
        self.lock_state = SwerveLockStates.DIAMOND
        self.last_state = []

        for _ in range(self.modules.value):
            self.last_state.append(WheelState())
        self.last_state = tuple(self.last_state)
    
    def lock(self):
        self.LOCKED = True

    def unlock(self):
        self.LOCKED = False
    
    def setLockState(self, lock: SwerveLockStates):
        self.lock_state = lock

    def getLockState(self) -> Tuple[WheelState]:
        module_states: list = []

        match self.lock_state:
            case SwerveLockStates.DEFAULT:
                for i in range(self.modules.value):
                    module_states.append(
                        WheelState(0, self.last_state[i].ANGLE)
                    )
            
            case SwerveLockStates.DIAMOND:
                for i in range(self.modules.value):
                    module_states.append(
                        WheelState(0, (1 if i % 2 == 0 else -1) * math.pi / self.modules.value) 
                    )

            case SwerveLockStates.X:
                for i in range(self.modules.value):
                    module_states.append(
                        SwerveLockStates(0, (-1 if i % 2 == 0 else 1) * math.pi / self.modules.value)
                    )
            
            case SwerveLockStates.ZERO:
                for i in range(self.modules.value):
                    module_states.append(
                        WheelState(0, 0)
                    )
        
        return tuple(module_states)

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        if self.LOCKED:
            return self.getLockState()

        velocity = chassis_state.VEL
        angular_velocity = chassis_state.ANG_VEL

        right: float = velocity.x - angular_velocity * self.ANGULAR_VELOCITY_X
        left: float = velocity.x + angular_velocity * self.ANGULAR_VELOCITY_X
        front: float = velocity.y + angular_velocity * self.ANGULAR_VELOCITY_Y
        back: float = velocity.y - angular_velocity * self.ANGULAR_VELOCITY_Y

        match self.modules:
            case SwerveModules.FOUR:
                self.last_state = (
                    WheelState(math.hypot(front, right), math.atan2(front, right)), # FR
                    WheelState(math.hypot(front, left), math.atan2(front, left)),   # FL
                    WheelState(math.hypot(back, left), math.atan2(back, left)),     # BL
                    WheelState(math.hypot(back, right), math.atan2(back, right))    # BR
                ) 
            
            case SwerveModules.THREE:
                pass

            case SwerveModules.TWO:
                self.last_state = (
                    WheelState(math.hypot(front, right), math.atan2(front, right)), # R
                    WheelState(math.hypot(back, left), math.atan2(back, left)),     # L
                )

        return self.last_state

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        velocity = Point()

        for each in speeds:
            velocity = velocity + Point(
                               x = each.VELOCITY * math.cos(each.ANGLE),
                               y = each.VELOCITY * math.sin(each.ANGLE))
            
        angular_velocity = velocity.x / self.R
        velocity = (velocity / len(speeds)).round(5)

        return ChassisState(
            velocity,
            round(angular_velocity, 5)
        )

    def getType(self) -> ChassisType:
        return ChassisType.HOLONOMIC
