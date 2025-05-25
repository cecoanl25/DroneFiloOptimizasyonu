from dataclasses import dataclass

@dataclass
class Drone:
    id: int
    max_weight: float
    battery: int
    speed: float
    start_pos: tuple

@dataclass
class DeliveryPoints:
    id: int
    pos: tuple
    weight: float
    priority: int
    time_window: tuple

@dataclass
class NoFlyZones:
    id: int
    coordinates: list[tuple]
    active_time: tuple
