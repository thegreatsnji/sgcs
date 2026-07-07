"""Respostas padronizadas da API."""

from rest_framework.response import Response


def success_response(data=None, message: str = "Operação concluída com sucesso.", status: int = 200):
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status,
    )


def error_response(message: str, errors=None, status: int = 400):
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors,
        },
        status=status,
    )
