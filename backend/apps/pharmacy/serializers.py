from rest_framework import serializers

from apps.pharmacy.constants import CategoriaItemUrgencia, TipoMovimentoStockUrgencia
from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia


class MedicamentoUrgenciaSerializer(serializers.ModelSerializer):
    abaixo_minimo = serializers.BooleanField(read_only=True)
    estado = serializers.CharField(read_only=True)
    stock_inicial_por_confirmar = serializers.BooleanField(read_only=True)
    servico_codigo = serializers.CharField(source="servico.codigo", read_only=True, default=None)

    class Meta:
        model = MedicamentoUrgencia
        fields = [
            "id",
            "codigo",
            "nome",
            "forma_apresentacao",
            "categoria",
            "unidade",
            "quantidade_stock",
            "stock_minimo",
            "validade",
            "preco_referencia_fcfa",
            "quantidade_texto_original",
            "servico",
            "servico_codigo",
            "activo",
            "observacoes",
            "abaixo_minimo",
            "estado",
            "stock_inicial_por_confirmar",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["quantidade_stock", "codigo"]


class MedicamentoUrgenciaWriteSerializer(serializers.ModelSerializer):
    quantidade_inicial = serializers.IntegerField(min_value=0, required=False, write_only=True, default=0)

    class Meta:
        model = MedicamentoUrgencia
        fields = [
            "nome",
            "forma_apresentacao",
            "categoria",
            "unidade",
            "stock_minimo",
            "validade",
            "preco_referencia_fcfa",
            "quantidade_texto_original",
            "servico",
            "activo",
            "observacoes",
            "quantidade_inicial",
        ]

    def validate_categoria(self, value):
        if value not in CategoriaItemUrgencia.values:
            raise serializers.ValidationError("Categoria inválida.")
        return value


class MovimentoStockUrgenciaSerializer(serializers.ModelSerializer):
    medicamento_nome = serializers.CharField(source="medicamento.nome", read_only=True)
    operador_nome = serializers.SerializerMethodField()
    paciente_nome = serializers.CharField(source="paciente.full_name", read_only=True, default=None)
    tipo_label = serializers.SerializerMethodField()

    class Meta:
        model = MovimentoStockUrgencia
        fields = [
            "id",
            "medicamento",
            "medicamento_nome",
            "tipo",
            "tipo_label",
            "quantidade",
            "quantidade_antes",
            "quantidade_depois",
            "motivo",
            "origem",
            "operador",
            "operador_nome",
            "paciente",
            "paciente_nome",
            "consulta",
            "created_at",
        ]
        read_only_fields = fields

    def get_operador_nome(self, obj):
        if not obj.operador:
            return ""
        name = obj.operador.get_full_name()
        return name or obj.operador.email

    def get_tipo_label(self, obj) -> str:
        return {
            "ENTRADA": "Entrada",
            "SAIDA": "Saída",
            "AJUSTE": "Ajuste",
            "PERDA_EXPIRACAO": "Perda / Expiração",
        }.get(obj.tipo, obj.tipo)


class RegistarMovimentoSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=TipoMovimentoStockUrgencia.choices, required=False)
    quantidade = serializers.IntegerField(min_value=0)
    motivo = serializers.CharField(required=False, allow_blank=True, max_length=255)
    paciente = serializers.IntegerField(required=False, allow_null=True)
    consulta = serializers.IntegerField(required=False, allow_null=True)


class DefinirStockInicialSerializer(serializers.Serializer):
    quantidade = serializers.IntegerField(min_value=1)
    stock_minimo = serializers.IntegerField(min_value=0, required=False)
    validade = serializers.DateField(required=False, allow_null=True)
    unidade = serializers.CharField(required=False, allow_blank=True, max_length=30)
