"""Exceções personalizadas da API."""

from rest_framework import status
from rest_framework.exceptions import APIException


class BusinessRuleException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Regra de negócio violada."
    default_code = "business_rule_error"


class ResourceNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Recurso não encontrado."
    default_code = "resource_not_found"


class PermissionDeniedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Não tem permissão para executar esta ação."
    default_code = "permission_denied"
