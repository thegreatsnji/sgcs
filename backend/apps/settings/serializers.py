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
    MedicoPerfil,
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


class MedicoPerfilSerializer(serializers.ModelSerializer):
    utilizador_nome = serializers.CharField(source="utilizador.get_full_name", read_only=True)
    utilizador_email = serializers.CharField(source="utilizador.email", read_only=True)
    especialidade_nome = serializers.CharField(source="especialidade.nome", read_only=True)
    departamento_nome = serializers.CharField(source="departamento.nome", read_only=True)
    servico_consulta_nome = serializers.CharField(source="servico_consulta.nome", read_only=True)
    servico_consulta_preco = serializers.DecimalField(
        source="servico_consulta.preco", max_digits=12, decimal_places=2, read_only=True
    )
    horario_configurado = serializers.SerializerMethodField()

    class Meta:
        model = MedicoPerfil
        fields = (
            "id",
            "utilizador",
            "utilizador_nome",
            "utilizador_email",
            "especialidade",
            "especialidade_nome",
            "departamento",
            "departamento_nome",
            "numero_profissional",
            "dias_trabalho",
            "horario_atendimento",
            "horario_configurado",
            "duracao_consulta_minutos",
            "servico_consulta",
            "servico_consulta_nome",
            "servico_consulta_preco",
            "activo",
            "disponivel_marcacao",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_horario_configurado(self, obj) -> bool:
        return bool(obj.horario_atendimento and obj.dias_trabalho)

    def validate_utilizador(self, user):
        from apps.authentication.models import UserRole

        if user.role != UserRole.MEDICO:
            raise serializers.ValidationError("Apenas utilizadores com perfil Médico podem ter MedicoPerfil.")
        return user

    def validate(self, attrs):
        utilizador = attrs.get("utilizador") or getattr(self.instance, "utilizador", None)
        if utilizador:
            qs = MedicoPerfil.objects.filter(utilizador=utilizador)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"utilizador": "Este médico já possui perfil configurado."})
        return attrs
