"""Serializers do módulo de configurações."""

from rest_framework import serializers

from apps.settings.models import (
    BackupRegisto,
    ConfiguracaoEmail,
    ConfiguracaoFaturacao,
    ConfiguracaoFicheiros,
    ConfiguracaoSeguranca,
    ConfiguracaoSms,
    Consultorio,
    Departamento,
    EspecialidadeMedica,
    Feriado,
    FeatureFlag,
    HorarioFuncionamento,
    PerfilClinica,
    TipoConsulta,
    TipoExameLaboratorio,
)


class PerfilClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilClinica
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EspecialidadeMedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecialidadeMedica
        fields = "__all__"


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = "__all__"


class ConsultorioSerializer(serializers.ModelSerializer):
    departamento_nome = serializers.CharField(source="departamento.nome", read_only=True)

    class Meta:
        model = Consultorio
        fields = "__all__"


class HorarioFuncionamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioFuncionamento
        fields = "__all__"


class FeriadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feriado
        fields = "__all__"


class TipoConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoConsulta
        fields = "__all__"


class TipoExameLaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoExameLaboratorio
        fields = "__all__"


class ConfiguracaoFaturacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoFaturacao
        fields = "__all__"


class ConfiguracaoEmailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = ConfiguracaoEmail
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class ConfiguracaoSmsSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = ConfiguracaoSms
        fields = "__all__"


class ConfiguracaoSegurancaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoSeguranca
        fields = "__all__"


class ConfiguracaoFicheirosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoFicheiros
        fields = "__all__"


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = "__all__"


class BackupRegistoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupRegisto
        fields = "__all__"
        read_only_fields = ("estado", "ficheiro", "tamanho_bytes", "created_at", "updated_at")
