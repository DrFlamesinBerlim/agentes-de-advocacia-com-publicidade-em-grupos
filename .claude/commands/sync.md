# /sync — Forçar sincronização GitHub

Verifica o estado de sync entre Antigravity (local) e GitHub (nuvem).

---

Ao receber este comando:

1. Leia `antigravity_output.txt` — mostre as últimas 20 linhas (atividade recente)
2. Leia `sync_state.json` se existir — mostre timestamp do último sync
3. Verifique `documentos/processos.json` — timestamp `atualizado_em`
4. Informe o que está desatualizado

**Comando PowerShell para forçar sync no Antigravity:**
```powershell
cd "C:\Users\advog\Meu Drive\X"
python agente_andamentos\sync_github.py
```

**Ou sync manual via git:**
```powershell
cd "C:\Users\advog\Meu Drive\X"
git add documentos\processos.json documentos\tarefas.json documentos\prazos_pendentes.json antigravity_output.txt
git commit -m "sync manual"
git push origin claude/upbeat-fermat-0x6gd8
```

Informe se há diferença entre dados locais (Antigravity tem 63+ processos) e o que está visível no GitHub (21 processos) — isso indica que o Antigravity não está rodando ou o push falhou.
