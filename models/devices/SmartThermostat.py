from dataclasses import dataclass
from .SmartDevice import SmartDevice, DevicePayload


@dataclass
class ThermostatPayload(DevicePayload):
    current_temp: float
    target_temp: float
    humidity: float


class SmartThermostat(SmartDevice):
    def __init__(self, name, location, current_temp, target_temp, humidity):
        super().__init__(name, location)
        self._current_temp = current_temp
        self._target_temp = target_temp
        self._humidity = humidity
        self._device_type = "THERMOSTAT"

    def get_status(self) -> dict:
        return {
            "id": str(self._id),
            "name": self._name,
            "location": self._location.value,
            "device_type": self._device_type,
            "current_temp": self._current_temp,
            "target_temp": self._target_temp,
            "humidity": self._humidity,
        }

    def update_state(self) -> None:
        if self._current_temp < self._target_temp:
            self._current_temp += 0.10  # slow heating
            # also increase humidity slightly when heating
            self._humidity += 0.02 if self._humidity < 100 else 0

        elif self._current_temp > self._target_temp:
            self._current_temp -= 0.05  # slow cooling
            # decrease humidity slightly when cooling
            self._humidity -= 0.01 if self._humidity > 0 else 0

    def execute_command(self, command: str) -> None:
        if command.startswith("set_target_temp"):
            _, value = command.split()
            self._target_temp = float(value)
        else:
            print(f"Unknown command: {command}")
