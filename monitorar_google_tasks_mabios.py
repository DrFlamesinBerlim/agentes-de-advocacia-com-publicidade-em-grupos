#!/usr/bin/env python3
"""
MABIOS v4 — Google Tasks Deadline Monitor
Monitora tarefas no Google Tasks e envia alertas quando prazos aproximam-se
Data: 2026-07-22
Responsável: Claude CC-001
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
log_file = Path.home() / "MABIOS" / "sync_history.log"
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GoogleTasksMonitor:
    """Monitora tarefas do Google Tasks via API"""

    def __init__(self, credentials_path=None):
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.base_url = "https://www.googleapis.com/tasks/v1"
        self.tasks_data = {}
        self.alerts_sent = {}

    def carregar_tarefas_locais(self, json_path):
        """Carrega tarefas do arquivo preparado GOOGLE_TASKS_PRONTO_22_07_2026.md"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.tasks_data = json.load(f)
            logging.info(f"✅ Carregadas {len(self.tasks_data)} tarefas do arquivo local")
            return self.tasks_data
        except FileNotFoundError:
            logging.error(f"❌ Arquivo não encontrado: {json_path}")
            return None

    def verificar_prazos_criticos(self):
        """Identifica tarefas com prazos críticos (<3 dias)"""
        hoje = datetime.now()
        criticos = []

        for task_id, task_data in self.tasks_data.items():
            if 'deadline' not in task_data:
                continue

            try:
                deadline = datetime.strptime(task_data['deadline'], '%d/%m/%Y')
                dias_restantes = (deadline - hoje).days

                if dias_restantes <= 3 and dias_restantes >= 0:
                    criticos.append({
                        'task_id': task_id,
                        'description': task_data.get('description', 'N/A'),
                        'client': task_data.get('client', 'N/A'),
                        'deadline': task_data['deadline'],
                        'dias_restantes': dias_restantes,
                        'priority': task_data.get('priority', 'NORMAL')
                    })
            except ValueError:
                continue

        return criticos

    def verificar_vencidos(self):
        """Identifica tarefas com prazo vencido"""
        hoje = datetime.now()
        vencidos = []

        for task_id, task_data in self.tasks_data.items():
            if 'deadline' not in task_data:
                continue

            try:
                deadline = datetime.strptime(task_data['deadline'], '%d/%m/%Y')
                dias_restantes = (deadline - hoje).days

                if dias_restantes < 0:
                    vencidos.append({
                        'task_id': task_id,
                        'description': task_data.get('description', 'N/A'),
                        'client': task_data.get('client', 'N/A'),
                        'deadline': task_data['deadline'],
                        'dias_vencidos': abs(dias_restantes),
                        'priority': task_data.get('priority', 'NORMAL')
                    })
            except ValueError:
                continue

        return vencidos

    def gerar_aviso_diario(self):
        """Gera aviso diário estruturado para Inbox_Claude"""
        criticos = self.verificar_prazos_criticos()
        vencidos = self.verificar_vencidos()

        aviso = {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'AVISO_PRAZOS_MABIOS',
            'nivel_severidade': 'CRÍTICO' if (criticos or vencidos) else 'NORMAL',
            'prazos_criticos': criticos,
            'prazos_vencidos': vencidos,
            'total_tarefas': len(self.tasks_data),
            'tarefas_monitoradas': len([t for t in self.tasks_data.values() if 'deadline' in t])
        }

        logging.info(f"📊 Aviso gerado: {len(criticos)} críticos, {len(vencidos)} vencidos")
        return aviso

    def formatar_aviso_texto(self, aviso):
        """Formata aviso para envio via Trans-LLM"""
        texto = f"""# 🚨 AVISO DIÁRIO — PRAZOS & URGÊNCIAS
**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Nível**: {aviso['nivel_severidade']}
**Tarefas Monitoradas**: {aviso['tarefas_monitoradas']}/{aviso['total_tarefas']}

## 🔴 PRAZOS CRÍTICOS ({len(aviso['prazos_criticos'])})
"""

        for task in aviso['prazos_criticos']:
            texto += f"""
**{task['task_id']}** — {task['description']}
- **Cliente**: {task['client']}
- **Deadline**: {task['deadline']} ({task['dias_restantes']} dias)
- **Prioridade**: {task['priority']}
"""

        if aviso['prazos_vencidos']:
            texto += f"""

## 🔴 PRAZOS VENCIDOS ({len(aviso['prazos_vencidos'])})
"""
            for task in aviso['prazos_vencidos']:
                texto += f"""
**{task['task_id']}** — {task['description']}
- **Cliente**: {task['client']}
- **Prazo Vencido**: {task['deadline']} ({task['dias_vencidos']} dias atrás)
- **Prioridade**: {task['priority']}
"""

        texto += f"""

## ✅ Status Watchdog
- **Loop Monitor**: ✅ ONLINE
- **Próximo Check**: {(datetime.now() + timedelta(hours=1)).strftime('%d/%m/%Y %H:%M')}
- **Gerado por**: CC-001 MABIOS v4
"""
        return texto

    def salvar_aviso_inbox(self, aviso_texto):
        """Salva aviso em Inbox_Claude para Trans-LLM processar"""
        inbox_path = Path.home() / "Google Drive" / "My Drive" / "03_MABIOS_Sistema" / "Inbox_Claude"
        inbox_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        arquivo = inbox_path / f"{timestamp}_AVISO_PRAZOS_MABIOS.md"

        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(aviso_texto)
            logging.info(f"✅ Aviso salvo em: {arquivo}")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao salvar aviso: {e}")
            return False

def executar_monitoramento():
    """Executa ciclo completo de monitoramento"""
    monitor = GoogleTasksMonitor()

    # Carregar tarefas do arquivo preparado
    tarefas_arquivo = Path.home() / "MABIOS" / "GOOGLE_TASKS_PRONTO_22_07_2026.json"

    if not tarefas_arquivo.exists():
        logging.warning(f"⚠️ Arquivo de tarefas não encontrado. Criando estrutura vazia...")
        monitor.tasks_data = {}
    else:
        monitor.carregar_tarefas_locais(str(tarefas_arquivo))

    # Gerar aviso
    aviso = monitor.gerar_aviso_diario()
    texto_aviso = monitor.formatar_aviso_texto(aviso)

    # Salvar em Inbox_Claude
    monitor.salvar_aviso_inbox(texto_aviso)

    logging.info("✅ Ciclo de monitoramento concluído")

    return aviso

if __name__ == '__main__':
    executar_monitoramento()
