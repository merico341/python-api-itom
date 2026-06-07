from enum import Enum

class IncidentState(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CANCELED = "Canceled"

class IncidentPriority(str, Enum):
    CRITICAL = "1 - Critical"
    HIGH = "2 - High"
    MODERATE = "3 - Moderate"
    LOW = "4 - Low"