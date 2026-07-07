"""Serializers de resultados laboratoriais."""

from rest_framework import serializers

from apps.laboratory.models import AnexoResultado, ParametroResultado, ResultadoLaboratorial
from apps.laboratory.services.laboratory_result_service import LaboratoryResultService


class ParametroResultadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametroResultado
        fields = (
            "id",
            "nome",
            "valor",
            "unidade",
            "valor_minimo",
            "valor_maximo",
            "interpretacao",
            "ordem",
        )
        read_only_fields = ("id", "interpretacao")


class ParametroCreateSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=120)
    valor = serializers.CharField(max_length=100)
    unidade = serializers.CharField(required=False, allow_blank=True, default="")
    valor_minimo = serializers.CharField(required=False, allow_blank=True, default="")
    valor_maximo = serializers.CharField(required=False, allow_blank=True, default="")
    interpretacao = serializers.CharField(required=False, allow_blank=True)
    ordem = serializers.IntegerField(required=False, default=0)


class AnexoResultadoSerializer(serializers.ModelSerializer):
    ficheiro_url = serializers.SerializerMethodField()
    nome_ficheiro = serializers.CharField(source="ficheiro.name", read_only=True)

    class Meta:
        model = AnexoResultado
        fields = ("id", "tipo", "descricao", "nome_ficheiro", "ficheiro_url", "created_at")
        read_only_fields = fields

    def get_ficheiro_url(self, obj) -> str | None:
        request = self.context.get("request")
        if obj.ficheiro and obj.ficheiro.file:
            if request:
                return request.build_absolute_uri(obj.ficheiro.file.url)
            return obj.ficheiro.file.url
        return None


class ResultadoLaboratorialSerializer(serializers.ModelSerializer):
    numero_pedido = serializers.CharField(source="pedido_laboratorial.numero_pedido", read_only=True)
    paciente_nome = serializers.CharField(source="pedido_laboratorial.paciente.full_name", read_only=True)
    paciente_id = serializers.IntegerField(source="pedido_laboratorial.paciente_id", read_only=True)
    consulta_id = serializers.IntegerField(source="pedido_laboratorial.consulta_id", read_only=True)
    medico_nome = serializers.SerializerMethodField()
    responsavel_nome = serializers.SerializerMethodField()
    validado_por_nome = serializers.SerializerMethodField()
    parametros = ParametroResultadoSerializer(many=True, read_only=True)
    anexos = AnexoResultadoSerializer(many=True, read_only=True)
    editavel = serializers.BooleanField(source="is_editavel", read_only=True)

    class Meta:
        model = ResultadoLaboratorial
        fields = (
            "id",
            "pedido_laboratorial",
            "numero_pedido",
            "paciente_id",
            "paciente_nome",
            "consulta_id",
            "medico_nome",
            "estado",
            "responsavel",
            "responsavel_nome",
            "validado_por",
            "validado_por_nome",
            "data_resultado",
            "data_validacao",
            "data_publicacao",
            "observacoes",
            "conclusao",
            "parametros",
            "anexos",
            "editavel",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_medico_nome(self, obj) -> str | None:
        medico = obj.pedido_laboratorial.medico
        return medico.get_full_name() if medico else None

    def get_responsavel_nome(self, obj) -> str | None:
        return obj.responsavel.get_full_name() if obj.responsavel else None

    def get_validado_por_nome(self, obj) -> str | None:
        return obj.validado_por.get_full_name() if obj.validado_por else None


class ResultadoCreateSerializer(serializers.Serializer):
    pedido_laboratorial = serializers.IntegerField()
    observacoes = serializers.CharField(required=False, allow_blank=True, default="")
    conclusao = serializers.CharField(required=False, allow_blank=True, default="")
    parametros = ParametroCreateSerializer(many=True, required=False, default=list)

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        parametros = validated_data.pop("parametros", [])
        try:
            resultado = LaboratoryResultService.criar_resultado(
                validated_data["pedido_laboratorial"],
                user,
                observacoes=validated_data.get("observacoes", ""),
                conclusao=validated_data.get("conclusao", ""),
                request=request,
            )
            for idx, param in enumerate(parametros):
                param_data = dict(param)
                param_data.setdefault("ordem", idx)
                LaboratoryResultService.adicionar_parametro(
                    resultado.pk,
                    user,
                    param_data,
                    request=request,
                )
            resultado.refresh_from_db()
            return resultado
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class ResultadoUpdateSerializer(serializers.Serializer):
    observacoes = serializers.CharField(required=False, allow_blank=True)
    conclusao = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return LaboratoryResultService.editar_resultado(
                instance.pk,
                user,
                observacoes=validated_data.get("observacoes"),
                conclusao=validated_data.get("conclusao"),
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
