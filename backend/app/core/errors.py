class AppError(Exception):
    """Base class for expected, user-facing application errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class ExternalServiceError(AppError):
    def __init__(self, message: str = "An external service failed"):
        super().__init__(message, status_code=502)


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "Service is not configured"):
        super().__init__(message, status_code=503)
