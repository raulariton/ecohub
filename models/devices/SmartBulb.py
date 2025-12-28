from models import DeviceLocation
from .SmartDevice import SmartDevice
from dataclasses import dataclass


@dataclass
class BulbPayload:
    device_id: str
    name: str
    location: str
    is_on: bool
    brightness: int


class SmartBulb(SmartDevice):
    def __init__(self, name: str, location: DeviceLocation, brightness: int = 100):
        super().__init__(name, location)
        self._is_on = True if brightness > 0 else False
        self._brightness = brightness
        self._device_type = "BULB"

    def get_status(self) -> dict:
        return {
            "id": str(self._id),
            "name": self._name,
            "location": self._location.value,
            "device_type": self._device_type,
            "is_on": self._is_on,
            "brightness": self._brightness,
        }

    def execute_command(self, command: str) -> None:
        # NOTE: there are no automatic (self-applied) commands for bulbs
        #  but changes happen from user input, which get
        #  reflected to the controller
        if command == "turn_on":
            self._is_on = True
            self._brightness = 100
        elif command == "turn_off":
            self._is_on = False
            self._brightness = 0
        elif command.startswith("set_brightness"):
            _, value = command.split()
            self._brightness = int(value)
        else:
            print(f"Unknown command: {command}")
