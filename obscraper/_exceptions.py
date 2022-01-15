"""Exceptions for the obscraper package."""


class InvalidResponseError(Exception):
    """An HTTP response returned unexpected content."""


class InvalidAuthCodeError(Exception):
    """Vote count API called with invalid authorisation code."""


class AttributeNotFoundError(Exception):
    """An attribute could not be extracted from an HTML page."""
