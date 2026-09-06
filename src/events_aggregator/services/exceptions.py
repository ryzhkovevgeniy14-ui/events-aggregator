"""
Исключения бизнес-логики сервиса.

Используются сервисным слоем для обозначения ошибок,
возникающих при работе с мероприятиями и регистрациями.
"""

class EventNotFoundError(ValueError):
    pass


class EventNotPublishedError(ValueError):
    pass


class RegistrationDeadlinePassedError(ValueError):
    pass


class SeatNotAvailableError(ValueError):
    pass


class TicketNotFoundError(ValueError):
    pass


class EventAlreadyPassedError(ValueError):
    pass


class IdempotencyConflictError(ValueError):
    pass