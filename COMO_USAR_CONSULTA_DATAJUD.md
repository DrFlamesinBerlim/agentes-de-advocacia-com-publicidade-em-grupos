# 📋 COMO USAR — Consulta DataJud API

## O Script

**Arquivo**: `consultar_processos_datajud.py`

**O que faz**:
- Consulta os processos T002 e T007 via API pública do CNJ
- Retorna: última movimentação, status, andamento
- Salva resultado em JSON (`CONSULTA_PROCESSOS_RESULTADO.json`)

---

## 🔑 PASSO 1: Obter Chave DataJud API

1. Acesse: https://www.cnj.jus.br/sistemas/datajud/api-publica/
2. Solicite uma chave pública (gratuito)
3. Aguarde aprovação (24-48h, às vezes instantâneo)
4. Você receberá uma chave como: `abc123xyz-def456uvw-ghi789rst`

---

## 💻 PASSO 2: Executar o Script

### No seu computador (Linux/Mac/Windows):

```bash
# 1. Instalar dependências
pip install requests

# 2. Executar com sua chave
python3 consultar_processos_datajud.py "SEU_CHAVE_AQUI"

# Exemplo:
python3 consultar_processos_datajud.py "abc123xyz-def456uvw-ghi789rst"
```

### Resultado esperado:

```
============================================================
🔍 CONSULTA DE PROCESSOS - De Brito Advocacia
   Via DataJud API (CNJ)
============================================================

📋 T002 — PROTOCOLAR PETIÇÃO RESCISÓRIA
   Cliente: Alexandre Marques de Campos
   Processo: 0611311-40.2023.8.04.4400
  📡 Consultando: 0611311-40.2023.8.04.4400 no tjam...
   ✅ Status: [ANDAMENTO]
   📅 Última mov: 2026-07-22
   📝 Descrição: [DESCRIÇÃO DA MOVIMENTAÇÃO]

📋 T007 — CHECAR ACOMPANHAMENTO MANDADO PRISÃO
   Cliente: Leandro Pereira Cardoso
   Processo: 7026053-67.2024.8.22.0001
  📡 Consultando: 7026053-67.2024.8.22.0001 no tjro...
   ✅ Status: [ANDAMENTO]
   📅 Última mov: 2026-05-23
   📝 Descrição: [DESCRIÇÃO DA MOVIMENTAÇÃO]

============================================================
📊 Gerando Relatório...
✅ Relatório salvo em: /root/MABIOS/import/CONSULTA_PROCESSOS_RESULTADO.json

📋 RESULTADO (JSON)
============================================================
{
  "timestamp": "2026-07-23T15:30:00Z",
  "sistema": "De Brito Advocacia - Consulta DataJud API",
  "processos": {
    "T002": {
      "numero": "0611311-40.2023.8.04.4400",
      "cliente": "Alexandre Marques de Campos",
      "descricao": "PROTOCOLAR PETIÇÃO RESCISÓRIA",
      "tribunal": "tjam",
      "movimentacao": {...}
    },
    "T007": {
      "numero": "7026053-67.2024.8.22.0001",
      "cliente": "Leandro Pereira Cardoso",
      "descricao": "CHECAR ACOMPANHAMENTO MANDADO PRISÃO",
      "tribunal": "tjro",
      "movimentacao": {...}
    }
  }
}

============================================================
✅ CONSULTA CONCLUÍDA
============================================================
```

---

## 📊 Arquivo de Resultado

O script salva em: `/root/MABIOS/import/CONSULTA_PROCESSOS_RESULTADO.json`

**Conteúdo**: JSON com dados completos dos processos (movimentações, andamento, etc.)

---

## ❓ Troubleshooting

| Problema | Solução |
|----------|---------|
| `Chave API inválida` | Verifique a chave (copiar exatamente como recebeu) |
| `Processo não encontrado` | Número pode estar incorreto ou processo não tem dados públicos |
| `Timeout na consulta` | Tente novamente (problema de conexão) |
| `HTTP 403` | Você está atrás de proxy? Proxy está bloqueando CNJ |

---

## ✅ Próximas Ações Após Consulta

Após executar o script e obter os resultados:

1. **Para T002**: Se petição não está protocolarizada → PROTOCOLAR HOJE
2. **Para T007**: Verificar status do mandado → COMUNICAR AO CLIENTE
3. **Enviar resultados para Claude** → Estruturar plano de ação

---

## 📞 Suporte

Se tiver problemas:
1. Verifique se tem acesso à internet (Python pode acessar a API)
2. Confirme que a chave DataJud está correta
3. Teste em outro computador se possível

---

**Script pronto em**: `consultar_processos_datajud.py`  
**Instruções**: Este arquivo  
**Próximo passo**: Obter chave DataJud → Executar script → Trazer resultado
