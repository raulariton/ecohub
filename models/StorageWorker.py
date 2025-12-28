class StorageWorker:
    def __init__(self, queue):
        self._queue = queue

    def run(self):
        # runs in a separate thread

        while True:
            if not self._queue.empty():
                data = self._queue.get()
                # store data to persistent storage
                print(f"Storing data: {data}")

                # mark task as done
                self._queue.task_done()
