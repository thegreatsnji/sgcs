"""Views de resultados laboratoriais."""

from django.http import FileResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.laboratory.models import AnexoResultado, ResultadoLaboratorial
from apps.laboratory.permissions import LaboratoryResultPermissionMixin
from apps.laboratory.result_filters import ResultadoLaboratorialFilter
from apps.laboratory.result_serializers import (
    AnexoResultadoSerializer,
    ParametroCreateSerializer,
    ResultadoCreateSerializer,
    ResultadoLaboratorialSerializer,
    ResultadoUpdateSerializer,
)
from apps.laboratory.services.laboratory_result_service import LaboratoryResultService
from core.pagination import StandardPagination
from core.responses import error_response, success_response


@extend_schema_view(
    list=extend_schema(tags=["Resultados Laboratoriais"]),
    retrieve=extend_schema(tags=["Resultados Laboratoriais"]),
    create=extend_schema(tags=["Resultados Laboratoriais"]),
    partial_update=extend_schema(tags=["Resultados Laboratoriais"]),
    validate_result=extend_schema(tags=["Resultados Laboratoriais"]),
    publish=extend_schema(tags=["Resultados Laboratoriais"]),
    attachments=extend_schema(tags=["Resultados Laboratoriais"]),
    download=extend_schema(tags=["Resultados Laboratoriais"]),
)
class LaboratoryResultViewSet(LaboratoryResultPermissionMixin, viewsets.ModelViewSet):
    queryset = ResultadoLaboratorial.objects.all()
    serializer_class = ResultadoLaboratorialSerializer
    pagination_class = StandardPagination
    filterset_class = ResultadoLaboratorialFilter
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return ResultadoCreateSerializer
        if self.action in {"partial_update", "update"}:
            return ResultadoUpdateSerializer
        return ResultadoLaboratorialSerializer

    def get_queryset(self):
        return LaboratoryResultService.listar_resultados(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = ResultadoLaboratorialSerializer(page, many=True, context={"request": request})
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Resultados laboratoriais obtidos com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return success_response(
            data=ResultadoLaboratorialSerializer(instance, context={"request": request}).data,
            message="Resultado obtido com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = ResultadoCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        resultado = serializer.save()
        return success_response(
            data=ResultadoLaboratorialSerializer(resultado, context={"request": request}).data,
            message="Resultado criado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ResultadoUpdateSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return success_response(
            data=ResultadoLaboratorialSerializer(updated, context={"request": request}).data,
            message="Resultado actualizado com sucesso.",
        )

    @action(detail=True, methods=["post"], url_path="validate")
    def validate_result(self, request, pk=None):
        try:
            resultado = LaboratoryResultService.validar_resultado(int(pk), request.user, request=request)
        except ResultadoLaboratorial.DoesNotExist:
            return error_response("Resultado não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ResultadoLaboratorialSerializer(resultado, context={"request": request}).data,
            message="Resultado validado com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        try:
            resultado = LaboratoryResultService.publicar_resultado(int(pk), request.user, request=request)
        except ResultadoLaboratorial.DoesNotExist:
            return error_response("Resultado não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ResultadoLaboratorialSerializer(resultado, context={"request": request}).data,
            message="Resultado publicado com sucesso.",
        )

    @extend_schema(request=ParametroCreateSerializer)
    @action(detail=True, methods=["post"], url_path="parameters")
    def add_parameter(self, request, pk=None):
        serializer = ParametroCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            LaboratoryResultService.adicionar_parametro(
                int(pk),
                request.user,
                serializer.validated_data,
                request=request,
            )
            resultado = ResultadoLaboratorial.objects.get(pk=pk)
        except ResultadoLaboratorial.DoesNotExist:
            return error_response("Resultado não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ResultadoLaboratorialSerializer(resultado, context={"request": request}).data,
            message="Parâmetro adicionado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def attachments(self, request, pk=None):
        upload = request.FILES.get("file")
        if not upload:
            return error_response("Ficheiro em falta.", status=status.HTTP_400_BAD_REQUEST)
        try:
            anexo = LaboratoryResultService.anexar_documento(
                int(pk),
                request.user,
                upload,
                descricao=request.data.get("descricao", ""),
                request=request,
            )
            resultado = ResultadoLaboratorial.objects.get(pk=pk)
        except ResultadoLaboratorial.DoesNotExist:
            return error_response("Resultado não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data={
                "resultado": ResultadoLaboratorialSerializer(resultado, context={"request": request}).data,
                "anexo": AnexoResultadoSerializer(anexo, context={"request": request}).data,
            },
            message="Anexo adicionado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        anexo_id = request.query_params.get("anexo_id")
        if not anexo_id:
            return error_response("Indique o parâmetro anexo_id.", status=status.HTTP_400_BAD_REQUEST)
        try:
            anexo = AnexoResultado.objects.select_related("ficheiro", "resultado").get(
                pk=int(anexo_id),
                resultado_id=int(pk),
            )
        except (AnexoResultado.DoesNotExist, ValueError):
            return error_response("Anexo não encontrado.", status=status.HTTP_404_NOT_FOUND)

        LaboratoryResultService.registar_download(int(pk), request.user, request=request)
        return FileResponse(anexo.ficheiro.file.open("rb"), as_attachment=True, filename=anexo.ficheiro.name)
