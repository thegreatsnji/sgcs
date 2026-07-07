"""Mixins de views do módulo de pacientes."""

from functools import wraps

from rest_framework import status

from core.responses import error_response, success_response


class SuccessResponseMixin:
    list_message = "Listagem obtida com sucesso."
    retrieve_message = "Detalhe obtido com sucesso."
    create_message = "Registo criado com sucesso."
    update_message = "Registo atualizado com sucesso."
    delete_message = "Registo eliminado com sucesso."

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message=self.list_message,
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(data=serializer.data, message=self.retrieve_message)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message=self.create_message,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message=self.update_message)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message=self.delete_message, data=None)


class PatientNestedMixin:
    patient_lookup_url_kwarg = "patient_pk"

    def get_patient(self):
        from apps.patients.services.patient_service import PatientService

        return PatientService.get_active_queryset().get(
            pk=self.kwargs[self.patient_lookup_url_kwarg]
        )

    def get_queryset(self):
        return super().get_queryset().filter(
            patient_id=self.kwargs[self.patient_lookup_url_kwarg]
        )


def handle_value_error(view_method):
    @wraps(view_method)
    def wrapper(self, request, *args, **kwargs):
        try:
            return view_method(self, request, *args, **kwargs)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)

    return wrapper
