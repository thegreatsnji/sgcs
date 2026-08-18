"""Normalização de texto e nomes — sem correcção automática de grafias."""

from __future__ import annotations

import re
import unicodedata

from apps.data_migration.constants import NAME_PARTICLES

_SPACE_RE = re.compile(r"\s+")


def collapse_spaces(value: str) -> str:
    return _SPACE_RE.sub(" ", (value or "").strip())


def fold_for_match(value: str) -> str:
    """Chave de comparação: minúsculas, sem acentos, espaços colapsados."""
    text = collapse_spaces(value)
    nfkd = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    return stripped.casefold()


def preserve_nfc(value: str) -> str:
    return unicodedata.normalize("NFC", collapse_spaces(value))


def normalize_person_name(original: str) -> tuple[str, str]:
    """Devolve (nome_original, nome_normalizado).

    Não corrige grafias. Apenas remove espaços extra e normaliza capitalização,
    preservando acentos e partículas (da, de, do, …).
    """
    raw = (original or "").strip()
    collapsed = preserve_nfc(raw)
    if not collapsed:
        return raw, ""

    parts: list[str] = []
    for index, token in enumerate(collapsed.split(" ")):
        lower = token.casefold()
        if index > 0 and lower in NAME_PARTICLES:
            parts.append(lower)
            continue
        if token.isupper() or token.islower() or token.istitle():
            parts.append(token[:1].upper() + token[1:].lower() if len(token) > 1 else token.upper())
        else:
            parts.append(token)
    return raw, " ".join(parts)


def looks_like_person_name(value: str) -> bool:
    text = collapse_spaces(value)
    if len(text) < 3:
        return False
    if text.replace(" ", "").isdigit():
        return False
    folded = fold_for_match(text)
    if any(folded == skip or folded.startswith(f"{skip} ") for skip in ("total", "subtotal", "resumo")):
        return False
    letters = sum(ch.isalpha() for ch in text)
    return letters >= 3
