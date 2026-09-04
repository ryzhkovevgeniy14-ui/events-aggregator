from enum import StrEnum


class EventStatus(StrEnum):
    NEW = "new"
    PUBLISHED = "published"


class TicketStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class SyncStatus(StrEnum):
    NEVER = "never"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"