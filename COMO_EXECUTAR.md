# 🖱️ COMO EXECUTAR OS SCRIPTS (Sem Windows+X)

## ⚡ Opção 1: MAIS FÁCIL - Clique Direito no Arquivo

### Passo 1: Localize o arquivo
```
fix_touchpad.bat
```

### Passo 2: Clique DIREITO nele
```
┌────────────────────────────┐
│ fix_touchpad.bat           │
│                            │
│ Abrir                      │
│ Editar                     │
│ ▶ Executar como Admin  ◄───┼─ CLIQUE AQUI
│ Renomear                   │
│ Deletar                    │
└────────────────────────────┘
```

### Passo 3: Escolha "Executar como administrador"

✓ Pronto! Script vai rodar automaticamente

---

## Opção 2: Via Prompt de Comando (CMD)

### Abra CMD de forma manual:

**Método A:**
1. Clique no Menu Iniciar
2. Procure por "Executar"
3. Digite: `cmd`
4. Pressione Enter

**Método B:**
1. Pressione: `Win + R` (ou Iniciar → Executar)
2. Digite: `cmd`
3. Pressione Enter

**Método C (Se Win+R não funciona):**
1. Clique em Menu Iniciar
2. Digite: `cmd`
3. Pressione Enter

### Então execute como ADMIN:

Na janela do CMD, copie e cole:

```cmd
cd %USERPROFILE%\Downloads
fix_touchpad.bat
```

Pressione Enter

---

## Opção 3: Duplo Clique Direto no Arquivo

Se o arquivo `.bat` estiver configurado:

1. Procure `fix_touchpad.bat`
2. Duplo clique nele
3. Clique "SIM" se pedir permissão
4. Script roda

---

## Opção 4: Via File Explorer (Explorador de Arquivos)

1. Abra File Explorer (pasta)
2. Vá em: `C:\Users\SeuNome\Downloads`
3. Procure por: `fix_touchpad.bat`
4. Clique direito → "Executar como administrador"

---

## 🎯 RESUMO

| Método | Dificuldade | Tempo |
|--------|------------|-------|
| **Clique Direito** | ⭐ Fácil | 10s |
| **Duplo Clique** | ⭐ Fácil | 10s |
| **Menu Iniciar + CMD** | ⭐⭐ Médio | 30s |
| **Win+R** | ⭐⭐ Médio | 30s |

---

## ✅ O Arquivo Correto

Procure por UM DESSES:

```
fix_touchpad.bat          ← Use este! (Batch - Qualquer Windows)
fix_touchpad.ps1          ← PowerShell (se PowerShell funcionar)
fix_mousepad.py           ← Python (se Python instalado)
```

---

## ⚠️ Se Pedir Permissão

Quando executar, pode aparecer:

```
Deseja permitir que este programa faça alterações no seu computador?
```

Clique: **SIM** ou **Permitir**

---

## 📺 O Que Vai Aparecer

```
================================================================================

                  [REPARADOR DE TOUCHPAD - FIX TOUCHPAD]

================================================================================

[ADMIN] Executando com privilegios de administrador

================================================================================
PASSO 1/3: Restaurando Servicos Criticos...
================================================================================

   Configurando PlugPlay...
   [OK] PlugPlay restaurado
   
   Configurando hidserv...
   [OK] hidserv restaurado
   
   ...

================================================================================
PASSO 2/3: Habilitando Touchpad via Registry...
================================================================================

   Importando configuracoes do registro...
   [OK] Registro atualizado

================================================================================
PASSO 3/3: Finalizando...
================================================================================

   Reiniciando em: 30 segundos...
   
   (Vai começar contagem regressiva)

```

---

## ✅ Depois de Reiniciar

Seu touchpad deve funcionar!

Se não:
1. Abra: `REPARO_TOUCHPAD.md`
2. Siga as instruções manuais

---

## 🆘 Se Nada Funcionar

**Última opção - Script Python:**

```cmd
pip install psutil
python fix_mousepad.py
```

Escolha opção 5 (FAZER TUDO)

---

**Qual método você vai usar? Recomendo: CLIQUE DIREITO NO ARQUIVO** 👆
