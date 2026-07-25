"""Custom exception classes for the AML Preprocessing module."""

class AMLProcessingError(Exception):
    """Base exception class for all AML processing errors."""
    pass

class DatasetNotFoundError(AMLProcessingError):
    """Raised when a dataset file cannot be found or read."""
    pass

class InvalidSchemaError(AMLProcessingError):
    """Raised when a dataset does not match the expected schema or constraints."""
    pass

class MissingColumnError(InvalidSchemaError):
    """Raised when one or more required columns are missing from the dataset."""
    pass

class JoinError(AMLProcessingError):
    """Raised when a join operation (e.g. merging transactions and accounts) fails."""
    pass
