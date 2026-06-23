import requests
import json
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configurações
API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
CLIENT_DIR = r"C:\Users\advog\Meu Drive\AI downloads\escritorio\clientes\Cli Keila Pastorini"

PROCESSOS = [
    {
        "numero": "50178267220268080024",
        "numero_fmt": "5017826-72.2026.8.08.0024",
        "tipo": "Ação de Indenização (Crédito de R$ 120.000)",
        "limite_movimentos": 10
    },
    {
        "numero": "00040195620158080024",
        "numero_fmt": "0004019-56.2015.8.08.0024",
        "tipo": "Ação de Usucapião",
        "limite_movimentos": 10
    },
    {
        "numero": "00301422820148080024",
        "numero_fmt": "0030142-28.2014.8.08.0024",
        "tipo": "Ação de Imissão na Posse",
        "limite_movimentos": 10
    }
]

def query_datajud(numero):
    url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjes/_search"
    headers = {
        "Authorization": f"ApiKey {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": {
            "match": {
                "numeroProcesso": numero
            }
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if resp.status_code == 200:
            hits = resp.json().get("hits", {}).get("hits", [])
            if hits:
                return hits[0].get("_source", {})
        return None
    except Exception as e:
        print(f"Erro ao consultar {numero}: {e}")
        return None

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("Iniciando consulta aos processos de Espírito Santo (TJES)...")
    
    os.makedirs(CLIENT_DIR, exist_ok=True)
    
    md_lines = []
    html_cards = []
    
    date_now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    md_lines.append("# RELATÓRIO DE PROCESSOS - ESPÍRITO SANTO (TJES)")
    md_lines.append(f"**Cliente:** Cli Keila Pastorini")
    md_lines.append(f"**Data de Emissão:** {date_now_str}")
    md_lines.append("\n---\n")
    
    for p in PROCESSOS:
        print(f"Buscando {p['numero_fmt']}...")
        data = query_datajud(p["numero"])
        
        if not data:
            md_lines.append(f"## {p['tipo']}\n**Número:** {p['numero_fmt']}\n*Erro: Não encontrado no DataJud ou sem movimentações.*")
            html_cards.append(f"""
            <div class="process-card">
                <div class="process-header">
                    <span class="process-title">{p['tipo']}</span>
                    <span class="process-meta">Número: {p['numero_fmt']}</span>
                </div>
                <p style="color:#ef4444;font-size:13px;">Processo não localizado na API DataJud.</p>
            </div>
            """)
            continue
            
        classe = data.get("classe", {}).get("nome", "Não Informada")
        orgao = data.get("orgaoJulgador", {}).get("nome", "Não Informado")
        dist = data.get("dataDistribuicao", "Não Informada")
        
        # Formatar data de distribuição
        if dist and dist != "Não Informada":
            try:
                dt_d = datetime.fromisoformat(dist.replace("Z", "+00:00"))
                dist = dt_d.strftime("%d/%m/%Y")
            except:
                pass
                
        movimentos = data.get("movimentos", [])
        
        md_lines.append(f"## {p['tipo']}")
        md_lines.append(f"- **Número do Processo:** {p['numero_fmt']}")
        md_lines.append(f"- **Classe Processual:** {classe}")
        md_lines.append(f"- **Órgão Julgador:** {orgao}")
        md_lines.append(f"- **Data de Distribuição:** {dist}")
        md_lines.append(f"- **Total de Movimentações:** {len(movimentos)}")
        md_lines.append("\n### Últimas Movimentações:")
        
        movs_html = []
        # Limita o número de movimentos a exibir para não ficar muito longo
        display_movs = movimentos[:p["limite_movimentos"]]
        
        for i, m in enumerate(display_movs):
            dt_raw = m.get("dataHora", "")
            dt_fmt = dt_raw
            if dt_raw:
                try:
                    dt = datetime.fromisoformat(dt_raw.replace("Z", "+00:00"))
                    dt_fmt = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    pass
            
            nome = m.get("nome", "")
            desc = m.get("descricao", "")
            
            # Formatar no markdown
            md_lines.append(f"{i+1}. **{dt_fmt}** — {nome}")
            if desc:
                md_lines.append(f"   *Descrição:* {desc}")
                
            # Formatar no HTML para o PDF
            desc_html = f'<div class="movement-desc">Descrição: {desc}</div>' if desc else ""
            movs_html.append(f"""
            <div class="movement-item">
                <span class="movement-date">{dt_fmt}</span>
                <div class="movement-name">{nome}</div>
                {desc_html}
            </div>
            """)
            
        md_lines.append("\n---\n")
        
        movs_joined = "\n".join(movs_html)
        html_cards.append(f"""
        <div class="process-card">
            <div class="process-header">
                <div>
                    <span class="process-title">{p['tipo']}</span>
                    <div class="process-meta">Número: {p['numero_fmt']} | Órgão: {orgao}</div>
                </div>
                <div style="font-size: 11px; color: #64748b; text-align: right;">
                    Classe: {classe}<br>
                    Distr: {dist}
                </div>
            </div>
            <div class="movement-list">
                {movs_joined}
            </div>
        </div>
        """)

    # Salva o arquivo Markdown
    md_output_path = os.path.join(CLIENT_DIR, "Relatório - Processos Espírito Santo (TJES).md")
    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[OK] Relatório Markdown salvo em: {md_output_path}")

    # Renderiza o PDF usando o Playwright
    html_cards_joined = "\n".join(html_cards)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Relatório de Processos TJES - Cli Keila Pastorini</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    body {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }}
    .header {{
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }}
    .header h1 {{
        font-size: 22px;
        margin: 0;
        color: #0f172a;
        font-weight: 700;
    }}
    .header .meta {{
        font-size: 13px;
        color: #64748b;
        margin-top: 5px;
        line-height: 1.6;
    }}
    .process-card {{
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        background-color: #fafafa;
        page-break-inside: avoid;
        break-inside: avoid;
    }}
    .process-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }}
    .process-title {{
        font-size: 15px;
        font-weight: 700;
        color: #1e3a8a;
    }}
    .process-meta {{
        font-size: 12px;
        color: #475569;
        margin-top: 4px;
    }}
    .movement-list {{
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}
    .movement-item {{
        padding-left: 12px;
        border-left: 2px solid #94a3b8;
        position: relative;
        font-size: 13px;
    }}
    .movement-item::before {{
        content: '';
        width: 6px;
        height: 6px;
        background-color: #64748b;
        border-radius: 50%;
        position: absolute;
        left: -4px;
        top: 5px;
    }}
    .movement-date {{
        font-weight: 600;
        color: #475569;
        font-size: 11px;
    }}
    .movement-name {{
        color: #0f172a;
        font-weight: 500;
        margin-top: 2px;
    }}
    .movement-desc {{
        color: #64748b;
        font-size: 12px;
        margin-top: 2px;
        font-style: italic;
    }}
</style>
</head>
<body>
    <div class="header">
        <h1>Relatório de Processos - Espírito Santo (TJES)</h1>
        <div class="meta">
            <strong>Escritório:</strong> De Brito Advocacia<br>
            <strong>Cliente:</strong> Cli Keila Pastorini<br>
            <strong>Data da Consulta:</strong> {date_now_str}
        </div>
    </div>
    <div class="chat-container">
        {html_cards_joined}
    </div>
</body>
</html>
"""
    
    pdf_output_path = os.path.join(CLIENT_DIR, "Relatório - Processos Espírito Santo (TJES).pdf")
    temp_html_path = pdf_output_path + ".temp.html"
    try:
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file:///{os.path.abspath(temp_html_path)}")
            page.wait_for_load_state("networkidle")
            page.pdf(
                path=pdf_output_path,
                format="A4",
                print_background=True,
                margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"}
            )
            browser.close()
        print(f"[OK] Relatório PDF salvo em: {pdf_output_path}")
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
    finally:
        if os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except Exception:
                pass

if __name__ == "__main__":
    main()
