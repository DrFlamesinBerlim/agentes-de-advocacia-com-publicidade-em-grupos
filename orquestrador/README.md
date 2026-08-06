# Orquestrador MABIOS — a matriz

Um único processo Python que roda **permanentemente** numa máquina sua
(VM do Google Cloud, PC dedicado, etc.) e substitui os envios duplicados de
CC-001 (Apps Script) e GA-002 (loop_monitor.py).

## O que ele faz sozinho (automático)

1. **Relatório unificado** — a cada hora, lê `processos.json`, apaga
   qualquer email de relatório anterior (do orquestrador OU dos sistemas
   antigos) e manda um único email atualizado. Nunca acumula.
2. **Indexação da Pasta X** — a cada 30 min, varre a pasta e grava um
   índice local (`indice_pasta_x.json`) para pesquisa instantânea.
3. **Propostas de reorganização** — 1x por dia, escreve sugestões em
   `propostas_reorganizacao.md`. **Nunca move ou apaga nada sozinho.**

## Instalação (na VM do Google Cloud ou PC que ficará sempre ligado)

```bash
cd orquestrador
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Credenciais Google (uma vez)

1. https://console.cloud.google.com → seu projeto → **APIs e serviços → Credenciais**
2. **Criar credenciais → ID do cliente OAuth → Aplicativo para computador**
3. Baixe o JSON, salve como `orquestrador/credentials.json`
4. Ative as APIs: **Google Drive API** e **Gmail API**
5. Rode:
   ```bash
   python orquestrador_mabios.py --primeira-vez
   ```
   Abre o navegador, você autoriza (é você clicando, igual antes), gera
   `token.json`. Só acontece essa vez — depois ele renova sozinho.

## Rodar como a matriz (heartbeat permanente)

```bash
python orquestrador_mabios.py
```

Fica rodando para sempre. Para deixar ligado mesmo fechando o terminal:

**Linux (systemd)** — crie `/etc/systemd/system/mabios.service` apontando
para este script com `ExecStart=/caminho/venv/bin/python orquestrador_mabios.py`,
depois `systemctl enable --now mabios`.

**Ou simples, com `screen`/`tmux`:**
```bash
screen -S mabios
python orquestrador_mabios.py
# Ctrl+A depois D para sair sem matar o processo
```

**Windows:** Agendador de Tarefas, ação "Iniciar um programa", disparo "Ao
iniciar o computador", sem duração limite.

## Comandos pontuais (não precisa da matriz rodando)

```bash
python orquestrador_mabios.py --buscar "railson"      # pesquisa no índice
python orquestrador_mabios.py --so-indexar             # reindexar agora
python orquestrador_mabios.py --so-relatorio            # mandar relatório agora
python orquestrador_mabios.py --so-propor                # gerar propostas agora
python orquestrador_mabios.py --uma-vez                  # os três de uma vez
```

## Sobre a substituição do CC-001 e GA-002

Depois que a matriz estiver rodando e você confirmar que o relatório
unificado está correto:

- **Desative os gatilhos do CC-001** no Apps Script (menu Acionadores →
  apagar) para não duplicar envios.
- **Pare o `loop_monitor.py`** do GA-002 (ou ajuste-o para não mais enviar
  email, só alimentar dados) pelo mesmo motivo.

O orquestrador já apaga emails com os assuntos antigos (`[CC-001]...`,
`[MOB]/[DSK] [DE BRITO ADV]`, `[MOB]/[DSK] [MABIOS v3]`) antes de mandar o
novo, então mesmo que os sistemas antigos ainda mandem algo por um tempo,
a caixa de entrada não vai acumular — mas o ideal é desligá-los.
