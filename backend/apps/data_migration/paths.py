"""Resolução de caminhos local (SGCS/backend) e Docker (/app)."""

from __future__ import annotations

from pathlib import Path


def backend_dir(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here, *here.parents]:
        if (parent / "manage.py").is_file() and (parent / "apps").is_dir():
            return parent
    return Path.cwd()


def project_root_from(start: Path | None = None) -> Path:
    backend = backend_dir(start)
    if backend.name == "backend" and (backend.parent / "docs").is_dir():
        return backend.parent
    return backend


def data_dir(root: Path | None = None) -> Path:
    backend = backend_dir()
    if root is not None:
        if (root / "backend" / "data").is_dir():
            return root / "backend" / "data"
        if (root / "data").is_dir():
            return root / "data"
    return backend / "data"


def default_output_dir(root: Path | None = None) -> Path:
    return data_dir(root) / "private" / "sauvida_migration"


def docs_dir(root: Path | None = None) -> Path:
    resolved = root or project_root_from()
    if (resolved / "docs").is_dir():
        return resolved / "docs"
    return backend_dir() / "docs"
