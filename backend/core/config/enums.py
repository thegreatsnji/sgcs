"""Enumerações partilhadas do SGCS."""

from django.db import models


class Environment(models.TextChoices):
    DEVELOPMENT = "development", "Desenvolvimento"
    STAGING = "staging", "Staging"
    PRODUCTION = "production", "Produção"


class StorageBackend(models.TextChoices):
    LOCAL = "local", "Armazenamento local"
    S3 = "s3", "Amazon S3"
    AZURE = "azure", "Azure Blob"


class CacheBackend(models.TextChoices):
    REDIS = "redis", "Redis"
    LOCAL = "local", "Memória local"
