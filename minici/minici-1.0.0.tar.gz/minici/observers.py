import asyncio
import asyncinotify
import functools
import os


class Observer(object):
    def __init__(self):
        self.callbacks = dict()
        self.callback_triggers = dict()

    def addCallbackTrigger(self, trigger_signal, callback_trigger):
        callback_triggers = self.callback_triggers.get(trigger_signal, [])
        callback_triggers.append(callback_trigger)
        self.callback_triggers[trigger_signal] = callback_triggers

    def addCallbacks(self, trigger, callbacks):
        callbacks_list = self.callbacks.get(trigger, [])
        callbacks_list.append(callbacks)
        self.callbacks[trigger] = callbacks_list

    def getEventInfo(self, event_type):
        return "{}.{}".format(self.__class__.__name__, event_type)

    async def observe(self):
        raise NotImplementedError()


class FileObserver(Observer):
    def __init__(self, file_):
        super().__init__()
        self.file_ = file_
        self.inotify = asyncinotify.Inotify()

    async def observe(self):
        trigger_event_tuples = [
            ("modify", asyncinotify.Mask.MODIFY),
            # ("ignored", asyncinotify.Mask.IGNORED),
        ]
        trigger_event_map = dict(trigger_event_tuples)
        event_trigger_map = dict([reversed(tup) for tup in trigger_event_tuples])
        event_trigger_map[asyncinotify.Mask.IGNORED] = "modify"

        watch_mask = functools.reduce(
            lambda mask, bit: mask | bit,
            [
                trigger_event_map[trigger]
                for trigger, callbacks in self.callbacks.items()
                if len(callbacks) > 0
            ],
            0,
        )
        while True:
            try:
                self.inotify.add_watch(self.file_, watch_mask)

                async for event in self.inotify:
                    os.system("clear")
                    trigger = event_trigger_map.get(event.mask, None)
                    for callbacks in self.callbacks.get(trigger, []):
                        event_info = self.getEventInfo(
                            "{} ({})".format(trigger, self.file_)
                        )
                        coroutines = [cb(event_info) for cb in callbacks]
                        await asyncio.gather(*coroutines)
                    if event.mask == asyncinotify.Mask.IGNORED:
                        break

            except Exception as e:
                await asyncio.sleep(0.5)


class ProcessObserver(Observer):
    def __init__(self, executor):
        super().__init__()
        self.executor = executor

    async def observe(self):
        triggers_to_observe = list(self.callbacks.keys())
        # await trigger and execute callbacks
        async def awaitLoop(trigger):
            # print("await trigger", trigger)
            event_info = self.getEventInfo(trigger)
            while True:
                await self.executor.awaitDone()
                # print(trigger, self.executor.done_state)
                if trigger not in self.executor.done_state:
                    continue
                for callbacks in self.callbacks.get(trigger, []):
                    # print("processobserver callback:", trigger, callbacks)
                    coroutines = [cb(event_info) for cb in callbacks]
                    await asyncio.gather(*coroutines)

        observer_loops = [awaitLoop(trigger) for trigger in triggers_to_observe]
        asyncio.gather(*observer_loops)
