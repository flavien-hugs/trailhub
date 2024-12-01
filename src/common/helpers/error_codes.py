from enum import Enum


class AppErrorCodes(str, Enum):
    DOCUMENT_NOT_FOUND = "document/document-not-found"
    DOCUMENT_ALREADY_EXISTS = "document/document-already-exists"
    INTERNAL_SERVER_ERROR = "app/internal-server-error"
    REQUEST_VALIDATION_ERROR = "app/request-validation-error"
    AUTH_ACCESS_DENIED = "app/service-access-denied"
