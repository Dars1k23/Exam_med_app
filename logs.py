from enum import IntEnum

class Status(IntEnum):
    OK = 1
    WARNING = 2
    CRITICAL_ERROR = 3


class LOGS:
    def __init__(self):
        self.write("New Session Begin", Status.OK)

    def write(self, message: str, status: Status):
        pass
