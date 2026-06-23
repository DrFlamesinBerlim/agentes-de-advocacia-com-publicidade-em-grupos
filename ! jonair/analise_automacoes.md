# 🤖 AUDITORIA DE AUTOMAÇÕES & ESTRATÉGIA DE WATCHDOG

Este documento apresenta uma análise técnica detalhada sobre o ecossistema de automações do escritório **De Brito Advocacia**, identificando o estado de funcionamento, vulnerabilidades, o que deve ser congelado (`freezed`), e a estratégia para manter os agentes ativos 24/7 através de um serviço Watchdog.

---

## 🔍 1. MAPEAMENTO E AUDITORIA DAS AUTOMAÇÕES ATUAIS

### A. Módulo de Andamentos Processuais (`agente_andamentos/`)
* **Componentes:** `agente_andamentos.py`, `atualizar_processos.py`, `modulo_prazos.py`, `modulo_calendar.py`.
* **Status de Funcionamento:**  **Parcialmente Operacional**.
  * *O que funciona:* O fluxo de consulta de processos públicos nos tribunais mapeados (TJRO, TJAM, TRT14, etc.) via API pública do CNJ DataJud. O cálculo de prazos (`modulo_prazos.py`) e a integração com a Google Calendar API (`modulo_calendar.py`) funcionam perfeitamente para criar marcos na agenda.
  * *O que NÃO funciona (Gaps):*
    1. **Processos em Segredo de Justiça:** A API pública não retorna dados de processos sob segredo (como a Revisão Criminal de Jonair `0800556-72.2026.8.22.0000` ou processos da comarca de Viana da Keila). Eles retornam 0 hits, gerando falsos negativos de atualização.
    2. **Vulnerabilidade de Credenciais:** Se a chave de API cadastrada (`cnj_api_key`) expirar ou for revogada (como ocorreu com a nova chave fornecida `cDZHYzlZa0JadVREZDJCendF...`), o script quebra silenciosamente com erro HTTP 401 ou 403, a menos que haja um tratamento de fallback estruturado.

### B. Processamento e Transcrição de WhatsApp (`automacoes/`)
* **Componentes:** `whatsapp_processor_core.py`, `process_local_zips.py`, `process_whatsapp_exports.py`.
* **Status de Funcionamento:**  **100% Operacional**.
  * *O que funciona:* Extração de ZIPs, conversão de áudios `.opus` para `.wav` via FFmpeg, transcrição automática em português, inserção em log de chat e geração de relatórios estilizados em PDF via Playwright. Os arquivos são organizados na pasta do cliente sob uma taxonomia limpa.
  * *Estabilidade:* Corrigido recentemente o bug de grafia do particípio verbal ("transcrevido" retificado para "transcrito").

---

## ❄️ 2. CONGELAMENTO DE CÓDIGO (Edition Freezed)
Para evitar regressões em componentes críticos que já estão totalmente testados e funcionais, os seguintes scripts devem ser marcados como **FREEZED** (sem edições de código adicionais permitidas, exceto por ordens explícitas de nível L3/Jefferson):

1. **[FREEZED] [whatsapp_processor_core.py](file:///c:/Users/advog/Meu%20Drive/X/automacoes/whatsapp_processor_core.py):** Toda a pipeline de parse de WhatsApp, transcrição de áudio e geração de PDF via Playwright está validada e funcional.
2. **[FREEZED] [modulo_prazos.py](file:///c:/Users/advog/Meu%20Drive/X/agente_andamentos/modulo_prazos.py):** As regras de cálculo de prazos com contagem em dias úteis (CPC) e dias corridos (CPP) estão perfeitamente mapeadas.

---

## 🛠️ 3. PONTOS DE MELHORIA E GAPS A RESOLVER (TAREFAS)

- `[ ]` **Implementação de Fallback de API no Agente Principal:**
  * *Melhoria:* Portar a lógica de chave dupla criada em `query_mabios_tjes.py` para o script principal `agente_andamentos.py`. Se o request retornar 401 com a chave configurada, tentar automaticamente a chave reserva.
  
- `[ ]` **Alertas Automáticos de Segredo de Justiça:**
  * *Melhoria:* No `agente_andamentos.py`, se um processo cadastrado for de um tribunal suportado mas retornar 0 hits na API do CNJ, o script deve marcar o status como "Segredo de Justiça / Requer Consulta Manual via PJe" no e-mail diário, em vez de apenas logar "Sem dados".

---

## 🐕 4. COMO MANTER OS AGENTES PESQUISANDO VIA WATCHDOG

O monitor `loop_monitor.py` é o responsável por agir como uma ponte em tempo real (Watchdog) no computador local do escritório. Ele escuta as alterações da pasta `X` e executa comandos solicitados pelos agentes em nuvem (como Claude ou Gemini) de forma imediata quando arquivos de handshake (`claude_output.txt` ou `gemini_output.txt`) são sincronizados pelo Google Drive.

### Por que a ação do watchdog não estava visível?
O watchdog só funciona se o processo Python do `loop_monitor.py` estiver **rodando continuamente na máquina local** (Windows do escritório). Se a máquina for reiniciada ou o terminal for fechado, o monitor morre.

### Plano de Ação: Manter o Watchdog Ativo 24/7 no Windows

Para garantir que o monitor nunca pare e rode de forma totalmente silenciosa no computador local, siga os passos abaixo para configurá-lo como um serviço persistente:

#### Método A: Execução Silenciosa via Script VBS (Recomendado)
Para evitar que uma janela preta do prompt de comando fique aberta na tela e seja fechada acidentalmente pelo usuário, podemos rodar o script em background utilizando um VBScript.

1. Crie o arquivo `C:\Users\advog\Meu Drive\X\iniciar_monitor_oculto.vbs` com o seguinte conteúdo:
   ```vbs
   Set WshShell = CreateObject("WScript.Shell")
   WshShell.Run "python ""C:\Users\advog\Meu Drive\X\automacoes\loop_monitor.py""", 0, False
   ```
2. Adicione este arquivo `.vbs` na pasta de Inicializar do Windows (`Startup`):
   * Aperte `Win + R`, digite `shell:startup` e clique em OK.
   * Crie um atalho para o arquivo `iniciar_monitor_oculto.vbs` nesta pasta.
   * Toda vez que o computador ligar, o monitor iniciará silenciosamente em segundo plano.

#### Método B: Configuração via Agendador de Tarefas do Windows
Podemos forçar o Windows a manter o script rodando infinitamente:
1. Abra o **Agendador de Tarefas** (`Task Scheduler`).
2. Crie uma nova Tarefa Básica chamada `Watchdog Agentes De Brito`.
3. Defina o disparador para **"Ao iniciar o computador"**.
4. Na ação, escolha **"Iniciar um programa"**:
   * Programa/script: `python`
   * Argumentos: `"C:\Users\advog\Meu Drive\X\automacoes\loop_monitor.py"`
5. Nas propriedades da tarefa:
   * Marque a opção **"Executar estando o usuário conectado ou não"** (para rodar como serviço de sistema).
   * Na aba "Configurações", marque **"Se a tarefa falhar, reiniciar a cada: 1 minuto"** e defina tentativas infinitas.
