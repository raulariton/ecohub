import asyncio
import queue
import threading

from models.AnalyticsEngine import AnalyticsEngine
from models.devices import SmartDevice
from .CriticalEvent import CriticalEvent
from .StorageWorker import StorageWorker


class Controller:
    def __init__(self):
        # storing received packets
        self._packet_queue = asyncio.Queue()
        self._connected_devices: list[SmartDevice] = []

        # initialize storage queue and storage worker
        self._storage_queue = queue.Queue()
        self._storage_worker = StorageWorker(self._storage_queue)

        # start storage worker in a separate thread
        self._storage_worker_thread = threading.Thread(
            target=self._storage_worker.run,
            daemon=False,
        )
        self._storage_worker_thread.start()

    async def connect(self, device: SmartDevice) -> asyncio.Queue:
        """
        Adds the device to the list of connected devices
        and returns the packet queue to be used by the device to send packets.
        """
        self._connected_devices.append(device)
        return self._packet_queue

    def handle_critical_event(self, payload, critical_event):
        # get device object using device id given in payload
        device = next(
            (
                device
                for device in self._connected_devices
                if str(device.id) == payload.device_id
            )
        )

        if critical_event == CriticalEvent.LOW_TEMPERATURE:
            # set to a safe temperature
            device.execute_command("set_target_temp 20.0")
            print(
                f"[CRITICAL]: {device.name} temperature too low! Adjusting target temperature."
            )
        elif critical_event == CriticalEvent.HIGH_TEMPERATURE:
            # set to a safe, non-freezing temperature
            device.execute_command("set_target_temp 17.0")
            print(
                f"[CRITICAL]: {device.name} temperature too high! Adjusting target temperature."
            )
        elif critical_event == CriticalEvent.LOW_HUMIDITY:
            # increase humidity by adjusting target temperature
            device.execute_command("set_target_temp 22.0")
            print(
                f"[CRITICAL]: {device.name} humidity too low! Adjusting target temperature to increase "
                f"humidity."
            )
        elif critical_event == CriticalEvent.HIGH_HUMIDITY:
            # decrease humidity by adjusting target temperature
            device.execute_command("set_target_temp 18.0")
            print(
                f"[CRITICAL]: {device.name} humidity too high! Adjusting target temperature to decrease "
                f"humidity."
            )

        elif critical_event == CriticalEvent.MOTION_DETECTED:
            # take a snapshot (if camera is on)
            #  the controller does not know if the camera is on or off, only attempts to make it take a
            #  snapshot
            device.execute_command("take_snapshot")
            print(
                f"[CRITICAL]: Motion detected by {device.name}! Attempting to take a snapshot."
            )
        elif critical_event == CriticalEvent.LOW_BATTERY:
            # turn off camera to save power
            #  the controller does not know if the camera is already off, only attempts to turn it off
            device.execute_command("turn_off")
            print(
                f"[CRITICAL]: {device.name} battery low! Turning off camera to save power."
            )

    async def consume(self):
        while True:
            packets = await self._packet_queue.get()

            # map packets to payloads
            payloads = list(AnalyticsEngine.map_packet(packets))

            # filter and handle critical events
            for payload, critical_event in AnalyticsEngine.filter_events(payloads):
                self.handle_critical_event(payload, critical_event)

            # reduce payloads to summaries
            summaries = AnalyticsEngine.reduce(payloads)
            if summaries:
                print(f"Summaries: {summaries}")

            # send payloads to storage queue
            for payload in payloads:
                self._storage_queue.put(payload)

            self._storage_queue.task_done()

    def end_storage_thread(self):
        # send None to storage queue to signal worker to stop
        self._storage_queue.put(None)
        self._storage_worker_thread.join()
