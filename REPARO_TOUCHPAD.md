# 🖱️ GUIA DE REPARO DO TOUCHPAD/MOUSEPAD

## ⚠️ Diagnóstico

Como você desligou serviços no MSConfig, provavelmente desabilitou:
- **Plug and Play** → Touchpad não é reconhecido
- **Device Installation Service** → Drivers não carregam
- **Human Interface Device Access** → Periféricos não funcionam

## ✅ Solução Rápida (5 minutos)

### Passo 1: Abra PowerShell como ADMIN

```
Windows + X → Windows PowerShell (Admin)
```

### Passo 2: Execute Este Comando

Copie e cole tudo de uma vez:

```powershell
# Restaurar serviços críticos
Set-Service -Name "PlugPlay" -StartupType Automatic -Status Running
Set-Service -Name "hidserv" -StartupType Automatic -Status Running
Set-Service -Name "DcaSvc" -StartupType Manual -Status Running
Set-Service -Name "Dhcp" -StartupType Automatic -Status Running

# Habilitar touchpad
Get-PnpDevice -PresentOnly | Where-Object { 
    $_.Name -match 'touch|pad|synaptics|elan|trackpad' 
} | ForEach-Object {
    Write-Host "Habilitando: $($_.Name)"
    Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false
}

# Reiniciar explorer
taskkill /f /im explorer.exe
Start-Process explorer.exe

# Reiniciar em 30 segundos
shutdown /r /t 30
```

### Passo 3: Aguarde Reiniciar

Windows vai reiniciar e o touchpad deve funcionar.

---

## 🔧 Se Não Funcionar: Método Manual

### Via Gerenciador de Dispositivos

1. **Abra Gerenciador de Dispositivos**
   - Windows + X → "Gerenciador de Dispositivos"

2. **Procure o Touchpad**
   - Procure por: "Mouse and other pointing devices"
   - Ou: "Mice and pointing devices"

3. **Localize o Touchpad**
   Pode estar com um desses nomes:
   - **Synaptics** (Dell, HP, Lenovo)
   - **ELAN** (Asus, Acer)
   - **Touchpad**
   - **TrackPad**
   - **Pointing Device**

4. **Se Tiver ⚠️ Amarelo**
   - Clique direito → "Habilitar dispositivo"
   - Espere 5 segundos
   - Se continuar com ⚠️, clique direito → "Desinstalar dispositivo"
   - Reinicie o notebook
   - Windows vai reinstalar automaticamente

5. **Se Não Aparecer**
   - Clique em "Exibir" (menu no topo)
   - Marque "Mostrar dispositivos ocultos"
   - Procure novamente

6. **Se Continuar Não Aparecendo**
   - Seu touchpad pode estar desabilitado na BIOS
   - Veja "Ativar na BIOS" abaixo

---

## 🖥️ Ativar na BIOS

Se o dispositivo não aparece no Gerenciador, pode estar desabilitado na BIOS.

### Como Acessar BIOS

1. **Reinicie o notebook**
2. **Na tela de inicialização (logo), pressione:**
   - **F2** (Dell, HP, Asus)
   - **F10** (HP mais antigos)
   - **Del** (Acer, alguns Asus)
   - **Fn + F2** (alguns Lenovo)

3. **Procure por:**
   - "Integrated Peripherals"
   - "Onboard Devices"
   - "Internal Pointing Device"
   - "Touchpad"

4. **Mude para "Enabled" ou "On"**

5. **Salve (geralmente F10) e saia**

6. **Windows vai reiniciar**

---

## 💾 Restaurar Driver do Fabricante

Se o touchpad aparecer mas não funciona:

### Dell
1. Acesse: **dell.com/support**
2. Digite seu modelo (Service Tag ou Product)
3. Baixe "Touchpad Driver" ou "HID Driver"
4. Execute o instalador
5. Reinicie

### HP
1. Acesse: **hp.com/support**
2. Digite seu modelo ou serial
3. Procure por "Touchpad" ou "Pointing Device Driver"
4. Baixe e instale
5. Reinicie

### Lenovo
1. Acesse: **support.lenovo.com**
2. Digite seu modelo
3. Procure por "Synaptics Driver" ou "Touchpad"
4. Baixe e instale
5. Reinicie

### Asus
1. Acesse: **asus.com/support**
2. Digite seu modelo
3. Procure por "ELAN Touchpad Driver" ou "Pointing Device"
4. Baixe e instale
5. Reinicie

### Acer
1. Acesse: **acer.com/support**
2. Digite seu modelo
3. Procure por "Touchpad Driver"
4. Baixe e instale
5. Reinicie

---

## 🚨 Se NADA Funcionar

### Última Opção: Redefinir Windows

```powershell
# Como ADMIN
Reset-ComputerMachinePassword
```

Ou manualmente:

1. Windows + I → **Configurações**
2. **Sistema** → **Recuperação**
3. Clique em **"Redefinir este PC"**
4. Escolha **"Manter meus arquivos"**
5. Espere reinstalar Windows
6. Drivers novos vão ser instalados

---

## 📞 Checklist de Soluções

- [ ] Executou comando PowerShell acima?
- [ ] Reiniciou depois?
- [ ] Verificou Gerenciador de Dispositivos?
- [ ] Procurou por "Hidden devices"?
- [ ] Tentou habilitar na BIOS?
- [ ] Baixou driver do fabricante?
- [ ] Reinstalou o driver?

Se marcou TODAS e não funcionou:

**Pode ser problema de HARDWARE**
- Touchpad fisicamente desligado
- Cabo desconectado
- Touchpad com defeito

👉 **Procure um técnico autorizado do fabricante**

---

## ⚡ Resumo Rápido

| Passo | Ação | Tempo |
|-------|------|-------|
| 1 | PowerShell command | 1 min |
| 2 | Reiniciar | 2 min |
| 3 | Testar | 1 min |
| ✅ | Pronto! | 4 min |

Se não funcionar em 4 minutos:
- Método Manual (5 min)
- Driver do Fabricante (10 min)
- Redefinir Windows (30 min)

---

## 🎁 Bônus: Desabilitar/Abilitar Touchpad

Se o touchpad atrapalha quando está digitando:

```powershell
# Desabilitar
Get-PnpDevice -PresentOnly | Where-Object { 
    $_.Name -match 'touch|pad' 
} | ForEach-Object {
    Disable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false
}

# Habilitar
Get-PnpDevice -PresentOnly | Where-Object { 
    $_.Name -match 'touch|pad' 
} | ForEach-Object {
    Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false
}
```

---

**Boa sorte! 🚀**

Se funcionar, aproveite seu notebook otimizado!
