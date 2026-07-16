#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Service Manager
Gerenciador seguro de serviços do Windows para otimização
"""

import subprocess
import sys
import ctypes
from pathlib import Path
from datetime import datetime


class ServiceManager:
    """Gerenciar serviços do Windows com segurança"""

    # Serviços essenciais que NUNCA devem ser desligados
    ESSENTIAL_SERVICES = {
        "PlugPlay": ("Plug and Play", "Automático"),
        "hidserv": ("Human Interface Device Access", "Automático"),
        "DcaSvc": ("Device Setup Manager", "Manual"),
        "Dhcp": ("DHCP Client", "Automático"),
        "Dnscache": ("DNS Client", "Automático"),
        "nsi": ("Network Store Interface Service", "Automático"),
        "AudioEndpointBuilder": ("Windows Audio Endpoint Builder", "Automático"),
        "Audiosrv": ("Windows Audio", "Automático"),
        "lmhosts": ("TCP/IP NetBIOS Helper", "Manual"),
    }

    # Serviços seguros para desligar (usam muita memória)
    SAFE_TO_DISABLE = {
        "OneDrive": ("OneDrive", "Automático" if Path("C:\\Windows.old").exists() else "Manual"),
        "Connected User Experiences": ("Connected User Experiences and Telemetry", "Manual"),
        "DiagTrack": ("DiagTrack", "Disabled"),
        "dmwappushservice": ("dmwappushservice", "Disabled"),
        "WSearch": ("Windows Search", "Disabled"),
        "SysMainSvc": ("Superfetch", "Disabled"),
        "TermService": ("Remote Desktop Services", "Disabled"),
        "RemoteRegistry": ("Remote Registry", "Disabled"),
        "TmNavigator": ("File Server Resource Manager", "Disabled"),
        "XblAuthManager": ("Xbox Live Auth Manager", "Disabled"),
        "XboxNetApiSvc": ("Xbox Live Networking Service", "Disabled"),
        "sppsvc": ("Software Protection", "Manual"),
        "PrintSpooler": ("Print Spooler", "Disabled" if not Path("C:\\Windows\\System32\\spool\\PRINTERS").exists() else "Automatic"),
    }

    def __init__(self):
        self.is_admin = self._check_admin()
        self.log_file = Path("service_manager_log.txt")
        self.log("=" * 80)
        self.log("WINDOWS SERVICE MANAGER")
        self.log("=" * 80)

    def _check_admin(self):
        """Verifica privilégios de administrador"""
        try:
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False

    def log(self, msg):
        """Registra mensagens"""
        print(msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    def run_powershell(self, command):
        """Executa comando PowerShell"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip(), result.returncode
        except Exception as e:
            return str(e), 1

    def get_service_status(self, service_name):
        """Obtém status de um serviço"""
        cmd = f"Get-Service -Name '{service_name}' -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType"
        output, code = self.run_powershell(cmd)
        return output if code == 0 else None

    def set_service_status(self, service_name, start_type, start=True):
        """Muda status de um serviço"""
        if not self.is_admin:
            self.log(f"⚠️  Privilégios de admin necessários para {service_name}")
            return False

        try:
            # Set startup type
            cmd = f"Set-Service -Name '{service_name}' -StartupType {start_type} -ErrorAction SilentlyContinue"
            self.run_powershell(cmd)

            # Start service if requested
            if start and start_type != "Disabled":
                cmd = f"Start-Service -Name '{service_name}' -ErrorAction SilentlyContinue"
                self.run_powershell(cmd)

            self.log(f"   ✓ {service_name}: {start_type}")
            return True
        except Exception as e:
            self.log(f"   ✗ Erro com {service_name}: {e}")
            return False

    def check_essential_services(self):
        """Verifica serviços essenciais"""
        self.log("\n🔍 VERIFICANDO SERVIÇOS ESSENCIAIS...")
        self.log("-" * 80)

        all_ok = True
        for service_code, (service_name, expected_status) in self.ESSENTIAL_SERVICES.items():
            status = self.get_service_status(service_code)

            if status:
                if "Running" in status or "Automatic" in status or "Manual" in status:
                    self.log(f"   ✓ {service_name}")
                else:
                    self.log(f"   ⚠️  {service_name} - DESABILITADO! Ativando...")
                    self.set_service_status(service_code, "Automatic", True)
                    all_ok = False
            else:
                self.log(f"   ? {service_name} - Não encontrado")

        if all_ok:
            self.log("\n✅ Todos os serviços essenciais estão OK!")
        else:
            self.log("\n⚠️  Alguns serviços foram reabilitados - REINICIE O WINDOWS!")

        return all_ok

    def setup_recommended_optimizations(self):
        """Configura otimizações recomendadas"""
        self.log("\n⚙️  CONFIGURANDO OTIMIZAÇÕES...")
        self.log("-" * 80)

        if not self.is_admin:
            self.log("❌ Privilégios de administrador necessários!")
            return

        count = 0
        for service_code, (service_name, status) in self.SAFE_TO_DISABLE.items():
            if status == "Disabled":
                self.set_service_status(service_code, "Disabled", False)
                count += 1

        self.log(f"\n✓ {count} serviços foram otimizados (desabilitados)")
        self.log("\n⚠️  REINICIE O WINDOWS para aplicar as mudanças!")

    def show_service_list(self):
        """Mostra lista de serviços"""
        self.log("\n📋 SERVIÇOS ESSENCIAIS")
        self.log("-" * 80)
        for service_code, (service_name, status) in self.ESSENTIAL_SERVICES.items():
            self.log(f"   • {service_name:<45} [{status}]")

        self.log("\n📋 SERVIÇOS SEGUROS PARA DESABILITAR")
        self.log("-" * 80)
        for service_code, (service_name, status) in self.SAFE_TO_DISABLE.items():
            self.log(f"   • {service_name:<45} [{status}]")

    def interactive_menu(self):
        """Menu interativo"""
        self.log("\n" + "=" * 80)
        self.log("OPÇÕES:")
        self.log("=" * 80)
        self.log("1. Verificar serviços essenciais")
        self.log("2. Aplicar otimizações recomendadas")
        self.log("3. Ver lista de serviços")
        self.log("4. Reabilitar todos os serviços")
        self.log("5. Sair")
        self.log("=" * 80)

        choice = input("\nEscolha uma opção (1-5): ").strip()

        if choice == "1":
            self.check_essential_services()
        elif choice == "2":
            confirm = input("\n⚠️  Isso pode desabilitar alguns serviços! Continuar? (S/N): ")
            if confirm.lower() == 's':
                self.setup_recommended_optimizations()
        elif choice == "3":
            self.show_service_list()
        elif choice == "4":
            confirm = input("\n⚠️  Isso reabilitará TODOS os serviços! Continuar? (S/N): ")
            if confirm.lower() == 's':
                self.revert_all_optimizations()
        elif choice == "5":
            self.log("\n👋 Saindo...")
            return False

        return True

    def revert_all_optimizations(self):
        """Desfaz todas as otimizações"""
        self.log("\n↩️  REVERTENDO OTIMIZAÇÕES...")
        self.log("-" * 80)

        if not self.is_admin:
            self.log("❌ Privilégios de administrador necessários!")
            return

        # Reabilita serviços essenciais
        for service_code, (service_name, status) in self.ESSENTIAL_SERVICES.items():
            self.set_service_status(service_code, status, True)

        # Reabilita serviços que foram desabilitados
        for service_code, (service_name, status) in self.SAFE_TO_DISABLE.items():
            if status == "Automatic" or status == "Manual":
                self.set_service_status(service_code, status, True)

        self.log("\n✓ Todos os serviços foram restaurados!")
        self.log("⚠️  REINICIE O WINDOWS!")

    def run(self):
        """Loop principal"""
        self.log(f"\n{'Admin' if self.is_admin else 'Usuário normal'} | {datetime.now()}\n")

        if not self.is_admin:
            self.log("⚠️  AVISO: Este programa deve ser executado como ADMINISTRADOR")
            self.log("   Para máxima funcionalidade, abra como Admin (Windows + X → Windows PowerShell Admin)\n")

        while True:
            try:
                if not self.interactive_menu():
                    break
                print("\n" + "-" * 80)
            except KeyboardInterrupt:
                self.log("\n\n👋 Programa interrompido pelo usuário")
                break
            except Exception as e:
                self.log(f"\n❌ Erro: {e}")


def main():
    """Função principal"""
    print("\n" + "=" * 80)
    print("🔧 GERENCIADOR DE SERVIÇOS DO WINDOWS")
    print("=" * 80)
    print("\nEste programa ajuda a:")
    print("  • Verificar se serviços críticos estão ativados")
    print("  • Desabilitar serviços que consomem muita memória")
    print("  • Reabilitar serviços se algo parar de funcionar")
    print("\n" + "=" * 80)

    manager = ServiceManager()
    manager.run()

    print("\n" + "=" * 80)
    print(f"📝 Log salvo em: {manager.log_file}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        import subprocess
    except ImportError:
        print("❌ Erro: subprocess não disponível")
        sys.exit(1)

    main()
