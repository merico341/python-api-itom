from enum import Enum

class LogStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"

class LogOperation(str, Enum):
    # Record
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

    # User
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"

    # Device
    CONNECT = "CONNECT"
    DISCONNECT = "DISCONNECT"
    STATUS_CHANGE = "STATUS_CHANGE"