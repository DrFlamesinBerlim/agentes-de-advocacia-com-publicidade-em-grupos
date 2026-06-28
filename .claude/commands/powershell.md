# /powershell — Comandos prontos para colar no PowerShell (Antigravity)

Gera comandos PowerShell prontos para executar no Antigravity local.

---

## Iniciar loop principal (Antigravity)
```powershell
cd "C:\Users\advog\Meu Drive\X"
python agente_andamentos\loop_monitor.py
```

## Processar rascunhos MABIOS_ACTION manualmente
```powershell
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_mabios_email.py" gmail
```

## Varrer caixa de entrada jurídica (Gmail inbox)
```powershell
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_emails.py" gmail
```

## Relatório de processos ativos
```powershell
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_relatorios.py"
```

## Relatório por comarca
```powershell
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_relatorios.py" --comarca "$ARGS"
```

## Relatório por cliente
```powershell
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_relatorios.py" --cliente "$ARGS"
```

## Relatório urgentes
```powershell
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_relatorios.py" --urgentes
```

## Atualizar processos (DataJud + prazos)
```powershell
python "C:\Users\advog\Meu Drive\X\agente_andamentos\atualizar_processos.py"
```

## Sync forçado com GitHub
```powershell
cd "C:\Users\advog\Meu Drive\X"
git pull origin claude/upbeat-fermat-0x6gd8
git add -A
git commit -m "sync manual $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
git push origin claude/upbeat-fermat-0x6gd8
```

## Ver log do loop_monitor
```powershell
Get-Content "C:\Users\advog\Meu Drive\X\logs\loop_monitor.log" -Tail 50
```

## Ver antigravity_output.txt (canal Claude→Antigravity)
```powershell
Get-Content "C:\Users\advog\Meu Drive\X\antigravity_output.txt" -Tail 30
```

---

Se o usuário passou um argumento (ex: `/powershell ariquemes`), use como valor do filtro no comando de relatório.
