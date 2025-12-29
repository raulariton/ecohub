import asyncio

from models.devices import *
from models import Controller, DeviceLocation


async def main(controller: Controller):
    devices = [
        SmartCamera("Garage Camera", DeviceLocation.GARAGE, 20),
        SmartBulb("Bedroom Light", DeviceLocation.BEDROOM, 100),
        SmartThermostat(
            "Living Room Thermostat", DeviceLocation.LIVING_ROOM, 12.0, 23.0, 30.0
        ),
    ]

    async with asyncio.TaskGroup() as tg:
        tg.create_task(controller.consume())

        for device in devices:
            tg.create_task(device.run(controller))


if __name__ == "__main__":
    # initialize controller
    controller = Controller()
    try:
        asyncio.run(main(controller))
    except KeyboardInterrupt:
        print("Shutting down IoT system...")

        # end storage worker thread
        # by inserting "None" into storage queue
        controller.end_storage_thread()
