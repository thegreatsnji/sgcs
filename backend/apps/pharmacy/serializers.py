from rest_framework import serializers

from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia


class MedicamentoUrgenciaSerializer(serializers.ModelSerializer):
    abaixo_minimo = serializers.BooleanField(read_only=True)
    servico_codigo = serializers.CharField(source="servico.codigo", read_only=True, default=None)

    class Meta:
        model = MedicamentoUrgencia
        fields = [
            "id",
            "codigo",
            "nome",
            "forma_apresentacao",
            "unidade",
            "quantidade_stock",
            "stock_minimo",
            "servico",
            "servico_codigo",
            "activo",
            "observacoes",
            "abaixo_minimo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["quantidade_stock"]


class MedicamentoUrgenciaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicamentoUrgencia
        fields = [
            "codigo",
            "nome",
            "forma_apresentacao",
            "unidade",
            "stock_minimo",
            "servico",
            "activo",
            "observacoes",
        ]


class MovimentoStockUrgenciaSerializer(serializers.ModelSerializer):
    medicamento_nome = serializers.CharField(source="medicamento.nome", read_only=True)
    operador_nome = serializers.CharField(source="operador.get_full_name", read_only=True)

    class Meta:
        model = MovimentoStockUrgencia
        fields = [
            "id",
            "medicamento",
            "medicamento_nome",
            "tipo",
            "quantidade",
            "quantidade_antes",
            "quantidade_depois",
            "motivo",
            "operador",
            "operador_nome",
            "created_at",
        ]


class RegistarMovimentoSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=["ENTRADA", "SAIDA", "AJUSTE"])
    quantidade = serializers.IntegerField(min_value=1)
    motivo = serializers.CharField(required=False, allow_blank=True, max_length=255)
