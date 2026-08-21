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