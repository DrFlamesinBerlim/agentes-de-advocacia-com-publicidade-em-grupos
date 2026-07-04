# /whatsapp — Processar e indexar exportações WhatsApp com transcrições

**Uso:** `/whatsapp [comando] [argumentos]`

**Status:** v1.0 — CONGELADO (template + parser + skill não se alteram)

---

## VISÃO GERAL

Processa exportações de chats WhatsApp (TXT, JSON) e:
1. Valida contra template genérico
2. Extrai mensagens, participantes, áudios
3. Indexa processos/partes mencionadas
4. Gera prova processual formatada para judicial

**Template:** Congelado — todas as exportações se adaptam a ele, nunca o contrário.

---

## COMANDOS

### `/whatsapp processar CAMINHO ORIGEM [DESCRICAO] [TIPO]`

Processa um arquivo de exportação WhatsApp.

**Argumentos:**
- `CAMINHO` — caminho completo do arquivo (TXT ou JSON)
- `ORIGEM` — identificador único (ex: "keyla_usa", "auzier_grupo")
- `DESCRICAO` (opcional) — breve descrição (ex: "Chat com cliente EUA")
- `TIPO` (opcional) — "individual" ou "grupo" (padrão: "grupo")

**Exemplo:**
```
/whatsapp processar "C:\Users\advog\Meu Drive\X\downloads AI\keyla_chat.txt" keyla_usa "Chat cliente nos EUA" individual
```

**O que faz:**
1. Lê arquivo TXT/JSON
2. Extrai:
   - Participantes e nomes únicos
   - Mensagens com timestamp, remetente, corpo
   - Transcrições (se existem em campo separado)
   - Documentos anexados
3. Indexa:
   - Processos mencionados (padrão NNNNNNN-DD.AAAA.J.TR.OOOO)
   - Referências a documentos jurídicos (contrato, petição, sentença, etc.)
   - Partes envolvidas (nome/papel/datas)
4. Preenche template genérico com dados reais
5. Salva:
   - `{origem}_processado.json` — estrutura completa
   - `{origem}_PROVA_PROCESSUAL.txt` — formatado para judicial

**Resultado esperado:**
```
[WHATSAPP PARSER] Processando: C:\Users\advog\...\keyla_chat.txt
  Origem: keyla_usa
  Tipo: individual
  ✅ JSON salvo: C:\...\keyla_usa_processado.json
  ✅ Prova processual: C:\...\keyla_usa_PROVA_PROCESSUAL.txt
  
  📊 Resumo:
     • 247 mensagens extraídas
     • 8 participantes identificados
     • 3 processos mencionados
     • 5 documentos jurídicos referenciados
     • Hash arquivo: ab3d4e5f... (para integridade)
```

---

### `/whatsapp listar-processados`

Lista todas as exportações já processadas.

```
/whatsapp listar-processados
```

**Resultado:**
```
EXPORTAÇÕES PROCESSADAS:

1. keyla_usa (processado em 2026-07-04)
   → 247 mensagens | 8 participantes
   → Processos: 7054209-31.2025.8.22.0001, 0800556-72.2026.8.22.0000
   → Prova: keyla_usa_PROVA_PROCESSUAL.txt

2. auzier_grupo (processado em 2026-06-28)
   → 1,253 mensagens | 15 participantes
   → Processos: 7057519-45.2025.8.22.0001
   → Prova: auzier_grupo_PROVA_PROCESSUAL.txt
```

---

### `/whatsapp buscar-processos`

Busca todos os processos mencionados em exportações.

```
/whatsapp buscar-processos 7054209
```

**Resultado:**
```
MENÇÕES DO PROCESSO 7054209-31.2025.8.22.0001:

🔍 Encontrado em: keyla_usa

  [2026-06-25 14:30] Keyla Pereira:
    "Enviei documento do processo 7054209-31.2025.8.22.0001 para análise"

  [2026-06-26 09:15] Keyla Pereira:
    "Preciso de parecer sobre a sentença do 7054209 até sexta"

  📋 Total: 2 menções
```

---

### `/whatsapp buscar-prova ORIGEM`

Exibe prova processual gerada (primeira/última páginas).

```
/whatsapp buscar-prova keyla_usa
```

**Resultado:**
```
PROVA PROCESSUAL — keyla_usa

PERÍODO: 2026-06-15 a 2026-07-04
TIPO DE CHAT: individual
TOTAL DE MENSAGENS: 247
PARTICIPANTES: 8

PARTICIPANTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Keyla Pereira
• Dr. Jefferson Silva de Brito
• [... 6 outros]

MENSAGENS (primeiras 50 de 247)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[2026-06-15 10:30] Keyla Pereira:
  Bom dia Dr. Jefferson, tudo bem? Preciso de ajuda no processo 7054209

[2026-06-15 10:45] Dr. Jefferson Silva de Brito:
  Oi Keyla, tudo bem sim. Qual é a questão?

... (197 mensagens) ...

[2026-07-04 16:20] Keyla Pereira:
  Obrigada pela orientação Dr. Jefferson!
```

---

### `/whatsapp vincular-tarefas ORIGEM PROCESSO`

Vincula exportação processada a tarefa ou processo.

```
/whatsapp vincular-tarefas keyla_usa 7054209-31.2025.8.22.0001
```

**O que faz:**
1. Localiza `keyla_usa_processado.json`
2. Busca processo 7054209... em `processos.json`
3. Registra origem de dados: "WhatsApp — keyla_usa"
4. Atualiza `processos.json` com link para prova

**Resultado:**
```
✅ Exportação keyla_usa vinculada ao processo 7054209-31.2025.8.22.0001
   Prova processual será incluída em relatórios do processo
```

---

## ESTRUTURA DO ARQUIVO PROCESSADO

Cada exportação processada é um JSON seguindo **template congelado** (`whatsapp_export_template.json`):

```json
{
  "exportacao": {
    "origem": {
      "tipo": "whatsapp_export",
      "fonte": "keyla_usa",
      "descricao": "Chat cliente nos EUA"
    },
    "metadados": {
      "data_exportacao": "2026-07-04T14:35:00+00:00",
      "periodo_inicio": "2026-06-15",
      "periodo_fim": "2026-07-04",
      "tipo_chat": "individual",
      "total_mensagens": 247,
      "total_participantes": 8
    }
  },
  "participantes": [
    {
      "id": "p_000",
      "nome": "Keyla Pereira",
      "eh_cliente": true,
      "eh_adversario": false
    }
  ],
  "mensagens": {
    "total": 247,
    "dados": [
      {
        "id": "msg_000001",
        "timestamp": "2026-06-15T10:30:00",
        "remetente": "Keyla Pereira",
        "tipo_conteudo": "texto",
        "corpo_texto": "Bom dia Dr. Jefferson..."
      }
    ]
  },
  "indice_processual": {
    "processos_mencionados": [
      {
        "numero": "7054209-31.2025.8.22.0001",
        "mencionado_por": ["Keyla Pereira"],
        "datas_mencao": ["2026-06-15T10:30:00"]
      }
    ]
  },
  "prova_processual": {
    "gerada": true,
    "conteudo": "Texto formatado para judicial..."
  }
}
```

**Sempre neste formato — nunca muda.**

---

## INTEGRAÇÃO COM SISTEMA

### Loop automático (30 minutos)

`loop_monitor.py` executa a cada **30 min**:
```python
# Em agente_andamentos/modulo_whatsapp_monitor.py
def checar_novos_exports():
    # Monitora documentos/whatsapp/inbox/
    # Se encontra novo arquivo → chama /whatsapp processar automaticamente
```

---

### Vinculação com processos

Quando `/whatsapp vincular-tarefas` é executado:
```
1. Localiza JSON processado
2. Busca processo em processos.json
3. Adiciona campo:
   "prova_whatsapp": {
     "origem": "keyla_usa",
     "data_processamento": "2026-07-04",
     "caminho": "documentos/whatsapp/processados/keyla_usa_PROVA_PROCESSUAL.txt"
   }
4. Atualiza processos.json
```

Depois em `/relatorio 7054209` aparece:
```
PROVA ANEXA:
  📎 WhatsApp keyla_usa — 247 mensagens
     Prova processual: keyla_usa_PROVA_PROCESSUAL.txt
```

---

## REGRAS OURO

1. **Template é CONGELADO** — nunca alterar `whatsapp_export_template.json`
2. **Todas as exportações se adaptam ao template** — não o contrário
3. **Parser genérico** — funciona com qualquer fonte (TXT, JSON, CSV com dados reais)
4. **Sem alucinação** — só extrai o que existe em um padrão claro (regex para datas, nomes, números)
5. **Hash de integridade** — verifica arquivo não foi alterado
6. **Prova processual** — formatada para tribunal, não varia

---

## CICLO DE VIDA

```
1. Encontrar exportação com transcrições
   ↓
2. /whatsapp processar <arquivo> <origem> <descricao> <tipo>
   ↓
3. JSON + Prova gerados automaticamente
   ↓
4. /whatsapp vincular-tarefas <origem> <processo>
   ↓
5. Aparece em /relatorio <processo> como prova anexa
   ↓
6. Enviável ao tribunal como evidência
```

---

## FAQ

**P: Posso alterar o template?**  
R: Não. É CONGELADO. Se precisa de novo campo, descongela em FROZEN.md com autorização explícita do Dr. Jefferson.

**P: E se o arquivo TXT tem formato diferente?**  
R: Modulo_whatsapp_parser.py tenta múltiplos padrões regex (DD/MM/YYYY, YYYY-MM-DD, etc.). Se falhar → registra erro em `processamento_sistema.erros_identificados`.

**P: Posso rodar `/whatsapp processar` no loop automaticamente?**  
R: Sim! Modulo_whatsapp_monitor.py monitora `documentos/whatsapp/inbox/` e chama automaticamente.

**P: Como indexa processos mencionados?**  
R: Busca padrão NNNNNNN-DD.AAAA.J.TR.OOOO no corpo de cada mensagem. Não precisa de AI — é regex puro (zero alucinação).

---

**Skill CONGELADA v1.0 — não altera sem descongelar!** 🧊

