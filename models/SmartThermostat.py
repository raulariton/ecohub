from models.SmartDevice import SmartDevice


class SmartThermostat(SmartDevice):
    # NOTE: The idea is that when a device connects to the system,
    #  it provides basic data about itself
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

    def execute_command(self, command: str) -> None:
        if command.startswith("set_target_temp"):
            _, value = command.split()
            self._target_temp = float(value)
        else:
            print(f"Unknown command: {command}")
