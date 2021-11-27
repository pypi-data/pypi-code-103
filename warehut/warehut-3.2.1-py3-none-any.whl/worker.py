import asyncio

from typing import Callable

from multiprocessing import Value, Process



class Worker:
    """Generic worker class"""
    
    status: Value
    running: Value


    def __init__(self):
        self.status = Value('b', False)
        self.running = Value('b', False)


    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, trace):
        pass


    async def _mainloop(self):
        """Main loop to be run within the context manager
        This should involve some boolean check for whether status still is true
        """
        raise NotImplementedError()

    def start(self, handle_error: Callable):
        """Start the worker process"""

        # Avoid starting multiple processes
        if self.running.value:
            return
        
        # Mark worker as online and running
        self.status.value = True
        self.running.value = True

        # Create and start the process
        process = Process(
            target=_start_process,
            kwargs=dict(
                worker=self,
                handle_error=handle_error
            )
        ).start()

    def stop(self):
        """Stop the worker process"""
        self.status.value = False


def _start_process(worker: Worker, handle_error: Callable):
    """Start process for worker and log any exceptions raised"""

    async def start_coroutine(worker: Worker, handle_error: Callable):
        try:
            async with worker:
                await worker._mainloop()

        except Exception as e:
            handle_error(type(worker), e)
        
        finally:
            # Make sure the status is offline even after a crash
            worker.status.value = False
            worker.running.value = False

    worker.event_loop = asyncio.get_event_loop()
    worker.event_loop.run_until_complete(start_coroutine(
                        worker=worker, handle_error=handle_error))