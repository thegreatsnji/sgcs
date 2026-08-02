"""Modelos de configuração da clínica e administração do sistema."""

from django.conf import settings
from django.db import models

from apps.settings.constants import DEFAULT_BILLING, DEFAULT_CURRENCY, DEFAULT_LANGUAGE, DEFAULT_TIMEZONE
from core.mixins import TimestampMixin


class ClinicSetting(models.Model):
    key = models.CharField("Chave", max_length=100, unique=True)
    value = models.JSONField("Valor", default=dict)
    description = models.TextField("Descrição", blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"
        ordering = ["key"]

    def __str__(self) -> str:
        return self.key


class PerfilClinica(TimestampMixin):
    nome = models.CharField("Nome da clínica", max_length=200, default="SauVida Clínica")
    logotipo = models.ImageField("Logótipo", upload_to="clinic/logo/", blank=True, null=True)
    nif = models.CharField("NIF", max_length=30, blank=True)
    morada = models.CharField("Morada", max_length=255, blank=True)
    cidade = models.CharField("Cidade", max_length=100, blank=True)
    pais = models.CharField("País", max_length=100, default="Guiné-Bissau")
    telefone = models.CharField("Telefone", max_length=30, blank=True)
    telemovel = models.CharField("Telemóvel", max_length=30, blank=True)
    email = models.EmailField("E-mail", blank=True)
    website = models.URLField("Website", blank=True)
    moeda = models.CharField("Moeda", max_length=10, default=DEFAULT_CURRENCY)
    fuso_horario = models.CharField("Fuso horário", max_length=50, default=DEFAULT_TIMEZONE)
    idioma = models.CharField("Idioma", max_length=10, default=DEFAULT_LANGUAGE)
    horario_funcionamento = models.TextField("Horário de funcionamento", blank=True)
    dias_uteis = models.JSONField("Dias úteis", default=list)
    mensagem_rodape = models.TextField("Mensagem do rodapé", blank=True)
    contacto_urgencia = models.CharField("Contacto de urgência", max_length=50, blank=True)
    texto_legal = models.TextField("Texto legal", blank=True)
    assinatura_digital = models.ImageField(
        "Assinatura digital", upload_to="clinic/signature/", blank=True, null=True
    )

    class Meta:
        verbose_name = "Perfil da clínica"
        verbose_name_plural = "Perfil da clínica"

    def __str__(self) -> str:
        return self.nome


class EspecialidadeMedica(TimestampMixin):
    codigo = models.CharField("Código", max_length=20, unique=True)
    nome = models.CharField("Nome", max_length=150)
    descricao = models.TextField("Descrição", blank=True)
    cor = models.CharField("Cor", max_length=7, default="#1e40af")
    activo = models.BooleanField("Activo", default=True)
    duracao_consulta_minutos = models.PositiveIntegerField("Duração consulta (min)", default=30)
    departamento = models.ForeignKey(
        "clinic_settings.Departamento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="especialidades",
        verbose_name="Departamento",
    )
    ordem = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Especialidade médica"
        verbose_name_plural = "Especialidades médicas"
        ordering = ["ordem", "nome"]

    def __str__(self) -> str:
        return self.nome


class Departamento(TimestampMixin):
    codigo = models.CharField("Código", max_length=20, unique=True)
    nome = models.CharField("Nome", max_length=150)
    descricao = models.TextField("Descrição", blank=True)
    activo = models.BooleanField("Activo", default=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departamentos_responsavel",
        verbose_name="Responsável",
    )
    localizacao = models.CharField("Localização", max_length=150, blank=True)
    horario = models.TextField("Horário", blank=True)
    contactos_internos = models.TextField("Contactos internos", blank=True)
    ordem = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ["ordem", "nome"]

    def __str__(self) -> str:
        return self.nome


class Consultorio(TimestampMixin):
    numero = models.CharField("Número", max_length=20, unique=True)
    nome = models.CharField("Nome", max_length=150)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name="consultorios",
        verbose_name="Departamento",
    )
    capacidade = models.PositiveIntegerField("Capacidade", default=1)
    equipamentos = models.TextField("Equipamentos", blank=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Consultório / Sala"
        verbose_name_plural = "Consultórios / Salas"
        ordering = ["numero"]

    def __str__(self) -> str:
        return f"{self.numero} — {self.nome}"


class HorarioFuncionamento(TimestampMixin):
    dia_semana = models.CharField("Dia da semana", max_length=3)
    hora_abertura = models.TimeField("Hora de abertura")
    hora_encerramento = models.TimeField("Hora de encerramento")
    intervalo_minutos = models.PositiveIntegerField("Intervalo (min)", default=0)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Horário de funcionamento"
        verbose_name_plural = "Horários de funcionamento"
        ordering = ["dia_semana"]
        unique_together = [("dia_semana",)]

    def __str__(self) -> str:
        return f"{self.dia_semana}: {self.hora_abertura}-{self.hora_encerramento}"


class Feriado(TimestampMixin):
    data = models.DateField("Data")
    nome = models.CharField("Nome", max_length=150)
    recorrente = models.BooleanField("Recorrente anualmente", default=False)

    class Meta:
        verbose_name = "Feriado"
        verbose_name_plural = "Feriados"
        ordering = ["data"]

    def __str__(self) -> str:
        return f"{self.data} — {self.nome}"


class TipoConsulta(TimestampMixin):
    codigo = models.CharField("Código", max_length=20, unique=True)
    nome = models.CharField("Nome", max_length=150)
    descricao = models.TextField("Descrição", blank=True)
    duracao_minutos = models.PositiveIntegerField("Duração (min)", default=30)
    preco_base = models.DecimalField("Preço base", max_digits=12, decimal_places=2, default=0)
    cor = models.CharField("Cor", max_length=7, default="#0d9488")
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Tipo de consulta"
        verbose_name_plural = "Tipos de consulta"
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class TipoExameLaboratorio(TimestampMixin):
    codigo = models.CharField("Código", max_length=64, unique=True)
    nome = models.CharField("Nome", max_length=150)
    categoria = models.CharField("Categoria", max_length=50)
    unidade = models.CharField("Unidade", max_length=30, blank=True)
    valor_referencia = models.CharField("Valor de referência", max_length=100, blank=True)
    tempo_medio_horas = models.PositiveIntegerField("Tempo médio (h)", default=24)
    activo = models.BooleanField("Activo", default=True)
    servico = models.ForeignKey(
        "billing.Servico",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tipos_exame_laboratorio",
        verbose_name="Serviço de faturação",
    )
    tipo_amostra = models.CharField("Tipo de amostra", max_length=80, blank=True)
    recipiente = models.CharField("Recipiente", max_length=80, blank=True)
    instrucoes_colheita = models.TextField("Instruções de colheita", blank=True)
    exige_jejum = models.BooleanField("Exige jejum", default=False)
    ordem = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Tipo de exame laboratorial"
        verbose_name_plural = "Tipos de exames laboratoriais"
        ordering = ["ordem", "nome"]

    def __str__(self) -> str:
        return self.nome


class ConfiguracaoFaturacao(TimestampMixin):
    iva_percentagem = models.DecimalField("IVA (%)", max_digits=5, decimal_places=2, default=0)
    moeda = models.CharField("Moeda", max_length=10, default=DEFAULT_CURRENCY)
    serie_faturas = models.CharField("Série faturas", max_length=20, default=DEFAULT_BILLING["serie_faturas"])
    serie_recibos = models.CharField("Série recibos", max_length=20, default=DEFAULT_BILLING["serie_recibos"])
    serie_orcamentos = models.CharField("Série orçamentos", max_length=20, default=DEFAULT_BILLING["serie_orcamentos"])
    desconto_maximo_percentagem = models.DecimalField("Desconto máximo (%)", max_digits=5, decimal_places=2, default=20)
    permitir_reducao_rececao = models.BooleanField("Permitir redução na receção", default=True)
    limite_reducao_rececao_percentual = models.DecimalField(
        "Limite de redução na receção (%)",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Deixar vazio até a clínica definir o limite.",
    )
    exigir_motivo_reducao = models.BooleanField("Exigir motivo de redução", default=True)
    exigir_autorizacao_acima_limite = models.BooleanField(
        "Exigir autorização acima do limite", default=True
    )
    permitir_valor_zero = models.BooleanField("Permitir valor cobrado zero", default=False)
    exigir_observacao_acima_percentual = models.DecimalField(
        "Exigir observação acima de (%)",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    notificar_director_reducao = models.BooleanField("Notificar direção sobre reduções", default=False)
    mostrar_reducao_no_recibo = models.BooleanField(
        "Mostrar redução no recibo entregue ao paciente", default=False
    )
    mostrar_preco_oficial_recibo = models.BooleanField(
        "Mostrar preço oficial no recibo", default=False
    )
    mostrar_reducao_recibo = models.BooleanField(
        "Mostrar linha de redução no recibo", default=False
    )
    mostrar_saldo_recibo = models.BooleanField("Mostrar saldo pendente no recibo", default=True)
    mostrar_ministerio_saude_recibo = models.BooleanField(
        "Mostrar referência ao Ministério da Saúde Pública", default=False
    )
    mostrar_valor_por_extenso = models.BooleanField(
        "Mostrar valor por extenso no recibo", default=False
    )
    formato_recibo = models.CharField(
        "Formato do recibo",
        max_length=20,
        default="A4",
        choices=[
            ("A4", "A4"),
            ("A5", "A5"),
            ("TERMICO_80", "Térmico 80 mm"),
        ],
    )
    texto_rodape_recibo = models.TextField("Texto do rodapé do recibo", blank=True)
    numero_inicial_recibo = models.PositiveIntegerField("Número inicial recibo", default=1)
    metodos_pagamento = models.JSONField("Métodos de pagamento", default=list)

    class Meta:
        verbose_name = "Configuração de faturação"
        verbose_name_plural = "Configuração de faturação"

    def __str__(self) -> str:
        return "Configuração de faturação"


class ConfiguracaoEmail(TimestampMixin):
    host = models.CharField("Host SMTP", max_length=200, blank=True)
    port = models.PositiveIntegerField("Porta", default=587)
    use_ssl = models.BooleanField("SSL", default=False)
    use_tls = models.BooleanField("TLS", default=True)
    username = models.CharField("Utilizador", max_length=150, blank=True)
    password = models.CharField("Password", max_length=255, blank=True)
    from_email = models.EmailField("E-mail remetente", blank=True)

    class Meta:
        verbose_name = "Configuração de e-mail"
        verbose_name_plural = "Configuração de e-mail"

    def __str__(self) -> str:
        return self.host or "SMTP"


class ConfiguracaoSms(TimestampMixin):
    provider = models.CharField("Fornecedor", max_length=100, blank=True)
    api_key = models.CharField("API Key", max_length=255, blank=True)
    sender_id = models.CharField("Sender ID", max_length=50, blank=True)
    activo = models.BooleanField("Activo", default=False)

    class Meta:
        verbose_name = "Configuração SMS"
        verbose_name_plural = "Configuração SMS"


class ConfiguracaoSeguranca(TimestampMixin):
    sessao_maxima_minutos = models.PositiveIntegerField("Sessão máxima (min)", default=480)
    password_min_length = models.PositiveIntegerField("Tamanho mínimo password", default=8)
    password_require_upper = models.BooleanField("Exigir maiúsculas", default=True)
    password_require_number = models.BooleanField("Exigir números", default=True)
    password_require_special = models.BooleanField("Exigir caracteres especiais", default=False)
    password_expiry_days = models.PositiveIntegerField("Expiração password (dias)", default=90)
    password_history_count = models.PositiveIntegerField("Histórico passwords", default=5)
    max_login_attempts = models.PositiveIntegerField("Tentativas máximas", default=5)
    lockout_minutes = models.PositiveIntegerField("Bloqueio (min)", default=30)
    two_factor_enabled = models.BooleanField("2FA activo", default=False)

    class Meta:
        verbose_name = "Configuração de segurança"
        verbose_name_plural = "Configuração de segurança"


class ConfiguracaoFicheiros(TimestampMixin):
    max_upload_mb = models.PositiveIntegerField("Tamanho máximo (MB)", default=10)
    allowed_types = models.JSONField("Tipos permitidos", default=list)
    storage_backend = models.CharField("Armazenamento", max_length=50, default="local")

    class Meta:
        verbose_name = "Configuração de ficheiros"
        verbose_name_plural = "Configuração de ficheiros"


class FeatureFlag(TimestampMixin):
    codigo = models.CharField("Código", max_length=50, unique=True)
    nome = models.CharField("Nome", max_length=150)
    descricao = models.TextField("Descrição", blank=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Feature flag"
        verbose_name_plural = "Feature flags"
        ordering = ["codigo"]

    def __str__(self) -> str:
        return self.codigo


class BackupRegisto(TimestampMixin):
    TIPO_MANUAL = "MANUAL"
    TIPO_AUTOMATICO = "AUTOMATICO"
    TIPO_CHOICES = [(TIPO_MANUAL, "Manual"), (TIPO_AUTOMATICO, "Automático")]

    ESTADO_PENDENTE = "PENDENTE"
    ESTADO_CONCLUIDO = "CONCLUIDO"
    ESTADO_ERRO = "ERRO"
    ESTADO_CHOICES = [
        (ESTADO_PENDENTE, "Pendente"),
        (ESTADO_CONCLUIDO, "Concluído"),
        (ESTADO_ERRO, "Erro"),
    ]

    tipo = models.CharField("Tipo", max_length=15, choices=TIPO_CHOICES, default=TIPO_MANUAL)
    estado = models.CharField("Estado", max_length=15, choices=ESTADO_CHOICES, default=ESTADO_PENDENTE)
    ficheiro = models.CharField("Ficheiro", max_length=500, blank=True)
    tamanho_bytes = models.BigIntegerField("Tamanho (bytes)", default=0)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backups_criados",
        verbose_name="Criado por",
    )
    observacoes = models.TextField("Observações", blank=True)

    class Meta:
        verbose_name = "Registo de backup"
        verbose_name_plural = "Registos de backup"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Backup {self.tipo} — {self.estado}"


class MedicoPerfil(TimestampMixin):
    utilizador = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_medico",
        verbose_name="Médico",
    )
    especialidade = models.ForeignKey(
        EspecialidadeMedica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicos",
        verbose_name="Especialidade",
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicos",
        verbose_name="Departamento",
    )
    numero_profissional = models.CharField("Número profissional", max_length=50, blank=True)
    dias_trabalho = models.JSONField("Dias de trabalho", default=list, blank=True)
    horario_atendimento = models.JSONField("Horário de atendimento", default=dict, blank=True)
    duracao_consulta_minutos = models.PositiveIntegerField("Duração consulta (min)", default=30)
    servico_consulta = models.ForeignKey(
        "billing.Servico",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicos_consulta",
        verbose_name="Serviço de consulta",
    )
    activo = models.BooleanField("Activo", default=True)
    disponivel_marcacao = models.BooleanField("Disponível para marcação", default=True)

    class Meta:
        verbose_name = "Perfil médico"
        verbose_name_plural = "Perfis médicos"

    def __str__(self) -> str:
        return f"Perfil médico — {self.utilizador.get_full_name()}"
