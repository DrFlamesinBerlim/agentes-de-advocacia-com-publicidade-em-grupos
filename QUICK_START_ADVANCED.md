# ⚡ QUICK START - System Cleaner ADVANCED

Começar em 2 minutos!

---

## 🎯 PASSO 1: AMBIENTE

✅ Python 3.7+ instalado
✅ Privilégios de administrador
✅ Arquivo: `system_cleaner_advanced.py`
✅ Config: `cleaner_config.json`

---

## 🚀 PASSO 2: EXECUTAR (SEGURO)

```cmd
python system_cleaner_advanced.py
```

Isso vai:
1. ✅ Criar restore point automático
2. ✅ Escanear arquivos temporários
3. ✅ Mostrar prévia (DRY-RUN)
4. ✅ **NÃO deletar nada**

---

## 📋 PASSO 3: REVISAR PRÉVIA

Você verá algo assim:

```
╔════════════════════════════════════════════════════════════════════════╗
║ SYSTEM CLEANER ADVANCED - Windows Optimization Tool                  ║
║ Integra padrões: Win11Debloat, TronScript, BleachBit, Harden-Windows║
╚════════════════════════════════════════════════════════════════════════╝

Status: ✓ ADMIN
Dry-run: HABILITADO

╔ INICIANDO LIMPEZA COMPLETA ╗

[ACTION] RestorePoint: Criando restore point: PreCleanup-20240115-143051
[SUCCESS] RestorePoint: Restore point criado: PreCleanup-20240115-143051

▶ Limpando Arquivos Temporários...
Deletando arquivos: [██████████████░░░░░░░░░░░░░░] 50% | 175/350 | ETA: 4s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PRÉVIA DO QUE SERÁ EXECUTADO (DRY-RUN)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivos a deletar: 350
Espaço a liberar: 256.50 MB

Operações:
  ✓ Limpeza de Temporários
    → 350 arquivos, 256.50 MB
```

---

## ✅ PASSO 4: CONFIRMAÇÃO

Se tudo parece correto:

```cmd
python system_cleaner_advanced.py --apply
```

Agora vai:
1. Recriar restore point
2. **Realmente deletar os arquivos**
3. Gerar relatório final

---

## 📊 PASSO 5: VISUALIZAR RESULTADOS

Arquivo de log gerado: `cleaner_advanced_log.json`

```json
{
  "start_time": "2024-01-15T14:30:45.123456",
  "end_time": "2024-01-15T14:30:57.654321",
  "logs": [
    {
      "timestamp": "2024-01-15T14:30:45.123456",
      "level": "ACTION",
      "category": "RestorePoint",
      "message": "Criando restore point: PreCleanup-20240115-143051"
    },
    {
      "timestamp": "2024-01-15T14:30:46.234567",
      "level": "SUCCESS",
      "category": "RestorePoint",
      "message": "Restore point criado: PreCleanup-20240115-143051"
    }
  ]
}
```

---

## 🎮 CUSTOMIZAR CONFIGURAÇÃO

Edite `cleaner_config.json`:

### Habilitar/Desabilitar Categorias

```json
"categories": {
  "Temporary Files": {
    "enabled": true        ← Mude para false para desabilitar
  }
}
```

### Mudar Localizações

```json
"Temporary Files": {
  "locations": [
    "%TEMP%",
    "%TMP%",
    "C:\\Custom\\Path"     ← Adicione seus caminhos aqui
  ]
}
```

### Ajustar Padrões de Arquivo

```json
"patterns": [
  "*.tmp",
  "*.log",
  "~*"                     ← Quais arquivos procurar
]
```

---

## ⚠️ MODO DRY-RUN (PADRÃO)

```json
"operations": {
  "dry_run_enabled": true  ← Sempre desabilita deleção
}
```

Para desabilitar:
```json
"dry_run_enabled": false
```

---

## 🔒 PROTEÇÃO DE SEGURANÇA

O script NUNCA deleta:

```json
"security": {
  "system_folders_protected": [
    "C:\\Windows",
    "C:\\Program Files"
  ],
  "never_delete_patterns": [
    "System32",
    "boot"
  ]
}
```

---

## 🆘 PROBLEMAS?

### Sem privilégios de administrador
```
Error: Script deve rodar como administrador
```
→ Clique direito no CMD → "Executar como administrador"

### Restore point não criado
```
Warning: Falha ao criar restore point
```
→ PowerShell pode estar desabilitado (continua mesmo assim)

### Arquivo não encontrado
```
Error: FileNotFoundError: [Errno 2] No such file or directory: 'cleaner_config.json'
```
→ Certifique que `cleaner_config.json` está no mesmo diretório

---

## 🚀 PRÓXIMAS FASES

Este é apenas o **PASSO 1** de integração open source!

```
✅ Fase 1: PADRÕES BÁSICOS (Done)
   - Restore points (Win11Debloat)
   - Dry-run (BleachBit)
   - JSON config (Padrão Industrial)
   - Structured logging (Harden-Windows)

🔄 Fase 2: MALWARE DETECTION (Next)
   - VirusTotal API
   - Scan automático
   - Quarantine system

📅 Fase 3: ADVANCED FEATURES
   - Bloatware removal
   - Driver optimization
   - Predictive monitoring

🎨 Fase 4: MODERN FRONTEND
   - C# WinUI 3
   - Real-time dashboard
   - Automatic scheduling
```

---

## 📖 MAIS INFORMAÇÕES

- README_ADVANCED_CLEANER.md - Documentação completa
- cleaner_config.json - Configuração editável
- OPEN_SOURCE_RESEARCH.md - Padrões integrados
- FEATURES_INTELIGENTES.md - Funcionalidades planejadas

---

**Tudo pronto! Execute agora:** 🎉

```cmd
python system_cleaner_advanced.py
```

