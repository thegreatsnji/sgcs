"""Throttling DRF do SGCS."""

from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle, UserRateThrottle


class LoginRateThrottle(ScopedRateThrottle):
    scope = "login"


class ApiAnonRateThrottle(AnonRateThrottle):
    scope = "anon"


class ApiUserRateThrottle(UserRateThrottle):
    scope = "user"
