#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Mousepad/Touchpad - Diagnóstico e Reparo Completo
Script especializado para reabilitar periféricos de entrada desabilitados
"""

import subprocess
import ctypes
import time
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def print(text, color):
        print(f"{color}{text}{Colors.END}")


class MousepadFixer:
    def __init__(self):
        self.is_admin = self._check_admin()

    def _check_admin(self):
        try:
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False

    def print_header(self):
        print("\n" + "="*80)
        Colors.print("🖱️  MOUSEPAD/TOUCHPAD - DIAGNÓSTICO E REPARO", Colors.BOLD + Colors.CYAN)
        print("="*80)

        if not self.is_admin:
            Colors.print("\n⚠️  EXECUTE COMO ADMINISTRADOR!", Colors.RED + Colors.BOLD)
            print("   Windows + X → Windows PowerShell (Admin)")
            print("   Depois execute: python fix_mousepad.py\n")
            return False
        else:
            Colors.print("✓ Executando com privilégios de ADMIN", Colors.GREEN)
            return True

    def diagnose(self):
        """Diagnóstico completo"""
        print("\n" + "-"*80)
        print("📊 DIAGNÓSTICO DE DISPOSITIVOS DE ENTRADA")
        print("-"*80)

        # Lista todos os dispositivos
        print("\n🔍 Procurando dispositivos...")
        cmd = """
        Get-PnpDevice -PresentOnly | Where-Object {
            $_.Name -match 'touch|pad|synaptics|elan|mouse|input|device'
        } | Select-Object Name, Status, ClassGuid | Format-Table -AutoSize
        """

        result = subprocess.run(
            f'powershell -Command "{cmd}"',
            shell=True,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print("Erros:", result.stderr)

        # Detalhes específicos
        print("\n📋 DISPOSITIVOS DESABILITADOS:")
        cmd_disabled = """
        Get-PnpDevice -PresentOnly | Where-Object {
            $_.Status -eq 'Error' -or $_.Status -eq 'Unknown'
        } | Select-Object Name, Status, InstanceId
        """

        result = subprocess.run(
            f'powershell -Command "{cmd_disabled}"',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            print(result.stdout)
        else:
            Colors.print("✓ Nenhum dispositivo com erro encontrado", Colors.GREEN)

    def enable_devices(self):
        """Habilita dispositivos desabilitados"""
        print("\n" + "-"*80)
        print("🔧 HABILITANDO DISPOSITIVOS DE ENTRADA")
        print("-"*80)

        # Estratégia 1: Habilitar via PnP Device
        print("\n[1/5] Tentando habilitar via PnP Devices...")
        cmd = """
        $devices = Get-PnpDevice -PresentOnly | Where-Object {
            $_.Status -eq 'Error' -or $_.Status -eq 'Unknown'
        }
        foreach ($device in $devices) {
            Write-Host "   Habilitando: $($device.Name)"
            Enable-PnpDevice -InstanceId $device.InstanceId -Confirm:$false
            Start-Sleep -Milliseconds 500
        }
        """

        subprocess.run(
            f'powershell -Command "{cmd}"',
            shell=True,
            capture_output=True
        )
        Colors.print("✓ Tentativa 1 concluída", Colors.GREEN)

        # Estratégia 2: Habilitar Synaptics/ELAN especificamente
        print("\n[2/5] Procurando Synaptics/ELAN Touchpad...")
        cmd = """
        $touchpad = Get-PnpDevice -PresentOnly | Where-Object {
            $_.Name -match 'Synaptics|ELAN|Touchpad|Trackpad'
        }
        if ($touchpad) {
            foreach ($tp in $touchpad) {
                Write-Host "   Encontrado: $($tp.Name) - Status: $($tp.Status)"
                Enable-PnpDevice -InstanceId $tp.InstanceId -Confirm:$false
                Start-Sleep -Milliseconds 500
            }
        } else {
            Write-Host "   Nenhum Synaptics/ELAN encontrado"
        }
        """

        result = subprocess.run(
            f'powershell -Command "{cmd}"',
            shell=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        Colors.print("✓ Tentativa 2 concluída", Colors.GREEN)

        # Estratégia 3: Habilitar Mouse/Pointing Device
        print("\n[3/5] Habilitando Mouse and Pointing Devices...")
        cmd = """
        $devices = Get-PnpDevice -PresentOnly | Where-Object {
            $_.Class -eq 'Mouse' -or $_.Class -eq 'HIDClass'
        }
        foreach ($device in $devices) {
            if ($device.Status -ne 'OK') {
                Write-Host "   Habilitando: $($device.Name)"
                Enable-PnpDevice -InstanceId $device.InstanceId -Confirm:$false
                Start-Sleep -Milliseconds 500
            }
        }
        """

        subprocess.run(
            f'powershell -Command "{cmd}"',
            shell=True,
            capture_output=True
        )
        Colors.print("✓ Tentativa 3 concluída", Colors.GREEN)

        # Estratégia 4: Reiniciar serviços de entrada
        print("\n[4/5] Reiniciando serviços de entrada...")
        services = [
            "hidserv",
            "HidBatt",
            "mouclass",
            "kbdclass"
        ]

        for service in services:
            cmd = f"""
            $service = Get-Service -Name '{service}' -ErrorAction SilentlyContinue
            if ($service) {{
                Write-Host "   Reiniciando: {service}"
                Stop-Service -Name '{service}' -Force -ErrorAction SilentlyContinue
                Start-Sleep -Milliseconds 300
                Start-Service -Name '{service}' -ErrorAction SilentlyContinue
            }}
            """

            subprocess.run(
                f'powershell -Command "{cmd}"',
                shell=True,
                capture_output=True
            )

        Colors.print("✓ Tentativa 4 concluída", Colors.GREEN)

        # Estratégia 5: Update drivers
        print("\n[5/5] Atualizando drivers...")
        cmd = """
        Get-PnpDevice -PresentOnly | Where-Object {
            $_.Name -match 'touch|pad|mouse|input'
        } | ForEach-Object {
            Write-Host "   Atualizando: $($_.Name)"
            pnputil /scan-devices
        }
        """

        subprocess.run(
            f'powershell -Command "{cmd}"',
            shell=True,
            capture_output=True
        )
        Colors.print("✓ Tentativa 5 concluída", Colors.GREEN)

    def restore_services(self):
        """Restaura serviços essenciais"""
        print("\n" + "-"*80)
        print("⚙️  RESTAURANDO SERVIÇOS ESSENCIAIS")
        print("-"*80)

        services = {
            "PlugPlay": "Automático",
            "hidserv": "Automático",
            "DcaSvc": "Manual",
            "Dhcp": "Automático",
            "Dnscache": "Automático",
        }

        for service, status in services.items():
            print(f"\n   {service}...")
            cmd = f"""
            Set-Service -Name '{service}' -StartupType {status} -ErrorAction SilentlyContinue
            Start-Service -Name '{service}' -ErrorAction SilentlyContinue
            """

            result = subprocess.run(
                f'powershell -Command "{cmd}"',
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                Colors.print(f"   ✓ {service} → {status}", Colors.GREEN)
            else:
                Colors.print(f"   ✗ Erro em {service}", Colors.RED)

    def manual_instructions(self):
        """Instruções manuais"""
        print("\n" + "="*80)
        print("📖 INSTRUÇÕES MANUAIS (Se o script não funcionar)")
        print("="*80)

        instructions = """
🖱️ OPÇÃO 1: Via Gerenciador de Dispositivos
   1. Pressione Windows + X
   2. Clique em "Gerenciador de Dispositivos"
   3. Procure por "Mouse and other pointing devices"
   4. Procure por "Touchpad", "Synaptics" ou "ELAN"
   5. Se tiver ⚠️ amarelo: Clique direito → "Habilitar dispositivo"
   6. Se não aparecer: Clique em "Exibir" → "Mostrar dispositivos ocultos"
   7. Reinicie o Windows

🖱️ OPÇÃO 2: Via PowerShell (Copiar e colar)
   (Execute como ADMIN)

   # Habilitar todos os dispositivos desabilitados
   Get-PnpDevice -PresentOnly | Where-Object {
       $_.Status -eq 'Error'
   } | ForEach-Object {
       Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false
   }

   # Reiniciar services
   Stop-Service -Name "hidserv" -Force
   Start-Service -Name "hidserv"

🖱️ OPÇÃO 3: Restaurar Driver do Fabricante
   1. Vá ao site do fabricante do notebook (Dell, HP, Lenovo, Asus, etc)
   2. Procure por "Drivers" ou "Support"
   3. Busque por seu modelo de notebook
   4. Baixe "Touchpad Driver" ou "HID Driver"
   5. Execute o instalador
   6. Reinicie o Windows

🖱️ OPÇÃO 4: Restaurar Windows
   Última opção se nada funcionar:
   1. Windows + I → Recuperação
   2. Clique em "Redefinir este PC"
   3. Escolha "Manter meus arquivos"
   4. Espere reinstalar Windows
"""

        print(instructions)

    def test_mousepad(self):
        """Testa se o mousepad funciona"""
        print("\n" + "-"*80)
        print("🧪 TESTANDO MOUSEPAD")
        print("-"*80)

        print("\n   Tocando no touchpad...")
        print("   Se o cursor se mover, o mousepad está FUNCIONANDO!")
        print("   Aguarde 10 segundos...\n")

        for i in range(10, 0, -1):
            print(f"   Contagem regressiva: {i}s", end="\r")
            time.sleep(1)

        print("\n   ✓ Teste concluído")

    def final_status(self):
        """Status final"""
        print("\n" + "-"*80)
        print("✅ STATUS FINAL")
        print("-"*80)

        cmd = """
        $touchpad = Get-PnpDevice -PresentOnly | Where-Object {
            $_.Name -match 'touch|pad|synaptics|elan' -and $_.Status -eq 'OK'
        }
        if ($touchpad) {
            Write-Host "✓ Touchpad HABILITADO:" -ForegroundColor Green
            $touchpad | Select-Object Name | Format-Table
        } else {
            Write-Host "⚠ Touchpad NÃO encontrado como OK" -ForegroundColor Yellow
        }
        """

        subprocess.run(
            f'powershell -Command "{cmd}"',
            shell=True,
            capture_output=True
        )

    def run(self):
        """Executa o reparo completo"""
        if not self.print_header():
            print("\n⚠️  Abra PowerShell como ADMINISTRADOR e tente novamente\n")
            input("Pressione ENTER para sair...")
            return

        # Menu
        print("\n" + "="*80)
        print("🎯 O QUE VOCÊ QUER FAZER?\n")
        print("   1 - Diagnóstico completo")
        print("   2 - Reparar mousepad (automático)")
        print("   3 - Restaurar serviços")
        print("   4 - Ver instruções manuais")
        print("   5 - Fazer TUDO (1+2+3)")
        print("   0 - Sair")
        print("="*80)

        choice = input("\n👉 Escolha: ").strip()

        if choice == "1":
            self.diagnose()
        elif choice == "2":
            self.enable_devices()
            self.test_mousepad()
            self.final_status()
        elif choice == "3":
            self.restore_services()
        elif choice == "4":
            self.manual_instructions()
        elif choice == "5":
            self.diagnose()
            time.sleep(2)
            self.enable_devices()
            time.sleep(2)
            self.restore_services()
            time.sleep(2)
            self.test_mousepad()
            self.final_status()
        elif choice == "0":
            print("\n👋 Saindo...")
            return

        print("\n" + "="*80)
        print("📝 PRÓXIMOS PASSOS:")
        print("="*80)
        print("""
   1. Teste o mousepad/touchpad
   2. Se não funcionar, siga as instruções manuais
   3. Se ainda não funcionar, reinstale driver do fabricante
   4. Última opção: Redefinir Windows (Recuperação)

   📧 Se persistir problema:
      - Leve a um técnico (pode ser HW problem)
      - Ou procure suporte do fabricante do notebook
""")

        print("\n" + "="*80)
        Colors.print("✨ Script concluído!", Colors.GREEN + Colors.BOLD)
        print("="*80 + "\n")

        input("Pressione ENTER para sair...")


def main():
    print("\n" + "="*80)
    Colors.print("🖱️  FIX MOUSEPAD - Reparo Completo de Touchpad/Mouse", Colors.BOLD + Colors.CYAN)
    print("="*80)

    fixer = MousepadFixer()
    fixer.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido")
    except Exception as e:
        Colors.print(f"\n❌ Erro: {e}", Colors.RED)
