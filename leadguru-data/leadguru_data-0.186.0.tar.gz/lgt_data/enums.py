import enum


class DedicatedBotState(enum.IntFlag):
    Operational = 0
    Stopped = 1
    ScheduledForDeletion = 2

class UserAccountState(enum.IntFlag):
    Operational = 0
    Suspended = 1
