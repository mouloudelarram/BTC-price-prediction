"""
Custom exceptions for the Mood Analysis API.
"""


class MoodAnalyzerException(Exception):
    """Base exception for mood analyzer."""
    pass


class ScrapperException(MoodAnalyzerException):
    """Exception raised by scrapper service."""
    pass


class LLMException(MoodAnalyzerException):
    """Exception raised by LLM service."""
    pass


class DataNotFound(MoodAnalyzerException):
    """Exception raised when data is not found."""
    pass


class ProcessingError(MoodAnalyzerException):
    """Exception raised during data processing."""
    pass


class ConfigurationError(MoodAnalyzerException):
    """Exception raised due to configuration issues."""
    pass


class TimeoutError(MoodAnalyzerException):
    """Exception raised when operation times out."""
    pass
