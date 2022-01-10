"""Exceptions for the obscraper package."""


class InvalidResponseError(Exception):
    """An HTTP response returned unexpected content."""


class InvalidAuthCodeError(Exception):
    """The vote count API was called with an invalid auth code."""


class AttributeNotFoundError(Exception):
    """An attribute could not be extracted from an HTML page."""
