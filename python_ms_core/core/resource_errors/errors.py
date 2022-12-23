class ServiceError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if args:
            self.message = args[0]
        else:
            self.message = None

    status = 400


class BadRequestError(ServiceError):
    status = 400


class UnauthorizedError(ServiceError):
    status = 401


class ForbiddenError(ServiceError):
    status = 403


class NotFoundError(ServiceError):
    status = 404


class TimeOutError(ServiceError):
    status = 408


class ConflictError(ServiceError):
    status = 409


class UnProcessableError(ServiceError):
    status = 422


class TooManyRequestError(ServiceError):
    status = 429


