import asyncio
from queue import Queue

from models.devices import *
from models import Controller, DeviceLocation


async def main():
    storage_queue = Queue()

    devices = [
        SmartCamera("Garage Camera", DeviceLocation.GARAGE, 100),
        SmartBulb("Bedroom Light", DeviceLocation.BEDROOM, 100),
        SmartThermostat("Living Room Thermostat", DeviceLocation.LIVING_ROOM, 22.0, 23.0, 30.0)
    ]

    controller = Controller()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(controller.consume())

        for device in devices:
            tg.create_task(device.run(controller))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down IoT system...")