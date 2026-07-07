"""Serializers do módulo de faturação."""

from decimal import Decimal

from rest_framework import serializers

from apps.billing.models import (
    Fatura,
    ItemFatura,
    ItemOrcamento,
    Orcamento,
    Pagamento,
    Recibo,
    Servico,
)
from apps.billing.services.billing_service import BillingService


class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = (
            "id",
            "codigo",
            "nome",
            "descricao",
            "categoria",
            "preco",
            "activo",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ItemOrcamentoSerializer(serializers.ModelSerializer):
    servico_nome = serializers.CharField(source="servico.nome", read_only=True)

    class Meta:
        model = ItemOrcamento
        fields = (
            "id",
            "servico",
            "servico_nome",
            "quantidade",
            "preco_unitario",
            "subtotal",
        )
        read_only_fields = ("id", "subtotal", "servico_nome")


class OrcamentoSerializer(serializers.ModelSerializer):
    paciente_nome = serializers.CharField(source="paciente.full_name", read_only=True)
    criado_por_nome = serializers.SerializerMethodField()
    itens = ItemOrcamentoSerializer(many=True, read_only=True)
    editavel = serializers.BooleanField(source="is_editavel", read_only=True)

    class Meta:
        model = Orcamento
        fields = (
            "id",
            "numero",
            "paciente",
            "paciente_nome",
            "criado_por",
            "criado_por_nome",
            "estado",
            "subtotal",
            "desconto",
            "imposto",
            "total",
            "validade",
            "itens",
            "editavel",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "numero",
            "estado",
            "subtotal",
            "imposto",
            "total",
            "criado_por",
            "created_at",
            "updated_at",
        )

    def get_criado_por_nome(self, obj) -> str | None:
        return obj.criado_por.get_full_name() if obj.criado_por else None


class OrcamentoCreateSerializer(serializers.Serializer):
    paciente = serializers.IntegerField()
    validade = serializers.DateField(required=False, allow_null=True)
    desconto = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=Decimal("0"))
    itens = serializers.ListField(child=serializers.DictField(), required=False, default=list)

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        itens = []
        for item in validated_data.get("itens", []):
            itens.append(
                {
                    "servico_id": item["servico"],
                    "quantidade": item.get("quantidade", 1),
                    "preco_unitario": item.get("preco_unitario"),
                }
            )
        try:
            return BillingService.criar_orcamento(
                validated_data["paciente"],
                user,
                validade=validated_data.get("validade"),
                desconto=validated_data.get("desconto", Decimal("0")),
                itens=itens,
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class ItemFaturaSerializer(serializers.ModelSerializer):
    servico_nome = serializers.CharField(source="servico.nome", read_only=True)

    class Meta:
        model = ItemFatura
        fields = ("id", "servico", "servico_nome", "quantidade", "preco", "subtotal")
        read_only_fields = ("id", "subtotal", "servico_nome")


class PagamentoSerializer(serializers.ModelSerializer):
    fatura_numero = serializers.CharField(source="fatura.numero", read_only=True)
    recebido_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = Pagamento
        fields = (
            "id",
            "fatura",
            "fatura_numero",
            "metodo_pagamento",
            "valor",
            "referencia",
            "estado",
            "recebido_por",
            "recebido_por_nome",
            "data_pagamento",
            "created_at",
        )
        read_only_fields = ("id", "estado", "recebido_por", "data_pagamento", "created_at")

    def get_recebido_por_nome(self, obj) -> str | None:
        return obj.recebido_por.get_full_name() if obj.recebido_por else None


class FaturaSerializer(serializers.ModelSerializer):
    paciente_nome = serializers.CharField(source="paciente.full_name", read_only=True)
    consulta_numero = serializers.CharField(
        source="consulta.appointment_number", read_only=True, default=None
    )
    emitida_por_nome = serializers.SerializerMethodField()
    itens = ItemFaturaSerializer(many=True, read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    editavel = serializers.BooleanField(source="is_editavel", read_only=True)
    total_pago = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Fatura
        fields = (
            "id",
            "numero",
            "paciente",
            "paciente_nome",
            "consulta",
            "consulta_numero",
            "orcamento",
            "estado",
            "subtotal",
            "desconto",
            "imposto",
            "total",
            "total_pago",
            "emitida_em",
            "emitida_por",
            "emitida_por_nome",
            "itens",
            "pagamentos",
            "editavel",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "numero",
            "estado",
            "subtotal",
            "imposto",
            "total",
            "total_pago",
            "emitida_em",
            "emitida_por",
            "created_at",
            "updated_at",
        )

    def get_emitida_por_nome(self, obj) -> str | None:
        return obj.emitida_por.get_full_name() if obj.emitida_por else None


class FaturaCreateSerializer(serializers.Serializer):
    paciente = serializers.IntegerField(required=False)
    consulta = serializers.IntegerField(required=False, allow_null=True)
    orcamento = serializers.IntegerField(required=False, allow_null=True)
    desconto = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    itens = serializers.ListField(child=serializers.DictField(), required=False, default=list)

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        itens = []
        for item in validated_data.get("itens", []):
            itens.append(
                {
                    "servico_id": item["servico"],
                    "quantidade": item.get("quantidade", 1),
                    "preco": item.get("preco"),
                }
            )
        try:
            return BillingService.gerar_fatura(
                user,
                paciente_id=validated_data.get("paciente"),
                consulta_id=validated_data.get("consulta"),
                orcamento_id=validated_data.get("orcamento"),
                desconto=validated_data.get("desconto"),
                itens=itens if itens else None,
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate(self, attrs):
        if not attrs.get("orcamento") and not attrs.get("paciente"):
            raise serializers.ValidationError("Indique o paciente ou um orçamento aprovado.")
        return attrs


class PagamentoCreateSerializer(serializers.Serializer):
    fatura = serializers.IntegerField()
    metodo_pagamento = serializers.CharField()
    valor = serializers.DecimalField(max_digits=12, decimal_places=2)
    referencia = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return BillingService.registar_pagamento(
                validated_data["fatura"],
                user,
                valor=validated_data["valor"],
                metodo_pagamento=validated_data["metodo_pagamento"],
                referencia=validated_data.get("referencia", ""),
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class ReciboSerializer(serializers.ModelSerializer):
    pagamento_valor = serializers.DecimalField(
        source="pagamento.valor", max_digits=12, decimal_places=2, read_only=True
    )
    fatura_numero = serializers.CharField(source="pagamento.fatura.numero", read_only=True)
    paciente_nome = serializers.CharField(
        source="pagamento.fatura.paciente.full_name", read_only=True
    )
    metodo_pagamento = serializers.CharField(source="pagamento.metodo_pagamento", read_only=True)

    class Meta:
        model = Recibo
        fields = (
            "id",
            "numero",
            "pagamento",
            "pagamento_valor",
            "fatura_numero",
            "paciente_nome",
            "metodo_pagamento",
            "emitido_em",
        )
        read_only_fields = fields
