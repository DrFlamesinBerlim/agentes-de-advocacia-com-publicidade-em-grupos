# 🖱️ COMO EXECUTAR O FIX TOUCHPAD

## ⚡ Forma Mais Rápida (Recomendado)

### Opção 1: Duplo clique no arquivo (SE a política permitir)

1. Procure por `fix_touchpad.ps1` na pasta
2. Clique direito nele
3. Escolha "Executar com PowerShell"
4. Clique "Sim" se pedir confirmação

✓ O script vai rodar automaticamente

---

### Opção 2: Via PowerShell (Garantido Funciona)

1. **Abra PowerShell como ADMINISTRADOR**
   - Clique em Windows (canto inferior esquerdo)
   - Digite: `powershell`
   - Clique direito em "Windows PowerShell"
   - Escolha "Executar como administrador"

2. **Copie este comando:**
   ```powershell
   cd C:\Users\SeuNome\Downloads
   powershell -ExecutionPolicy Bypass -File fix_touchpad.ps1
   ```

   Substitua `SeuNome` pelo seu usuário do Windows

3. **Cole no PowerShell e pressione ENTER**

✓ O script vai rodar automaticamente

---

## 📍 Localização do Arquivo

O arquivo `fix_touchpad.ps1` está em:
```
C:\Users\SeuNome\Downloads\
ou
C:\Users\SeuNome\Documents\
ou
C:\caminho\onde\você\clonou\o\repositório\
```

---

## 🎯 O Que o Script Faz

```
PASSO 1/4: Restaurando Serviços Críticos
   ✓ PlugPlay (para reconhecer periféricos)
   ✓ hidserv (Human Interface Device)
   ✓ DcaSvc (Device Setup)
   ✓ DHCP (internet)
   ✓ DNS (internet)

PASSO 2/4: Habilitando Touchpad
   Procura por: Synaptics, ELAN, Touchpad
   Encontrado: [seu touchpad]
   ✓ Habilitando...

PASSO 3/4: Limpando Registros
   ✓ Removendo atalhos órfãos

PASSO 4/4: Reiniciando Windows
   ✓ Encerrando Explorer
   ✓ Iniciando Explorer
   🔄 Reiniciando em 30 segundos...
```

---

## ⚠️ Se Aparecer Erro de "Política de Execução"

Execute este comando PRIMEIRO:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

Depois execute:
```powershell
powershell -ExecutionPolicy Bypass -File fix_touchpad.ps1
```

---

## 📺 Output Esperado

```
================================================================================
🖱️  FIX TOUCHPAD - Reparador Automático
================================================================================

✓ Executando com privilégios de ADMIN

────────────────────────────────────────────────────────────────────────────────
PASSO 1/4: Restaurando Serviços Críticos...
────────────────────────────────────────────────────────────────────────────────

   Configurando PlugPlay → Automático... ✓
   Configurando hidserv → Automático... ✓
   Configurando DcaSvc → Manual... ✓
   Configurando Dhcp → Automático... ✓
   Configurando Dnscache → Automático... ✓
   Configurando nsi → Automático... ✓

✅ Serviços restaurados

────────────────────────────────────────────────────────────────────────────────
PASSO 2/4: Habilitando Touchpad...
────────────────────────────────────────────────────────────────────────────────

   Encontrado: ELAN Touchpad
      Status: Error → Habilitado ✓

✅ Touchpad habilitado com sucesso!

────────────────────────────────────────────────────────────────────────────────
PASSO 3/4: Limpando Registros Inválidos...
────────────────────────────────────────────────────────────────────────────────

   Removendo atalhos órfãos... ✓

✅ Registro limpo

────────────────────────────────────────────────────────────────────────────────
PASSO 4/4: Preparando para Reiniciar...
────────────────────────────────────────────────────────────────────────────────

   Encerrando Explorer... ✓
   Iniciando Explorer... ✓

✅ Tudo pronto para reiniciar!

================================================================================
🔄 REINICIANDO WINDOWS
================================================================================

⏱️  Seu notebook vai reiniciar em 30 segundos...

   Salve seus arquivos! Você será desconectado automaticamente.

   Pressione Ctrl+C para CANCELAR o restart (não é recomendado)

   Reiniciando em: 30 segundos
   Reiniciando em: 29 segundos
   ...
   Reiniciando agora!

✨ Script concluído! Reinicio iniciado...
```

---

## ✅ Depois de Reiniciar

Após o Windows reiniciar:

1. **Teste o mousepad/touchpad**
   - Passe o dedo sobre ele
   - O cursor deve se mover

2. **Se funcionar:**
   - 🎉 Perfeito! Seu touchpad foi reparado!

3. **Se não funcionar:**
   - Vá para: [REPARO_TOUCHPAD.md](./REPARO_TOUCHPAD.md)
   - Siga as instruções manuais

---

## 🆘 Problemas Durante Execução

### "Acesso Negado"
```powershell
# Execute como ADMINISTRADOR!
# Windows + X → Windows PowerShell (Admin)
```

### "Script is disabled"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### "Arquivo não encontrado"
```powershell
# Certifique-se que está na pasta correta
cd C:\Users\SeuNome\Downloads
ls fix_touchpad.ps1
```

---

## 📞 Resumo de 3 Linhas

```
1. Abra PowerShell como ADMIN (Windows + X)
2. Digite: powershell -ExecutionPolicy Bypass -File fix_touchpad.ps1
3. Pressione ENTER e deixe rodar
```

**Pronto! 🚀**

---

## 🎁 Bônus: Automatizar

Se quiser executar sempre que iniciar:

1. Abra: `Win + R`
2. Digite: `shell:startup`
3. Coloque `fix_touchpad.ps1` lá
4. Próximo boot: executa automaticamente

---

**Boa sorte! Seu touchpad vai funcionar! 💪**
