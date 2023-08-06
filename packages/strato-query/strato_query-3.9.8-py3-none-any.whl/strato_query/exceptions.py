"""
StratoDem Analytics : exceptions
Principal Author(s) : Michael Clawar
Secondary Author(s) :
Description :

Notes :

August 21, 2019
"""

__all__ = ['StratoDemAPIException', 'APITokenNotFoundException', 'APIQueryFailedException']


class StratoDemAPIException(Exception):
    pass


class APITokenNotFoundException(StratoDemAPIException):
    pass


class APIQueryFailedException(StratoDemAPIException):
    pass
