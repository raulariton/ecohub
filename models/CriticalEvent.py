from enum import Enum


class CriticalEvent(Enum):
    # thermostat alerts
    LOW_TEMPERATURE = 1
    HIGH_TEMPERATURE = 2
    LOW_HUMIDITY = 3
    HIGH_HUMIDITY = 4

    # camera alerts
    MOTION_DETECTED = 5
    LOW_BATTERY = 6
