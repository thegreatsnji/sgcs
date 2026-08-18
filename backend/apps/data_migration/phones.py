"""Normalização de telefones sem inventar números."""

from __future__ import annotations

import re

_DIGIT_RE = re.compile(r"\d+")


def extract_digits(value: str) -> str:
    return "".join(_DIGIT_RE.findall(value or ""))


def normalize_phone(value: str) -> str:
    """Normaliza para dígitos. Não inventa prefixos internacionais."""
    digits = extract_digits(value)
    if not digits:
        return ""
    if len(digits) < 5:
        return ""
    return digits


def phones_compatible(a: str, b: str) -> bool:
    left, right = normalize_phone(a), normalize_phone(b)
    if not left or not right:
        return False
    if left == right:
        return True
    return left[-6:] == right[-6:] and min(len(left), len(right)) >= 6


def looks_like_phone(value: str) -> bool:
    digits = extract_digits(value)
    return 7 <= len(digits) <= 15
