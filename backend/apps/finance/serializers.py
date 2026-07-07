"""Serializers do módulo financeiro."""

from rest_framework import serializers

from apps.finance.models import Caixa, CategoriaFinanceira, Despesa, MovimentoFinanceiro
from apps.finance.services.finance_service import FinanceService


class CategoriaFinanceiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaFinanceira
        fields = ("id", "nome", "tipo", "descricao", "activa", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class CaixaSerializer(serializers.ModelSerializer):
    utilizador_abertura_nome = serializers.SerializerMethodField()
    utilizador_fecho_nome = serializers.SerializerMethodField()

    class Meta:
        model = Caixa
        fields = (
            "id",
            "codigo",
            "nome",
            "estado",
            "saldo_inicial",
            "saldo_actual",
            "data_abertura",
            "data_fecho",
            "utilizador_abertura",
            "utilizador_abertura_nome",
            "utilizador_fecho",
            "utilizador_fecho_nome",
            "observacoes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "estado",
            "saldo_actual",
            "data_abertura",
            "data_fecho",
            "utilizador_abertura",
            "utilizador_fecho",
            "created_at",
            "updated_at",
        )

    def get_utilizador_abertura_nome(self, obj):
        return obj.utilizador_abertura.get_full_name() if obj.utilizador_abertura else None

    def get_utilizador_fecho_nome(self, obj):
        return obj.utilizador_fecho.get_full_name() if obj.utilizador_fecho else None


class MovimentoFinanceiroSerializer(serializers.ModelSerializer):
    caixa_codigo = serializers.CharField(source="caixa.codigo", read_only=True)
    utilizador_nome = serializers.SerializerMethodField()

    class Meta:
        model = MovimentoFinanceiro
        fields = (
            "id",
            "caixa",
            "caixa_codigo",
            "tipo",
            "origem",
            "valor",
            "descricao",
            "referencia",
            "pagamento",
            "despesa",
            "utilizador",
            "utilizador_nome",
            "data",
            "created_at",
        )
        read_only_fields = fields

    def get_utilizador_nome(self, obj):
        return obj.utilizador.get_full_name() if obj.utilizador else None


class DespesaSerializer(serializers.ModelSerializer):
    criado_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = Despesa
        fields = (
            "id",
            "fornecedor",
            "categoria",
            "categoria_financeira",
            "valor",
            "descricao",
            "estado",
            "data",
            "observacoes",
            "criado_por",
            "criado_por_nome",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "estado", "criado_por", "created_at", "updated_at")

    def get_criado_por_nome(self, obj):
        return obj.criado_por.get_full_name() if obj.criado_por else None


class DespesaCreateSerializer(serializers.Serializer):
    fornecedor = serializers.CharField(max_length=150)
    categoria = serializers.CharField(required=False, default="OUTROS")
    categoria_financeira = serializers.IntegerField(required=False, allow_null=True)
    valor = serializers.DecimalField(max_digits=14, decimal_places=2)
    descricao = serializers.CharField()
    data = serializers.DateField()
    observacoes = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        return FinanceService.criar_despesa(user, validated_data, request=request)
