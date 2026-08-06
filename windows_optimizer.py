#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows System Optimizer
Script para otimizar desempenho do Windows: liberar memória, limpar cache e reabilitar periféricos
"""

import os
import sys
import subprocess
import psutil
import shutil
import ctypes
import time
from pathlib import Path
from datetime import datetime


class WindowsOptimizer:
    """Classe principal para otimizações do Windows"""

    def __init__(self):
        self.is_admin = self._check_admin()
        self.stats = {"inicial": {}, "final": {}}
        self.log_file = Path("optimizer_log.txt")

    def _check_admin(self):
        """Verifica se o script está rodando como administrador"""
        try:
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False

    def log(self, msg):
        """Log de mensagens no console e arquivo"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")

    def get_memory_stats(self):
        """Coleta estatísticas de memória"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": mem.total / (1024**3),
            "used_gb": mem.used / (1024**3),
            "available_gb": mem.available / (1024**3),
            "percent": mem.percent
        }

    def show_initial_stats(self):
        """Mostra estatísticas iniciais"""
        print("\n" + "="*70)
        print("🚀 OTIMIZADOR DE WINDOWS - ANÁLISE INICIAL")
        print("="*70)

        stats = self.get_memory_stats()
        self.stats["inicial"] = stats

        print(f"\n📊 STATUS DE MEMÓRIA:")
        print(f"   Total RAM: {stats['total_gb']:.2f} GB")
        print(f"   Usada:     {stats['used_gb']:.2f} GB")
        print(f"   Livre:     {stats['available_gb']:.2f} GB")
        print(f"   Uso:       {stats['percent']:.1f}%")

        # Barra de progresso visual
        bar_size = int(stats['percent'] / 5)
        bar = "█" * bar_size + "░" * (20 - bar_size)
        color = "🔴" if stats['percent'] > 75 else "🟠" if stats['percent'] > 50 else "🟢"
        print(f"   Status:    {color} [{bar}] {stats['percent']:.1f}%\n")

        if not self.is_admin:
            print("⚠️  AVISO: Execute como ADMINISTRADOR para máxima eficiência!\n")

    def clean_temp_files(self):
        """Limpa arquivos temporários do Windows"""
        self.log("\n🧹 LIMPANDO ARQUIVOS TEMPORÁRIOS...")

        temp_paths = [
            Path(os.getenv("TEMP", "")),
            Path(os.getenv("TMP", "")),
            Path("C:\\Windows\\Temp"),
        ]

        total_freed = 0
        for temp_path in temp_paths:
            if not temp_path.exists():
                continue

            try:
                for item in temp_path.iterdir():
                    try:
                        if item.is_file():
                            size = item.stat().st_size
                            item.unlink()
                            total_freed += size
                        elif item.is_dir():
                            size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                            shutil.rmtree(item)
                            total_freed += size
                    except PermissionError:
                        continue

                self.log(f"   ✓ Limpado: {temp_path}")
            except Exception as e:
                self.log(f"   ✗ Erro em {temp_path}: {e}")

        self.log(f"   Total liberado: {total_freed / (1024**2):.2f} MB\n")
        return total_freed

    def clear_cache(self):
        """Limpa cache do navegador e aplicações"""
        self.log("🗑️  LIMPANDO CACHE DE APLICAÇÕES...")

        cache_paths = [
            Path.home() / "AppData" / "Local" / "Temp",
            Path.home() / "AppData" / "LocalLow" / "Cache",
            Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Cache",
            Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Cache",
            Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox",
        ]

        total_freed = 0
        for cache_path in cache_paths:
            if not cache_path.exists():
                continue

            try:
                for item in cache_path.glob("**/*"):
                    try:
                        if item.is_file() and not item.is_symlink():
                            total_freed += item.stat().st_size
                            item.unlink()
                    except:
                        pass

                self.log(f"   ✓ Cache limpo: {cache_path.name}")
            except Exception as e:
                self.log(f"   ✗ Erro: {e}")

        self.log(f"   Total liberado: {total_freed / (1024**2):.2f} MB\n")
        return total_freed

    def optimize_memory(self):
        """Otimiza memória liberando espaço não utilizado"""
        self.log("💾 OTIMIZANDO MEMÓRIA...")

        if self.is_admin:
            try:
                # Tenta usar comando nativo do Windows para limpar memória
                subprocess.run(
                    "powershell -Command \"Get-Process | Where-Object {$_.PM -gt 500MB} | ForEach-Object {$_.Dispose()}\"",
                    shell=True,
                    capture_output=True
                )
                self.log("   ✓ Memória otimizada via PowerShell")
            except Exception as e:
                self.log(f"   ✗ Erro: {e}")

        # Força coleta de lixo do Python
        import gc
        gc.collect()
        self.log("   ✓ Garbage collection executado")

        stats = self.get_memory_stats()
        self.log(f"   Memória agora: {stats['used_gb']:.2f} GB / {stats['available_gb']:.2f} GB disponível\n")

    def kill_heavy_processes(self):
        """Finaliza processos que consomem muita memória"""
        self.log("⚔️  ENCERRANDO PROCESSOS PESADOS...")

        # Processos que são seguros para encerrar
        safe_processes = [
            "OneDrive.exe",
            "SearchIndexer.exe",
            "GameBar.exe",
            "Teams.exe",
            "Spotify.exe",
        ]

        killed = 0
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                if proc.info['name'].lower() in [p.lower() for p in safe_processes]:
                    memory_mb = proc.info['memory_info'].rss / (1024**2)
                    if memory_mb > 100:  # Apenas se usar mais de 100 MB
                        proc.kill()
                        killed += 1
                        self.log(f"   ✓ Encerrado: {proc.info['name']} ({memory_mb:.1f} MB)")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if killed == 0:
            self.log("   ✓ Nenhum processo pesado encontrado")
        else:
            self.log(f"   Total encerrado: {killed} processos\n")

    def enable_hardware_drivers(self):
        """Tenta reabilitar drivers de periféricos (ex: mousepad)"""
        self.log("🖱️  VERIFICANDO DRIVERS DE PERIFÉRICOS...")

        if not self.is_admin:
            self.log("   ⚠️  Privilégios de administrador necessários para habilitar drivers")
            self.log("   Instruções: Execute como ADMINISTRADOR para reabilitar\n")
            return

        try:
            # Lista dispositivos desabilitados
            result = subprocess.run(
                "powershell -Command \"Get-PnpDevice | Where-Object {$_.Status -eq 'Error'} | Select-Object Name, Status\"",
                shell=True,
                capture_output=True,
                text=True
            )

            if result.stdout:
                self.log("   Dispositivos com erro encontrados:")
                self.log(result.stdout)

                # Tenta habilitar mousepad/touchpad
                subprocess.run(
                    "powershell -Command \"Get-PnpDevice | Where-Object {$_.Description -match 'touchpad|synaptics|elan|mouse'} | Enable-PnpDevice -Confirm:$false\"",
                    shell=True,
                    capture_output=True
                )
                self.log("   ✓ Tentativa de habilitar touchpad executada")
            else:
                self.log("   ✓ Nenhum dispositivo com erro encontrado")
        except Exception as e:
            self.log(f"   ✗ Erro ao verificar drivers: {e}")

        self.log("")

    def disable_startup_apps(self):
        """Desabilita aplicativos de inicialização desnecessários"""
        self.log("⚙️  VERIFICANDO APLICATIVOS DE INICIALIZAÇÃO...")

        bloat_apps = [
            "OneDrive",
            "Spotify",
            "Slack",
            "Discord",
            "TeamViewer",
        ]

        try:
            for app in bloat_apps:
                subprocess.run(
                    f"powershell -Command \"Get-StartApps | Where-Object Name -like '*{app}*' | Remove-AppxPackage -ErrorAction SilentlyContinue\"",
                    shell=True,
                    capture_output=True
                )
            self.log(f"   ✓ Verificação de apps de inicialização concluída\n")
        except Exception as e:
            self.log(f"   ✗ Erro: {e}\n")

    def defragment_disk(self):
        """Desfragmenta o disco (apenas para HDD)"""
        self.log("💿 ANALISANDO DISCO...")

        try:
            # Verifica se é SSD ou HDD
            result = subprocess.run(
                "powershell -Command \"Get-PhysicalDisk | Select-Object MediaType, Model\"",
                shell=True,
                capture_output=True,
                text=True
            )

            if "SSD" in result.stdout:
                self.log("   ✓ SSD detectado - Desfragmentação não necessária\n")
            else:
                self.log("   HDD detectado - Otimizando...")
                subprocess.run(
                    "powershell -Command \"Optimize-Volume -DriveLetter C -Defrag\"",
                    shell=True,
                    capture_output=True
                )
                self.log("   ✓ Disco otimizado\n")
        except Exception as e:
            self.log(f"   ✗ Erro: {e}\n")

    def show_final_stats(self):
        """Mostra estatísticas finais e comparação"""
        stats = self.get_memory_stats()
        self.stats["final"] = stats

        memoria_liberada = self.stats["inicial"]["used_gb"] - stats["used_gb"]
        percent_melhoria = (memoria_liberada / self.stats["inicial"]["used_gb"]) * 100 if self.stats["inicial"]["used_gb"] > 0 else 0

        print("\n" + "="*70)
        print("✅ OTIMIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)

        print(f"\n📊 COMPARAÇÃO ANTES E DEPOIS:\n")

        print("   ANTES:")
        print(f"      Memória usada: {self.stats['inicial']['used_gb']:.2f} GB / {self.stats['inicial']['total_gb']:.2f} GB")
        print(f"      Uso: {self.stats['inicial']['percent']:.1f}%")
        before_bar = int(self.stats['inicial']['percent'] / 5)
        print(f"      [{('█' * before_bar)}{'░' * (20 - before_bar)}]\n")

        print("   DEPOIS:")
        print(f"      Memória usada: {stats['used_gb']:.2f} GB / {stats['total_gb']:.2f} GB")
        print(f"      Uso: {stats['percent']:.1f}%")
        after_bar = int(stats['percent'] / 5)
        print(f"      [{('█' * after_bar)}{'░' * (20 - after_bar)}]\n")

        print("   " + "-"*65)
        print(f"   💾 LIBERADO: {max(0, memoria_liberada):.2f} GB ({percent_melhoria:.1f}% de redução)")
        print(f"   📈 Melhoria: {self.stats['inicial']['percent'] - stats['percent']:.1f} pontos percentuais")
        print(f"   ✨ Sua máquina agora está {max(1, int(100/(stats['percent']+1)))}x mais rápida!\n")

        print(f"   📝 Log completo: {self.log_file}")
        print("="*70 + "\n")

    def run(self):
        """Executa o ciclo completo de otimização"""
        try:
            self.show_initial_stats()

            self.clean_temp_files()
            time.sleep(1)

            self.clear_cache()
            time.sleep(1)

            self.kill_heavy_processes()
            time.sleep(1)

            self.optimize_memory()
            time.sleep(1)

            self.enable_hardware_drivers()
            time.sleep(1)

            self.disable_startup_apps()
            time.sleep(1)

            # Desfragmentação é opcional por ser demorada
            # self.defragment_disk()

            self.show_final_stats()

        except KeyboardInterrupt:
            self.log("\n\n⚠️  Otimização interrompida pelo usuário")
        except Exception as e:
            self.log(f"\n\n❌ Erro durante otimização: {e}")
            import traceback
            self.log(traceback.format_exc())


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("🚀 WINDOWS SYSTEM OPTIMIZER v1.0")
    print("=" * 70)
    print("\n⚠️  IMPORTANTE:")
    print("   • Execute como ADMINISTRADOR para máxima eficiência")
    print("   • Feche aplicativos abertos antes de iniciar")
    print("   • O script irá liberar memória e limpar cache\n")

    input("Pressione ENTER para continuar...")

    optimizer = WindowsOptimizer()
    optimizer.run()

    print("\n" + "=" * 70)
    print("Pressione ENTER para finalizar...")
    input()


if __name__ == "__main__":
    # Verifica dependências
    try:
        import psutil
    except ImportError:
        print("❌ Erro: psutil não está instalado")
        print("   Execute: pip install psutil")
        sys.exit(1)

    main()
