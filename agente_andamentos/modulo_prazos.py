"""
MÓDULO DE PRAZOS PROCESSUAIS — DE BRITO ADVOCACIA
Dr. Jefferson Silva de Brito | OAB/RO 2952

Cobre: Cível (CPC), Trabalhista (CLT/PJe), Criminal (CPP)
Lógica: detecta movimento → calcula prazo → gera 4 marcos + prazo final
"""

from datetime import datetime, date, timedelta
from typing import Optional

# ─────────────────────────────────────────────────────────────────
# FERIADOS — Porto Velho / Rondônia / Nacional
#
# Fontes:
#   Nacional   : Lei 9.093/95, Lei 662/49, Lei 14.759/2023 (20/nov)
#   Estadual RO: Decreto nº 31.210/2026 (feriados + pontos facultativos)
#   Municipal  : Decreto Municipal PVH nº 21.691/2025 (calendário 2026)
#                Decreto 25.709/2021 (Nossa Senhora Auxiliadora)
#   TJRO       : Res. 032/2016-PR/TJRO + CPC art. 220 + CNJ Res. 244/2016
#                Suspensão de prazos: 20/dez a 20/jan (CPC art. 220)
# ─────────────────────────────────────────────────────────────────

# Feriados e pontos facultativos FIXOS (MM-DD, valem todo ano)
_FERIADOS_FIXOS = {
    # ── Nacionais ──────────────────────────────────────────────
    '01-01': 'Confraternização Universal',
    '04-21': 'Tiradentes',
    '05-01': 'Dia do Trabalho',
    '09-07': 'Independência do Brasil',
    '10-12': 'Nossa Senhora Aparecida',
    '11-02': 'Finados',
    '11-15': 'Proclamação da República',
    '11-20': 'Consciência Negra (Lei 14.759/2023)',
    '12-25': 'Natal',
    # ── Estadual RO ────────────────────────────────────────────
    '01-04': 'Instalação do Estado de Rondônia',
    # ── Municipais Porto Velho ──────────────────────────────────
    '01-24': 'Instalação do Município de Porto Velho',
    '05-24': 'Nossa Senhora Auxiliadora — Padroeira de Porto Velho',
    '10-02': 'Aniversário de Porto Velho (Decreto Municipal 21.691/2025)',
    # ── Pontos facultativos fixos (suspendem prazos forenses) ──
    '12-24': 'Véspera de Natal',
    '12-31': 'Véspera de Ano-Novo',
}

# Pontos facultativos VARIÁVEIS por ano — atualizar em janeiro de cada ano
# Fonte: Decreto estadual anual (Decreto RO 31.210/2026 para 2026)
_PONTOS_FACULTATIVOS_ANUAIS: dict[int, set] = {
    2026: {
        date(2026,  1,  2),  # Sexta após Ano-Novo
        date(2026,  2, 18),  # Quarta-feira de Cinzas (manhã)
        date(2026,  4,  2),  # Quinta-feira Semana Santa
        date(2026,  4, 20),  # Segunda após Páscoa
        date(2026,  6,  5),  # Sexta após Corpus Christi
        date(2026, 10, 30),  # Dia do Servidor Público (transferido)
    },
}


def _no_recesso(d: date) -> bool:
    """
    CPC art. 220: prazos suspensos de 20/dez a 20/jan (inclusive).
    TJRO Res. 032/2016 + CNJ Res. 244/2016.
    """
    mm, dd = d.month, d.day
    if mm == 12 and dd >= 20:
        return True
    if mm == 1 and dd <= 20:
        return True
    return False


def _feriados_moveis(ano: int) -> set:
    """
    Feriados e pontos facultativos móveis baseados na Páscoa (algoritmo de Gauss).
    Inclui: Segunda e Terça de Carnaval, Quarta de Cinzas (manhã),
            Sexta-feira da Paixão, Corpus Christi, Sexta após Corpus.
    """
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d_ = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d_ - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    pascoa = date(ano, mes, dia)

    return {
        pascoa - timedelta(days=48),  # Segunda de Carnaval
        pascoa - timedelta(days=47),  # Terça de Carnaval
        pascoa - timedelta(days=46),  # Quarta de Cinzas (ponto facultativo - manhã)
        pascoa - timedelta(days=2),   # Sexta-feira da Paixão (feriado nacional)
        pascoa + timedelta(days=60),  # Corpus Christi
        pascoa + timedelta(days=61),  # Sexta após Corpus Christi (decreto RO)
    }


_cache_moveis: dict = {}

def _get_moveis(ano: int) -> set:
    if ano not in _cache_moveis:
        _cache_moveis[ano] = _feriados_moveis(ano)
    return _cache_moveis[ano]


def _eh_util(d: date) -> bool:
    """
    Retorna True se o dia é dia útil forense em Porto Velho/TJRO:
    - Segunda a sexta
    - Não é feriado/ponto facultativo nacional, estadual RO ou municipal PVH
    - Não é feriado móvel (Carnaval, Paixão, Corpus Christi, etc.)
    - Não está no período de suspensão TJRO (20/dez a 20/jan — CPC art. 220)
    """
    if d.weekday() >= 5:
        return False
    chave = f'{d.month:02d}-{d.day:02d}'
    if chave in _FERIADOS_FIXOS:
        return False
    if d in _get_moveis(d.year):
        return False
    if d in _PONTOS_FACULTATIVOS_ANUAIS.get(d.year, set()):
        return False
    if _no_recesso(d):
        return False
    return True


def _proximo_util(d: date) -> date:
    """Retorna o próximo dia útil a partir de d (inclusive)."""
    while not _eh_util(d):
        d += timedelta(days=1)
    return d

def _somar_uteis(inicio: date, n: int) -> date:
    """Soma n dias úteis a partir de inicio (inclusive)."""
    atual = inicio
    contados = 0
    while contados < n:
        if _eh_util(atual):
            contados += 1
        if contados < n:
            atual += timedelta(days=1)
    return atual

# ─────────────────────────────────────────────────────────────────
# TABELA MESTRA DE PRAZOS
# Fonte: CPC/2015, CLT, CPP, Lei 9.099/95, Lei 6.830/80
# ─────────────────────────────────────────────────────────────────

TABELA_PRAZOS = {

    # ══════════════════════════════════════════
    # CÍVEL — CPC/2015
    # ══════════════════════════════════════════

    # RECURSOS
    "apelação": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Apelação (CPC art. 1.003)",
        "fundamento": "Art. 1.009 e 1.003 §5º CPC",
        "urgente": False,
    },
    "agravo de instrumento": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Agravo de Instrumento (CPC art. 1.015)",
        "fundamento": "Art. 1.016 e 1.003 §5º CPC",
        "urgente": False,
    },
    "agravo interno": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Agravo Interno (CPC art. 1.021)",
        "fundamento": "Art. 1.021 §2º CPC",
        "urgente": False,
    },
    "agravo regimental": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Agravo Regimental",
        "fundamento": "Regimento interno do tribunal",
        "urgente": False,
    },
    "embargos de declaração": {
        "area": "civel",
        "dias": 5,
        "tipo_contagem": "uteis",
        "descricao": "Embargos de Declaração (CPC art. 1.022)",
        "fundamento": "Art. 1.023 CPC",
        "urgente": True,
    },
    "embargos de declaração trabalhista": {
        "area": "trabalhista",
        "dias": 5,
        "tipo_contagem": "uteis",
        "descricao": "Embargos de Declaração (CLT art. 897-A)",
        "fundamento": "Art. 897-A CLT",
        "urgente": True,
    },
    "recurso especial": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Recurso Especial (CPC art. 1.029)",
        "fundamento": "Art. 1.029 e 1.003 §5º CPC",
        "urgente": False,
    },
    "recurso extraordinário": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Recurso Extraordinário (CPC art. 1.029)",
        "fundamento": "Art. 1.029 e 1.003 §5º CPC",
        "urgente": False,
    },
    "contrarrazões de apelação": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Contrarrazões de Apelação (CPC art. 1.010)",
        "fundamento": "Art. 1.010 §1º CPC",
        "urgente": False,
    },

    # CONTESTAÇÃO / RESPOSTA
    "citação cível": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Prazo para Contestação (CPC art. 335)",
        "fundamento": "Art. 335 CPC",
        "urgente": False,
    },
    "citação procedimento sumário": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Contestação — Procedimento Comum",
        "fundamento": "Art. 335 CPC",
        "urgente": False,
    },
    "citação juizado especial": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "corridos",
        "descricao": "Resposta — Juizado Especial Cível (Lei 9.099/95)",
        "fundamento": "Art. 30 Lei 9.099/95",
        "urgente": False,
    },
    "impugnação ao cumprimento de sentença": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Impugnação ao Cumprimento de Sentença (CPC art. 525)",
        "fundamento": "Art. 525 CPC",
        "urgente": False,
    },
    "embargos à execução": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Embargos à Execução (CPC art. 915)",
        "fundamento": "Art. 915 CPC",
        "urgente": False,
    },
    "embargos à execução fiscal": {
        "area": "civel",
        "dias": 30,
        "tipo_contagem": "corridos",
        "descricao": "Embargos à Execução Fiscal (Lei 6.830/80)",
        "fundamento": "Art. 16 Lei 6.830/80",
        "urgente": False,
    },
    "embargos de terceiro": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Embargos de Terceiro (CPC art. 674)",
        "fundamento": "Art. 675 CPC",
        "urgente": False,
    },
    "exceção de pré-executividade": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Exceção de Pré-Executividade (construção jurisprudencial)",
        "fundamento": "Jurisprudência STJ — prazo razoável",
        "urgente": False,
    },

    # MANIFESTAÇÕES / INTIMAÇÕES GERAIS
    "intimação para manifestação": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Manifestação nos autos (CPC art. 218)",
        "fundamento": "Art. 218 §3º CPC — prazo geral 15 dias",
        "urgente": False,
    },
    "intimação para juntar documentos": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Juntada de Documentos (CPC art. 218)",
        "fundamento": "Art. 218 §3º CPC",
        "urgente": False,
    },
    "réplica": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Réplica à Contestação (CPC art. 350/351)",
        "fundamento": "Art. 350/351 CPC",
        "urgente": False,
    },

    # ══════════════════════════════════════════
    # EXECUÇÃO CÍVEL / CUMPRIMENTO DE SENTENÇA
    # ══════════════════════════════════════════

    "cumprimento de sentença — pagamento": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Pagamento em Cumprimento de Sentença (CPC art. 523)",
        "fundamento": "Art. 523 CPC — multa de 10% + honorários se não pagar",
        "urgente": True,
    },
    "penhora realizada": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Impugnação à Penhora (CPC art. 525)",
        "fundamento": "Art. 525 CPC",
        "urgente": False,
    },
    "avaliação de bem": {
        "area": "civel",
        "dias": 15,
        "tipo_contagem": "uteis",
        "descricao": "Impugnação à Avaliação (CPC art. 873)",
        "fundamento": "Art. 873 CPC",
        "urgente": False,
    },

    # ══════════════════════════════════════════
    # TRABALHISTA — CLT / PJe TRT14
    # ══════════════════════════════════════════

    "citação trabalhista": {
        "area": "trabalhista",
        "dias": 5,
        "tipo_contagem": "uteis",
        "descricao": "Apresentação de Defesa Trabalhista (CLT art. 847)",
        "fundamento": "Art. 847 CLT — defesa oral ou escrita na audiência",
        "urgente": True,
    },
    "recurso ordinário trabalhista": {
        "area": "trabalhista",
        "dias": 8,
        "tipo_contagem": "uteis",
        "descricao": "Recurso Ordinário Trabalhista (CLT art. 895)",
        "fundamento": "Art. 895 CLT",
        "urgente": True,
    },
    "contrarrazões recurso ordinário": {
        "area": "trabalhista",
        "dias": 8,
        "tipo_contagem": "uteis",
        "descricao": "Contrarrazões ao Recurso Ordinário (CLT art. 895)",
        "fundamento": "Art. 900 CLT",
        "urgente": True,
    },
    "recurso de revista": {
        "area": "trabalhista",
        "dias": 8,
        "tipo_contagem": "uteis",
        "descricao": "Recurso de Revista (CLT art. 896)",
        "fundamento": "Art. 896 CLT",
        "urgente": True,
    },
    "agravo de petição trabalhista": {
        "area": "trabalhista",
        "dias": 8,
        "tipo_contagem": "uteis",
        "descricao": "Agravo de Petição (CLT art. 897)",
        "fundamento": "Art. 897 §1º CLT",
        "urgente": True,
    },
    "agravo de instrumento trabalhista": {
        "area": "trabalhista",
        "dias": 8,
        "tipo_contagem": "uteis",
        "descricao": "Agravo de Instrumento Trabalhista (CLT art. 897)",
        "fundamento": "Art. 897 b CLT",
        "urgente": True,
    },
    "execução trabalhista — pagamento": {
        "area": "trabalhista",
        "dias": 48,
        "tipo_contagem": "horas",
        "descricao": "Pagamento em Execução Trabalhista (CLT art. 880)",
        "fundamento": "Art. 880 CLT — 48 horas para pagamento ou nomeação à penhora",
        "urgente": True,
    },
    "impugnação à sentença de liquidação": {
        "area": "trabalhista",
        "dias": 8,
        "tipo_contagem": "uteis",
        "descricao": "Impugnação à Sentença de Liquidação (CLT art. 884)",
        "fundamento": "Art. 884 CLT",
        "urgente": True,
    },
    "embargos à execução trabalhista": {
        "area": "trabalhista",
        "dias": 5,
        "tipo_contagem": "uteis",
        "descricao": "Embargos à Execução Trabalhista (CLT art. 884)",
        "fundamento": "Art. 884 CLT",
        "urgente": True,
    },

    # ══════════════════════════════════════════
    # CRIMINAL — CPP
    # ══════════════════════════════════════════

    "apelação criminal": {
        "area": "criminal",
        "dias": 5,
        "tipo_contagem": "corridos",
        "descricao": "Apelação Criminal (CPP art. 593)",
        "fundamento": "Art. 593 e 600 CPP — interposição em 5 dias",
        "urgente": True,
    },
    "razões de apelação criminal": {
        "area": "criminal",
        "dias": 8,
        "tipo_contagem": "corridos",
        "descricao": "Razões de Apelação Criminal (CPP art. 600)",
        "fundamento": "Art. 600 CPP",
        "urgente": True,
    },
    "recurso em sentido estrito": {
        "area": "criminal",
        "dias": 5,
        "tipo_contagem": "corridos",
        "descricao": "Recurso em Sentido Estrito (CPP art. 581)",
        "fundamento": "Art. 586 CPP",
        "urgente": True,
    },
    "embargos de declaração criminal": {
        "area": "criminal",
        "dias": 2,
        "tipo_contagem": "corridos",
        "descricao": "Embargos de Declaração Criminal (CPP art. 619)",
        "fundamento": "Art. 619 CPP",
        "urgente": True,
    },
    "resposta à acusação": {
        "area": "criminal",
        "dias": 10,
        "tipo_contagem": "corridos",
        "descricao": "Resposta à Acusação (CPP art. 396-A)",
        "fundamento": "Art. 396-A CPP",
        "urgente": True,
    },
    "defesa prévia": {
        "area": "criminal",
        "dias": 10,
        "tipo_contagem": "corridos",
        "descricao": "Defesa Prévia / Resposta à Acusação (CPP art. 396-A)",
        "fundamento": "Art. 396-A CPP",
        "urgente": True,
    },
    "alegações finais criminal": {
        "area": "criminal",
        "dias": 5,
        "tipo_contagem": "uteis",
        "descricao": "Alegações Finais (CPP art. 403)",
        "fundamento": "Art. 403 CPP",
        "urgente": True,
    },
    "memorial criminal": {
        "area": "criminal",
        "dias": 5,
        "tipo_contagem": "uteis",
        "descricao": "Memorial / Alegações Finais por escrito (CPP art. 403 §3º)",
        "fundamento": "Art. 403 §3º CPP",
        "urgente": True,
    },
    "habeas corpus": {
        "area": "criminal",
        "dias": 0,
        "tipo_contagem": "urgente",
        "descricao": "Habeas Corpus — SEM PRAZO PEREMPTÓRIO",
        "fundamento": "Art. 647 CPP — pode ser impetrado a qualquer tempo",
        "urgente": True,
    },
    "mandado de segurança": {
        "area": "civel",
        "dias": 120,
        "tipo_contagem": "corridos",
        "descricao": "Mandado de Segurança (Lei 12.016/09)",
        "fundamento": "Art. 23 Lei 12.016/09 — 120 dias do ato coator",
        "urgente": False,
    },
    "agravo regimental criminal": {
        "area": "criminal",
        "dias": 5,
        "tipo_contagem": "corridos",
        "descricao": "Agravo Regimental Criminal",
        "fundamento": "Regimento interno do tribunal",
        "urgente": True,
    },
    "contrarrazões apelação criminal": {
        "area": "criminal",
        "dias": 8,
        "tipo_contagem": "corridos",
        "descricao": "Contrarrazões à Apelação Criminal (CPP art. 600)",
        "fundamento": "Art. 600 CPP",
        "urgente": True,
    },
    "revisão criminal": {
        "area": "criminal",
        "dias": 0,
        "tipo_contagem": "sem_prazo",
        "descricao": "Revisão Criminal — SEM PRAZO",
        "fundamento": "Art. 621 CPP — pode ser proposta a qualquer tempo",
        "urgente": False,
    },
}

# ─────────────────────────────────────────────────────────────────
# MAPEAMENTO: palavras-chave do DataJud → tipo de prazo
# ─────────────────────────────────────────────────────────────────

KEYWORDS_MOVIMENTO = {
    # ─────────────────────────────────────────
    # PUBLICACAO / DJE — termos reais DataJud
    # Publicacao no DJE normalmente abre prazo
    # ─────────────────────────────────────────
    "disponibilização no diário da justiça eletrônico": "intimação para manifestação",
    "publicação no diário": "intimação para manifestação",
    "intimação": "intimação para manifestação",
    "intimado": "intimação para manifestação",
    "intimação para": "intimação para manifestação",

    # ─────────────────────────────────────────
    # RECURSOS CÍVEIS
    # ─────────────────────────────────────────
    "apelação": "apelação",
    "apelante": "apelação",
    "apelar": "apelação",
    "agravo de instrumento": "agravo de instrumento",
    "agravo interno": "agravo interno",
    "agravo regimental": "agravo regimental",
    "embargos de declaração": "embargos de declaração",
    "não-acolhimento de embargos": "embargos de declaração",
    "recurso especial": "recurso especial",
    "recurso extraordinário": "recurso extraordinário",
    "contrarrazões": "contrarrazões de apelação",

    # ─────────────────────────────────────────
    # CITAÇÃO / CONTESTAÇÃO
    # ─────────────────────────────────────────
    "citado": "citação cível",
    "citação": "citação cível",
    "contestação": "citação cível",

    # ─────────────────────────────────────────
    # EXECUÇÃO / CUMPRIMENTO
    # ─────────────────────────────────────────
    "impugnação ao cumprimento": "impugnação ao cumprimento de sentença",
    "cumprimento de sentença": "cumprimento de sentença — pagamento",
    "penhora": "penhora realizada",
    "avaliação de bem": "avaliação de bem",
    "embargos à execução": "embargos à execução",
    "embargos de terceiro": "embargos de terceiro",
    "execução fiscal": "embargos à execução fiscal",

    # ─────────────────────────────────────────
    # MANIFESTAÇÕES GERAIS
    # ─────────────────────────────────────────
    "réplica": "réplica",
    "manifestação": "intimação para manifestação",
    "juntar": "intimação para juntar documentos",

    # ─────────────────────────────────────────
    # MANDADO — prazo para cumprimento
    # ─────────────────────────────────────────
    "mandado": "intimação para manifestação",
    "recebido mandado": "intimação para manifestação",

    # ─────────────────────────────────────────
    # TRABALHISTA
    # ─────────────────────────────────────────
    "recurso ordinário": "recurso ordinário trabalhista",
    "recurso de revista": "recurso de revista",
    "agravo de petição": "agravo de petição trabalhista",
    "embargos execução trabalhista": "embargos à execução trabalhista",
    "liquidação": "impugnação à sentença de liquidação",
    "48 horas": "execução trabalhista — pagamento",

    # ─────────────────────────────────────────
    # CRIMINAL — termos reais DataJud
    # ─────────────────────────────────────────
    "apelação criminal": "apelação criminal",
    "sentido estrito": "recurso em sentido estrito",
    "resposta à acusação": "resposta à acusação",
    "defesa prévia": "defesa prévia",
    "alegações finais": "alegações finais criminal",
    "memorial": "memorial criminal",
    "habeas corpus": "habeas corpus",
    "revisão criminal": "revisão criminal",
    "embargos de declaração criminal": "embargos de declaração criminal",
    "juntada de petição do mp": "resposta à acusação",
    "manutenção da prisão preventiva": "habeas corpus",
    "recebimento do termo de audiência": "alegações finais criminal",
}


def detectar_tipo_prazo(nome_movimento: str) -> Optional[str]:
    """
    Recebe o nome do movimento do DataJud e retorna a chave da tabela de prazos.
    """
    nome_lower = nome_movimento.lower()
    for keyword, tipo in KEYWORDS_MOVIMENTO.items():
        if keyword in nome_lower:
            return tipo
    return None


def calcular_prazo_final(data_publicacao: date, prazo_info: dict) -> Optional[date]:
    """
    Calcula a data final do prazo a partir da data de publicação.
    Regra CNJ: prazo começa no PRIMEIRO DIA ÚTIL seguinte à publicação.
    Usa _eh_util() com feriados nacionais fixos.
    """
    tipo = prazo_info.get("tipo_contagem", "uteis")

    if tipo in ("sem_prazo", "urgente"):
        return None

    if tipo == "horas":
        return data_publicacao + timedelta(hours=prazo_info["dias"])

    dias = prazo_info["dias"]
    # Prazo começa no primeiro dia útil APÓS a publicação
    data_inicio = _proximo_util(data_publicacao + timedelta(days=1))

    if tipo == "corridos":
        return data_inicio + timedelta(days=dias - 1)

    elif tipo == "uteis":
        return _somar_uteis(data_inicio, dias)

    return data_inicio + timedelta(days=dias)


def gerar_4_marcos(data_publicacao: date, data_prazo_final: date) -> list:
    """
    Divide o intervalo entre publicação e prazo final em 4 marcos iguais.
    Retorna lista de 5 itens: [publicação, 25%, 50%, 75%, final]
    """
    if not data_prazo_final:
        return []

    total_dias = (data_prazo_final - data_publicacao).days
    if total_dias <= 0:
        return [data_publicacao, data_prazo_final]

    marcos = []
    for i in range(5):
        frac = i / 4
        delta = int(total_dias * frac)
        marcos.append(data_publicacao + timedelta(days=delta))

    return marcos


def gerar_eventos_calendar(processo_info: dict, movimento: str, data_publicacao: date) -> list:
    """
    Recebe os dados do processo + movimento detectado.
    Retorna lista de dicts prontos para criar no Google Calendar.
    """
    tipo_prazo = detectar_tipo_prazo(movimento)
    if not tipo_prazo:
        return []

    prazo_info = TABELA_PRAZOS.get(tipo_prazo)
    if not prazo_info:
        return []

    data_final = calcular_prazo_final(data_publicacao, prazo_info)
    marcos = gerar_4_marcos(data_publicacao, data_final)

    if not marcos:
        return []

    numero = processo_info["numero"]
    cliente = processo_info["cliente"]
    tipo_processo = processo_info.get("tipo", "")
    area = prazo_info["area"].upper()
    urgente = prazo_info.get("urgente", False)

    descricao_base = prazo_info["descricao"]
    fundamento = prazo_info["fundamento"]
    dias = prazo_info["dias"]
    tipo_contagem = prazo_info["tipo_contagem"]

    eventos = []

    rotulos = [
        ("📌 PUBLICAÇÃO DETECTADA", "Início do prazo — publicação identificada pelo agente"),
        ("⏳ PRAZO 25%", f"Primeiro quarto do prazo — {dias} dias {tipo_contagem}"),
        ("⏳ PRAZO 50%", f"Metade do prazo — ação recomendada"),
        ("⚡ PRAZO 75%", f"Três quartos do prazo — iniciar redação urgente"),
        ("🚨 PRAZO FINAL", f"VENCIMENTO DO PRAZO — {descricao_base}"),
    ]

    for i, (marco_data, (rotulo, obs)) in enumerate(zip(marcos, rotulos)):
        is_final = (i == 4)

        titulo = f"{'⚠️ ' if urgente and is_final else ''}{rotulo} | {cliente} | {descricao_base}"

        corpo = (
            f"Processo: {numero}\n"
            f"Cliente: {cliente}\n"
            f"Tipo: {tipo_processo} ({area})\n"
            f"Movimento: {movimento}\n"
            f"Publicação: {data_publicacao.strftime('%d/%m/%Y')}\n"
            f"Prazo: {dias} dias {tipo_contagem}\n"
            f"Vencimento: {data_final.strftime('%d/%m/%Y') if data_final else 'Sem prazo'}\n"
            f"Fundamento: {fundamento}\n\n"
            f"Marco {i+1}/5: {obs}\n\n"
            f"Dr. Jefferson Silva de Brito | OAB/RO 2952\n"
            f"Agente De Brito Advocacia"
        )

        # Notificações: no dia (minutos antes)
        notificacoes = [480, 120, 30]  # 8h, 2h, 30min antes
        if is_final:
            notificacoes = [1440, 480, 120, 30]  # +24h antes para prazo final

        eventos.append({
            "titulo": titulo,
            "data": marco_data,
            "descricao": corpo,
            "cor": "11" if is_final else ("6" if i >= 3 else "2"),  # vermelho/amarelo/verde
            "notificacoes_minutos": notificacoes,
            "urgente": urgente,
            "is_prazo_final": is_final,
        })

    return eventos


# ─────────────────────────────────────────────────────────────────
# EXPORTAR PARA USO NO AGENTE PRINCIPAL
# ─────────────────────────────────────────────────────────────────

__all__ = [
    "TABELA_PRAZOS",
    "KEYWORDS_MOVIMENTO",
    "detectar_tipo_prazo",
    "calcular_prazo_final",
    "gerar_4_marcos",
    "gerar_eventos_calendar",
]


if __name__ == "__main__":
    # TESTE LOCAL
    from datetime import date

    processo_teste = {
        "numero": "0001234-56.2024.8.22.0001",
        "cliente": "Charles Novais de Almeida",
        "tipo": "Civil — Caminhão",
        "tribunal": "TJRO"
    }

    movimento_teste = "Intimado para apresentar contrarrazões de apelação"
    data_pub = date.today()

    eventos = gerar_eventos_calendar(processo_teste, movimento_teste, data_pub)

    print(f"\n{'='*60}")
    print(f"PROCESSO: {processo_teste['numero']}")
    print(f"MOVIMENTO: {movimento_teste}")
    print(f"{'='*60}")
    for ev in eventos:
        print(f"\n📅 {ev['data'].strftime('%d/%m/%Y')} — {ev['titulo'][:60]}")
    print(f"\n✅ {len(eventos)} eventos gerados para o Google Calendar")
