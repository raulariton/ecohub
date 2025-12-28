import asyncio

from models.AnalyticsEngine import AnalyticsEngine

class Controller:
    def __init__(self):
        # storing received packets
        self._packet_queue = asyncio.Queue()
        # storing payloads to be written to storage
        self._storage_queue = asyncio.Queue()

    async def connect(self) -> asyncio.Queue:
        """Returns a queue to which packets can be sent."""
        return self._packet_queue

    async def consume(self):
        while True:
            packets = await self._packet_queue.get()

            # map packets to payloads
            payloads = list(AnalyticsEngine.map_packet(packets))

            # filter critical events
            for critical_event in AnalyticsEngine.filter_events(payloads):
                print(f"Critical event detected: {critical_event}")

            # reduce payloads to summaries
            summaries = AnalyticsEngine.reduce(payloads)
            if summaries:
                print(f"Summaries: {summaries}")

            # send payloads to storage queue
            for payload in payloads:
                await self._storage_queue.put(payload)

            self._storage_queue.task_done()






        # while True:
        #     for connection in self.connections:
        #         async with connection:
        #             packet = await connection._packet_queue.get()
        #             await self.queue.put(packet)
