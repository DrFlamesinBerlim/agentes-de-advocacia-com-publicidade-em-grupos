#!/usr/bin/env python3
"""
MABIOS v4 — Google Tasks Bulk Import Helper
Prepara tarefas para importação em lote no Google Tasks
Data: 2026-07-22
"""

import json
from datetime import datetime
from pathlib import Path
import re

class GoogleTasksImporter:
    """Converte documento de tarefas para formato Google Tasks"""

    TAREFAS_TEMPLATE = {
        "T001": {
            "title": "🚨 VIAGEM HUMAITÁ — URGENTE",
            "description": "Processo: 0609455-41.2023.8.04.4400 (Alexandre Marques de Campos)\nComarca: Humaitá/AM\nAção: Criar tarefa urgente viajar para Humaitá\nDatas: Quinta / Sexta / Monday (Sexta mais provável)",
            "deadline": "31/07/2026",
            "priority": "CRÍTICO",
            "client": "Alexandre Marques de Campos",
            "process": "0609455-41.2023.8.04.4400",
            "comarca": "Humaitá/AM"
        },
        "T002": {
            "title": "🚨 PROTOCOLAR PETIÇÃO RESCISÓRIA",
            "description": "Processo: 0611311-40.2023.8.04.4400 (Alexandre Marques de Campos)\nClasse: Inquérito Policial\nAção: Protocolar petição (já pronta)\nDetalhes: Cobrar diligência do novo juiz / Envio imediato em conclusão",
            "deadline": "25/07/2026",
            "priority": "CRÍTICO",
            "client": "Alexandre Marques de Campos",
            "process": "0611311-40.2023.8.04.4400",
            "comarca": "TJAM"
        },
        "T003": {
            "title": "🚨 REUNIÃO COM CLIENTE BERNADETE",
            "description": "Processo: 7012658-71.2025.8.22.0001 (Bernadete da Silva Goveia)\nComarca: Porto Velho\nAção: Transformar em tarefa + agendar reunião\nObjetivo: Decidir próximos passos do caso",
            "deadline": "26/07/2026",
            "priority": "CRÍTICO",
            "client": "Bernadete da Silva Goveia",
            "process": "7012658-71.2025.8.22.0001",
            "comarca": "Porto Velho"
        },
        "T004": {
            "title": "⏰ JUNTAR CUSTAS — LILIAN",
            "description": "Processo: 7053758-06.2025.8.22.0001 (Lilian de Jesus Borges)\nAção: Juntar custas do processo",
            "deadline": "29/07/2026",
            "priority": "ALTO",
            "client": "Lilian de Jesus Borges",
            "process": "7053758-06.2025.8.22.0001",
            "comarca": "Porto Velho"
        },
        "T005": {
            "title": "⏰ JUNTAR TERMO DE REVOGAÇÃO",
            "description": "Processo: 7077392-31.2025.8.22.0001 (Jefferson Sinfronio de Oliveira)\nAção: Criar tarefa para juntar termo de revogação",
            "deadline": "29/07/2026",
            "priority": "ALTO",
            "client": "Jefferson Sinfronio de Oliveira",
            "process": "7077392-31.2025.8.22.0001",
            "comarca": "Porto Velho"
        },
        "T006": {
            "title": "⏰ VERIFICAR NOTAS FISCAIS — ALDEMIR",
            "description": "Processo: 7032995-81.2025.8.22.0001 (Aldemir Ribeiro da Silva)\nAção: Levantar notas fiscais (informações já coletadas)",
            "deadline": "31/07/2026",
            "priority": "MÉDIO",
            "client": "Aldemir Ribeiro da Silva",
            "process": "7032995-81.2025.8.22.0001",
            "comarca": "Porto Velho"
        },
        "T007": {
            "title": "⏰ CHECAR ACOMPANHAMENTO MANDADO PRISÃO",
            "description": "Processo: 7026053-67.2024.8.22.0001 (Leandro Pereira Cardoso)\nÚltima Mov: 23/05/2024 - Definitivo (DESATUALIZADO)\nAção: Obter Outlook para Android + acompanhar caso",
            "deadline": "25/07/2026",
            "priority": "CRÍTICO",
            "client": "Leandro Pereira Cardoso",
            "process": "7026053-67.2024.8.22.0001",
            "comarca": "Porto Velho"
        }
    }

    @staticmethod
    def converter_data(data_str):
        """Converte formato DD/MM/YYYY para formato Google Tasks"""
        try:
            return datetime.strptime(data_str, '%d/%m/%Y').isoformat()
        except:
            return None

    @staticmethod
    def gerar_csv_import():
        """Gera CSV para importação em Google Tasks"""
        csv_header = "Task Name,Due Date,Priority\n"
        csv_rows = []

        for task_id, task_data in GoogleTasksImporter.TAREFAS_TEMPLATE.items():
            due_date = GoogleTasksImporter.converter_data(task_data['deadline'])
            priority_map = {
                'CRÍTICO': 'High',
                'ALTO': 'Medium',
                'MÉDIO': 'Low'
            }
            priority = priority_map.get(task_data['priority'], 'Low')

            csv_rows.append(f'"{task_data["title"]}","{task_data["deadline"]}","{priority}"')

        return csv_header + '\n'.join(csv_rows)

    @staticmethod
    def gerar_json_estruturado():
        """Gera JSON estruturado com dados completos das tarefas"""
        return json.dumps(GoogleTasksImporter.TAREFAS_TEMPLATE, ensure_ascii=False, indent=2)

    @staticmethod
    def gerar_markdown_checklist():
        """Gera markdown com checklist de importação manual"""
        md = "# 📋 CHECKLIST DE IMPORTAÇÃO — GOOGLE TASKS\n\n"
        md += "**Data**: " + datetime.now().strftime('%d/%m/%Y') + "\n"
        md += "**Total de tarefas**: " + str(len(GoogleTasksImporter.TAREFAS_TEMPLATE)) + "\n\n"

        md += "## 🚨 CRÍTICAS (7) — Importar HOJE\n"
        criticas = [t for t in GoogleTasksImporter.TAREFAS_TEMPLATE.values() if t['priority'] == 'CRÍTICO']
        for i, task in enumerate(criticas, 1):
            md += f"{i}. ☐ **{task['title']}** ({task['deadline']})\n"

        md += "\n## 🟡 ALTAS (2) — Importar semana que vem\n"
        altas = [t for t in GoogleTasksImporter.TAREFAS_TEMPLATE.values() if t['priority'] == 'ALTO']
        for i, task in enumerate(altas, 1):
            md += f"{i}. ☐ **{task['title']}** ({task['deadline']})\n"

        md += "\n## 🟢 MÉDIAS (1) — Importar depois\n"
        medias = [t for t in GoogleTasksImporter.TAREFAS_TEMPLATE.values() if t['priority'] == 'MÉDIO']
        for i, task in enumerate(medias, 1):
            md += f"{i}. ☐ **{task['title']}** ({task['deadline']})\n"

        md += "\n## 📝 INSTRUÇÕES DE IMPORTAÇÃO\n"
        md += """
1. Acesse [https://tasks.google.com](https://tasks.google.com)
2. Crie uma lista chamada "De Brito Advocacia — OAB/RO 2952"
3. Copie cada tarefa abaixo e crie manualmente em Google Tasks
4. Defina as datas de vencimento (deadline)
5. Ative notificações para 1 dia antes do prazo

## ✅ VERIFICAÇÃO PÓS-IMPORTAÇÃO

- [ ] Todas as 7 tarefas críticas criadas
- [ ] Datas de vencimento configuradas corretamente
- [ ] Notificações ativadas em desktop + mobile
- [ ] Tarefas aparecem no Google Calendar
- [ ] Integração Gmail-Tasks ativada
"""
        return md

def main():
    """Exporta formatos de importação"""
    importer = GoogleTasksImporter()

    # Criar diretório de saída
    output_dir = Path.home() / "MABIOS" / "import"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Gerar CSV
    csv_content = importer.gerar_csv_import()
    csv_file = output_dir / "tarefas_google_tasks.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    print(f"✅ CSV exportado: {csv_file}")

    # Gerar JSON
    json_content = importer.gerar_json_estruturado()
    json_file = output_dir / "tarefas_google_tasks.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json_content)
    print(f"✅ JSON exportado: {json_file}")

    # Gerar Markdown checklist
    md_content = importer.gerar_markdown_checklist()
    md_file = output_dir / "CHECKLIST_IMPORTACAO.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ Checklist exportado: {md_file}")

    print(f"\n📁 Todos os arquivos salvos em: {output_dir}")

if __name__ == '__main__':
    main()
