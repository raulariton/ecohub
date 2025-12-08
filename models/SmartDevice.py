from abc import ABC, abstractmethod
import uuid
import DeviceLocation


class SmartDevice(ABC):
    def __init__(self, name: str, location: DeviceLocation):
        self._id = uuid.uuid4()
        self._name = name
        self._location = location
        self._device_type = "GENERIC"

    @abstractmethod
    def get_status(self) -> str:
        pass

    @abstractmethod
    def execute_command(self, command: str) -> None:
        # no idea rn
        pass

    def connect(self) -> None:
        # simulate connection (async io delay)
        print(f"Device {self._name} connected.")
