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
    ReducaoValorAutorizacao,
    Servico,
    ServicoPrecoHistorico,
)
from apps.billing.services.billing_service import BillingService


class ServicoSerializer(serializers.ModelSerializer):
    departamento_nome = serializers.CharField(source="departamento.nome", read_only=True)
    especialidade_nome = serializers.CharField(source="especialidade.nome", read_only=True)
    categoria_label = serializers.SerializerMethodField()
    motivo_alteracao_preco = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Servico
        fields = (
            "id",
            "codigo",
            "nome",
            "descricao",
            "categoria",
            "categoria_label",
            "departamento",
            "departamento_nome",
            "especialidade",
            "especialidade_nome",
            "preco",
            "moeda",
            "preco_confirmado",
            "preco_confirmado_em",
            "estado_validacao",
            "permite_faturacao_sem_preco_confirmado",
            "activo",
            "exige_pedido_medico",
            "exige_pagamento_antecipado",
            "permite_pagamento_parcial",
            "exige_agendamento",
            "gera_resultado",
            "duracao_minutos",
            "unidade_cobranca",
            "ordem",
            "observacoes",
            "created_at",
            "updated_at",
            "motivo_alteracao_preco",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "departamento_nome",
            "especialidade_nome",
            "preco_confirmado_em",
            "estado_validacao",
        )

    estado_validacao = serializers.CharField(source="estado_validacao_preco", read_only=True)

    def get_categoria_label(self, obj) -> str:
        return obj.get_categoria_display()

    def validate_preco(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if self.instance and "preco" in attrs and attrs["preco"] != self.instance.preco:
            from apps.billing.services.catalog_service import user_pode_alterar_preco

            if not user_pode_alterar_preco(user):
                raise serializers.ValidationError(
                    {"preco": "Sem permissão para alterar o preço oficial."}
                )
        return attrs

    def create(self, validated_data):
        validated_data.pop("motivo_alteracao_preco", None)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            validated_data["criado_por"] = user
            validated_data["actualizado_por"] = user
        if not validated_data.get("moeda"):
            from apps.billing.constants import DEFAULT_SERVICE_CURRENCY

            validated_data["moeda"] = DEFAULT_SERVICE_CURRENCY
        user = getattr(request, "user", None)
        from apps.billing.services.catalog_service import user_pode_alterar_preco

        if user and user_pode_alterar_preco(user) and validated_data.get("preco", 0) > 0:
            validated_data["preco_confirmado"] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        motivo = validated_data.pop("motivo_alteracao_preco", "")
        request = self.context.get("request")
        user = getattr(request, "user", None)
        preco = validated_data.get("preco")
        if preco is not None and preco != instance.preco and user:
            from apps.billing.services.catalog_service import registar_alteracao_preco

            registar_alteracao_preco(
                instance,
                instance.preco,
                preco,
                user=user,
                request=request,
                motivo=motivo,
                origem="manual",
            )
        if user and user.is_authenticated:
            validated_data["actualizado_por"] = user
        return super().update(instance, validated_data)


class ServicoPrecoHistoricoSerializer(serializers.ModelSerializer):
    alterado_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = ServicoPrecoHistorico
        fields = (
            "id",
            "preco_anterior",
            "preco_novo",
            "motivo",
            "origem",
            "alterado_por",
            "alterado_por_nome",
            "ip_address",
            "created_at",
        )

    def get_alterado_por_nome(self, obj) -> str | None:
        return obj.alterado_por.get_full_name() if obj.alterado_por else None


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
        fields = (
            "id",
            "servico",
            "servico_nome",
            "quantidade",
            "preco",
            "preco_oficial",
            "subtotal",
            "subtotal_oficial",
            "valor_reducao",
            "percentual_reducao",
            "motivo_reducao",
            "observacao_reducao",
            "origem_preco",
            "estado_autorizacao_reducao",
        )
        read_only_fields = (
            "id",
            "subtotal",
            "subtotal_oficial",
            "servico_nome",
            "valor_reducao",
            "percentual_reducao",
            "origem_preco",
            "estado_autorizacao_reducao",
        )


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
                    "preco_cobrado": item.get("preco_cobrado", item.get("preco")),
                    "motivo_reducao": item.get("motivo_reducao"),
                    "observacao_reducao": item.get("observacao_reducao"),
                    "autorizacao_reducao_id": item.get("autorizacao_reducao_id"),
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


class ReducaoValorAutorizacaoSerializer(serializers.ModelSerializer):
    servico_nome = serializers.CharField(source="servico.nome", read_only=True)
    servico_codigo = serializers.CharField(source="servico.codigo", read_only=True)
    solicitado_por_nome = serializers.SerializerMethodField()
    decidido_por_nome = serializers.SerializerMethodField()
    paciente_nome = serializers.CharField(source="paciente.full_name", read_only=True, default=None)

    class Meta:
        model = ReducaoValorAutorizacao
        fields = (
            "id",
            "servico",
            "servico_nome",
            "servico_codigo",
            "paciente",
            "paciente_nome",
            "fatura",
            "quantidade",
            "preco_oficial",
            "preco_proposto",
            "diferenca_unitaria",
            "percentual_reducao",
            "motivo_reducao",
            "observacao_solicitacao",
            "estado",
            "solicitado_por",
            "solicitado_por_nome",
            "solicitado_em",
            "decidido_por",
            "decidido_por_nome",
            "decidido_em",
            "observacao_decisao",
        )
        read_only_fields = (
            "id",
            "estado",
            "solicitado_por",
            "solicitado_em",
            "decidido_por",
            "decidido_em",
            "fatura",
        )

    def get_solicitado_por_nome(self, obj) -> str | None:
        return obj.solicitado_por.get_full_name() if obj.solicitado_por else None

    def get_decidido_por_nome(self, obj) -> str | None:
        return obj.decidido_por.get_full_name() if obj.decidido_por else None


class ReducaoValorSolicitarSerializer(serializers.Serializer):
    servico = serializers.IntegerField()
    paciente = serializers.IntegerField(required=False, allow_null=True)
    quantidade = serializers.IntegerField(required=False, default=1)
    preco_proposto = serializers.DecimalField(max_digits=12, decimal_places=2)
    motivo_reducao = serializers.CharField()
    observacao = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        from apps.billing.services.reduction_service import ReductionError, solicitar_autorizacao_reducao

        user = self.context["request"].user
        try:
            return solicitar_autorizacao_reducao(
                user,
                servico_id=validated_data["servico"],
                paciente_id=validated_data.get("paciente"),
                quantidade=validated_data.get("quantidade", 1),
                preco_proposto=validated_data["preco_proposto"],
                motivo_reducao=validated_data["motivo_reducao"],
                observacao=validated_data.get("observacao", ""),
                request=self.context["request"],
            )
        except ReductionError as exc:
            raise serializers.ValidationError(str(exc)) from exc


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
