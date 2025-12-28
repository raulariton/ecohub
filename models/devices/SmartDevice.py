import json
from abc import ABC, abstractmethod
import uuid
from datetime import datetime

from models import Controller, DeviceLocation
import asyncio


class SmartDevice(ABC):
    def __init__(self, name: str, location: DeviceLocation):
        self._id = uuid.uuid4()
        self._name = name
        self._location = location
        self._device_type = "GENERIC"
        self._controller_queue: asyncio.Queue | None = None

    @abstractmethod
    def get_status(self) -> str:
        pass

    @abstractmethod
    def execute_command(self, command: str) -> None:
        pass

    async def connect(self, controller: Controller) -> None:
        # simulate connection (async io delay)
        self._controller_queue = await controller.connect()
        print(f"Device {self._name} connected.")

    async def run(self, controller: Controller) -> None:
        await self.connect(controller)

        while True:
            status = self.get_status()
            packet = {
                "device_id": str(self._id),
                "timestamp": datetime.now().isoformat(),
                "payload": status,
            }

            await self._controller_queue.put(json.dumps(packet))

            await asyncio.sleep(5)  # send status every 5 seconds
