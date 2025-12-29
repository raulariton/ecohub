from queue import Queue


class StorageWorker:
    def __init__(self, queue: Queue):
        self._queue = queue

    def run(self):
        # runs in a separate thread

        with open("history.log", "w") as file:
            while True:
                # this will block
                # until there is something in the queue
                log = self._queue.get()

                # condition to explicitly break the loop and
                # end thread
                # if there is 'None' in the queue, we break
                if log is None:
                    break

                # write log in file
                file.write(f"{log}\n")
                # flush to write immediately
                file.flush()

