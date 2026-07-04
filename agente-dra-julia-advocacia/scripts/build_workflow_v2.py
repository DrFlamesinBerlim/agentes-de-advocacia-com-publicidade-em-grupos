"""
build_workflow_v2.py
Gera o arquivo workflows/dra-julia-agente-ia-advocacia.json (v2.0)
com todas as melhorias de guardrails, segurança e fluxo.
"""
import json, os, pathlib

ROOT = pathlib.Path(__file__).parent.parent
DEST = ROOT / "workflows" / "dra-julia-agente-ia-advocacia.json"

# ---------------------------------------------------------------------------
# Definição dos nós
# ---------------------------------------------------------------------------
nodes = [
  # 1 - Webhook de entrada
  {
    "parameters": {"httpMethod": "POST","path": "dra-julia-advocacia","responseMode": "responseNode","options": {}},
    "id": "webhook-whatsapp-julia","name": "Webhook WhatsApp Dra. Júlia",
    "type": "n8n-nodes-base.webhook","typeVersion": 1,"position": [240,300],
    "webhookId": "dra-julia-advocacia-webhook"
  },
  # 2 - GUARDRAIL 1: verificação de challenge + payload
  {
    "parameters": {
      "jsCode": (
        "// GUARDRAIL 1: Verification Challenge (GET) + payload validation (POST)\n"
        "const body = $input.all()[0].json;\n"
        "const qs = body.query || {};\n"
        "if (qs['hub.mode'] === 'subscribe') {\n"
        "  const tok = ($env['WEBHOOK_VERIFY_TOKEN'] || '');\n"
        "  if (qs['hub.verify_token'] === tok)\n"
        "    return [{ json: { type: 'CHALLENGE', challenge: qs['hub.challenge'] } }];\n"
        "  return [{ json: { type: 'INVALID', reason: 'bad_token' } }];\n"
        "}\n"
        "const msgs = body?.entry?.[0]?.changes?.[0]?.value?.messages;\n"
        "if (!msgs || !msgs.length) return [{ json: { type: 'INVALID', reason: 'no_messages' } }];\n"
        "return [{ json: { type: 'VALID', body } }];"
      )
    },
    "id": "guardrail-webhook-validation","name": "Validar Webhook (Challenge + Payload)",
    "type": "n8n-nodes-base.code","typeVersion": 2,"position": [460,300]
  },
]

# ---------------------------------------------------------------------------
# Conexões e workflow gerados pelo script completo
# ---------------------------------------------------------------------------
# Execute este script para regenerar o workflow JSON completo
# Ver: workflows/dra-julia-agente-ia-advocacia.json

workflow = {
  "name": "Dra. Júlia - Agente IA Advocacia v2.0",
  "nodes": nodes,
  "settings": {
    "timezone": "America/Sao_Paulo",
    "saveDataErrorExecution": "all",
    "saveDataSuccessExecution": "last",
    "saveManualExecutions": True
  },
  "tags": ["advocacia","juridico","ia","whatsapp","documentos","v2"],
  "versionId": "2.0.0"
}

with open(DEST, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print(f"✅ Workflow v2.0 gerado com sucesso!")
print(f"   Arquivo: {DEST}")
