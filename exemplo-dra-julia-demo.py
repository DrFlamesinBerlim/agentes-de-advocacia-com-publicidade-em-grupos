#!/usr/bin/env python3
"""
EXEMPLO: Como a Dra. Julia funciona
Simula o fluxo completo de uma consulta WhatsApp → Processamento → Resposta
"""

import json
from datetime import datetime
from typing import Dict, List

# ============================================================================
# PASSO 1: WEBHOOK WHATSAPP RECEBE MENSAGEM
# ============================================================================

class MessageFromWhatsApp:
    """Simula mensagem recebida via WhatsApp Business API"""

    def __init__(self):
        self.webhook_payload = {
            "messaging_product": "whatsapp",
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "5564992217123",
                            "type": "text",
                            "text": {
                                "body": "Oi Dra Julia, tive um acidente de carro. O outro motorista quer me obrigar a pagar tudo mas não foi culpa minha. O que faço?"
                            }
                        }]
                    }
                }]
            }]
        }

print("=" * 80)
print("📱 PASSO 1: WEBHOOK WHATSAPP")
print("=" * 80)

msg = MessageFromWhatsApp()
client_phone = msg.webhook_payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
client_message = msg.webhook_payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

print(f"✅ Mensagem recebida do cliente: {client_phone}")
print(f"📝 Conteúdo: '{client_message}'")
print()


# ============================================================================
# PASSO 2: N8N WEBHOOK GUARDRAILS (Validação de Segurança)
# ============================================================================

class N8NGuardrails:
    """Simula os 2 nós iniciais do workflow N8N da Dra. Julia"""

    @staticmethod
    def validate_webhook(payload: dict) -> bool:
        """Valida challenge do webhook para evitar replay attacks"""
        # Verificação de token
        webhook_verify_token = "token_secreto_n8n_dra_julia"

        if payload.get("hub.verify_token") == webhook_verify_token:
            print("✅ Webhook válido (token verificado)")
            return True
        print("❌ Webhook inválido")
        return False

    @staticmethod
    def check_rate_limit(phone: str, limit: int = 5) -> bool:
        """Verifica se cliente ultrapassou limite de mensagens/min"""
        # Em produção: consulta Redis ou banco de dados
        print(f"✅ Rate limit OK (cliente {phone} tem {limit} slots disponíveis)")
        return True

print("=" * 80)
print("🔒 PASSO 2: VALIDAÇÃO N8N (Guardrails)")
print("=" * 80)

guardrails = N8NGuardrails()
guardrails.validate_webhook({"hub.verify_token": "token_secreto_n8n_dra_julia"})
guardrails.check_rate_limit(client_phone)
print()


# ============================================================================
# PASSO 3: ANÁLISE COM GPT-4o (Classificação + Extração)
# ============================================================================

class GPT4oAnalyzer:
    """Simula chamada a GPT-4o para triagem e análise"""

    def triagem(self, message: str) -> Dict:
        """Classifica mensagem em categoria jurídica"""
        # Em produção: chama OpenAI API
        return {
            "categoria": "responsabilidade_civil",
            "subcategoria": "acidente_trânsito",
            "urgência": "média",
            "confidence": 0.95,
            "palavras_chave": ["acidente", "motorista", "culpa", "obrigação_pagar"],
            "recomendação": "Agendar consulta detalhada (colher depoimento, fotos cena, boletim BO)"
        }

    def gerar_resposta_inicial(self, triagem: Dict, message: str) -> str:
        """Gera resposta automática educacional"""
        # Em produção: chama GPT-4o com prompt customizado
        return f"""Olá! 👋

Obrigado por procurar a Dra. Julia. Identifiquei sua situação como:
📋 Categoria: {triagem['categoria'].replace('_', ' ').title()}

**Informações iniciais importantes:**

1️⃣ **Você pode estar protegido** — Em acidentes de trânsito, a culpa deve ser provada. Testemunhas, câmeras, boletim de ocorrência (BO) são essenciais.

2️⃣ **Não aceite culpa facilmente** — Documentar tudo agora (fotos do carro, local, placas, contatos de testemunhas).

3️⃣ **Próximos passos recomendados:**
   • Tirar fotos do local e danos
   • Fazer Boletim de Ocorrência se houver danos
   • Guardar documentos do outro motorista (RG, CNH, placa)
   • Não assinar nada sem orientação jurídica

⏰ **Para uma análise completa**, gostaria de agendar uma consulta detalhada.

Responda: "Sim, quero agendar" ou "Preciso de mais informações"
"""

print("=" * 80)
print("🤖 PASSO 3: ANÁLISE COM GPT-4o")
print("=" * 80)

analyzer = GPT4oAnalyzer()
triagem = analyzer.triagem(client_message)

print(f"📊 Triagem:")
print(f"   Categoria: {triagem['categoria'].replace('_', ' ').title()}")
print(f"   Urgência: {triagem['urgência']}")
print(f"   Confiança: {triagem['confidence']*100}%")
print()

resposta = analyzer.gerar_resposta_inicial(triagem, client_message)
print("🤖 Resposta Gerada:")
print("-" * 80)
print(resposta)
print("-" * 80)
print()


# ============================================================================
# PASSO 4: AGENDAMENTO EM GOOGLE SHEETS + CALENDAR
# ============================================================================

class GoogleSheetSync:
    """Simula integração com Google Sheets e Calendar"""

    def criar_registro_consulta(self, phone: str, triagem: Dict, message: str) -> Dict:
        """Cria linha em Clientes_Dra_Julia no Google Sheets"""
        consulta = {
            "id_cliente": f"CLI_{phone[-4:]}",
            "telefone": phone,
            "data_primeiro_contato": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "categoria": triagem["categoria"],
            "urgência": triagem["urgência"],
            "resumo_problema": message[:100] + "...",
            "status": "novo",
            "url_sheets": "https://docs.google.com/spreadsheets/d/1nXxxx/edit#gid=0"
        }
        return consulta

    def agendar_consulta(self, phone: str, categoria: str) -> Dict:
        """Cria evento no Google Calendar + slot livre"""
        return {
            "data_sugerida": "2026-07-07 14:00",
            "duracao_minutos": 30,
            "link_meet": "https://meet.google.com/abc-defg-hij",
            "evento_id": "evt_drjulia_2026_07_07_1400",
            "confirmado": False,
            "link_agendamento": "https://calendly.com/dra-julia/consulta-remota"
        }

print("=" * 80)
print("📊 PASSO 4: REGISTRO EM GOOGLE SHEETS + CALENDAR")
print("=" * 80)

sheets = GoogleSheetSync()
consulta_db = sheets.criar_registro_consulta(client_phone, triagem, client_message)

print("📋 Registro criado em Clientes_Dra_Julia:")
for key, value in consulta_db.items():
    print(f"   {key}: {value}")
print()

agendamento = sheets.agendar_consulta(client_phone, triagem["categoria"])
print("📅 Slot de Consulta Sugerido:")
for key, value in agendamento.items():
    print(f"   {key}: {value}")
print()


# ============================================================================
# PASSO 5: ENVIO DE RESPOSTA WHATSAPP (COM BOTÕES INTERATIVOS)
# ============================================================================

class WhatsAppResponse:
    """Simula envio de resposta via Evolution API / Baileys"""

    def enviar_mensagem(self, to_phone: str, text: str, buttons: List[str] = None):
        """Envia mensagem de texto com botões interativos"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {
                "body": text
            }
        }

        if buttons:
            payload["interactive"] = {
                "type": "button",
                "body": {"text": "Escolha uma opção:"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "btn_1", "title": btn}}
                        for btn in buttons
                    ]
                }
            }

        return payload

print("=" * 80)
print("💬 PASSO 5: ENVIO WHATSAPP")
print("=" * 80)

whatsapp = WhatsAppResponse()
payload = whatsapp.enviar_mensagem(
    to_phone=client_phone,
    text=resposta,
    buttons=["Agendar Consulta", "Mais Informações", "Falar com Atendente"]
)

print(f"✅ Mensagem enviada para {client_phone}")
print(f"📨 Payload:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print()


# ============================================================================
# PASSO 6: MONITORAMENTO (Se cliente responde "Agendar")
# ============================================================================

class ConsultaWorkflow:
    """Simula fluxo após cliente responder positivamente"""

    def processar_resposta_usuario(self, resposta_botao: str) -> Dict:
        """Processa qual botão foi clicado"""

        if resposta_botao == "Agendar Consulta":
            return {
                "ação": "enviar_link_agendamento",
                "link": "https://calendly.com/dra-julia/consulta-remota",
                "próximo_passo": "confirmar_agendamento"
            }
        elif resposta_botao == "Mais Informações":
            return {
                "ação": "enviar_material_educativo",
                "materiais": [
                    "responsabilidade_civil_acidente.pdf",
                    "boletim_ocorrencia_guia.pdf"
                ],
                "próximo_passo": "aguardar_resposta"
            }
        else:  # "Falar com Atendente"
            return {
                "ação": "escalar_para_humano",
                "atendente": "maria.silva@dra-julia.com.br",
                "próximo_passo": "suporte_humano"
            }

print("=" * 80)
print("🔄 PASSO 6: MONITORAMENTO (Cliente Clica em Botão)")
print("=" * 80)

workflow = ConsultaWorkflow()

# Simular 3 possíveis respostas
for resposta_user in ["Agendar Consulta", "Mais Informações", "Falar com Atendente"]:
    resultado = workflow.processar_resposta_usuario(resposta_user)
    print(f"\n📌 Cliente clicou: '{resposta_user}'")
    print(f"   → Ação: {resultado['ação']}")
    print(f"   → Próximo: {resultado['próximo_passo']}")
    if "link" in resultado:
        print(f"   → Link: {resultado['link']}")
    if "materiais" in resultado:
        print(f"   → Materiais: {', '.join(resultado['materiais'])}")

print()


# ============================================================================
# FLUXO COMPLETO (RESUMO)
# ============================================================================

print("=" * 80)
print("📊 FLUXO COMPLETO RESUMIDO")
print("=" * 80)

fluxo = f"""
1️⃣  WEBHOOK WHATSAPP recebe: "{client_message}"

2️⃣  N8N GUARDRAILS validam token e rate-limit ✅

3️⃣  GPT-4o ANALISA:
    • Categoria: {triagem['categoria'].replace('_', ' ').title()}
    • Urgência: {triagem['urgência']}
    • Resposta gerada em ~2 segundos

4️⃣  GOOGLE SHEETS registra cliente:
    • Clientes_Dra_Julia: nova linha criada
    • ID: {consulta_db['id_cliente']}

5️⃣  GOOGLE CALENDAR sugere slot:
    • Data: {agendamento['data_sugerida']}
    • Link: {agendamento['link_meet']}

6️⃣  WHATSAPP envia resposta + botões (via Evolution API)
    • Tempo total: ~3-5 segundos

7️⃣  MONITORAMENTO: aguarda clique em botão
    ├─ "Agendar Consulta" → Enviar link Calendly
    ├─ "Mais Informações" → Enviar PDFs educativos
    └─ "Falar com Atendente" → Escalar para humano

📈 RESULTADO:
   • Cliente tem resposta imediata (não aguarda humano)
   • Dra. Julia tem informações estruturadas (triagem feita)
   • Sistema está pronto para agendamento automático
   • Fallback para atendente humano se necessário
"""

print(fluxo)

print("=" * 80)
print("🎯 PRÓXIMAS MELHORIAS (Para 'Publicidade em Grupos')")
print("=" * 80)

melhorias = """
Ao invés de responder 1 cliente, enviar MÚLTIPLAS POSTAGENS em grupos:

✅ Batches diários de conteúdo:
   • 09:00 — Jurisprudência semanal (3 decisões relevantes)
   • 14:30 — Dica legal (tópico: responsabilidade civil, direito do trabalho, etc.)
   • 18:00 — Case de sucesso (cliente autorizado anônimo)

✅ Sem responder individualmente, mas com:
   • Reações rastreadas (👍❤️😂)
   • Shares contados
   • Links clicados monitorados
   • Grupos onde conteúdo performou melhor

✅ Integrado com:
   • Canva (gerar imagens automáticas)
   • monday.com (controlar calendário de postagens)
   • Google Sheets (rastrear analytics)
"""

print(melhorias)

print("\n" + "=" * 80)
print("✅ FIM DA SIMULAÇÃO")
print("=" * 80)
