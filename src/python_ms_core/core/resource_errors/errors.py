class ServiceError(Exception):
    status = 400

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if args:
            self.message = args[0]['message']
            self.status_code = args[0]['status_code'] if int(args[0]['status_code']) > 0 else self.status
            self.description = args[0]['description']
        else:
            self.message = None
            self.status_code = self.status
            self.description = None


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


class InternalServerError(ServiceError):
    status = 500
