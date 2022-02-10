"""Exceptions for the obscraper package."""


class InvalidResponseError(Exception):
    """An HTTP response returned unexpected content."""


class AttributeNotFoundError(Exception):
    """An attribute could not be extracted from an HTML page."""
