#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Cleaner PRO - Premium Windows Cleaning Tool
Com feedback visual, barras de progresso e análises detalhadas
"""

import os
import sys
import shutil
import subprocess
import ctypes
import hashlib
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json


class Colors:
    """Códigos de cor ANSI"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

    @staticmethod
    def format(text, color):
        return f"{color}{text}{Colors.END}"


class ProgressBar:
    """Barra de progresso visual com ETA"""
    def __init__(self, total, desc="Processando"):
        self.total = max(total, 1)
        self.current = 0
        self.desc = desc
        self.start_time = time.time()

    def update(self, amount=1):
        self.current = min(self.current + amount, self.total)
        self._show()

    def _show(self):
        percent = self.current / self.total
        filled = int(30 * percent)
        bar = "█" * filled + "░" * (30 - filled)
        elapsed = time.time() - self.start_time

        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
        else:
            eta = 0

        status = f"{self.current}/{self.total}" if self.total > 1 else "✓"
        time_str = f"{eta:.0f}s" if eta > 0 else "..."

        sys.stdout.write(f"\r{self.desc}: [{bar}] {percent*100:3.0f}% | {status} | ETA: {time_str}")
        sys.stdout.flush()

    def finish(self, msg="Concluído"):
        elapsed = time.time() - self.start_time
        sys.stdout.write(f"\r{self.desc}: [{'█'*30}] 100% | {self.total}/{self.total} | {msg} em {elapsed:.1f}s\n")
        sys.stdout.flush()


class SystemCleanerPro:
    """Ferramenta profissional de limpeza do Windows"""

    def __init__(self):
        self.is_admin = self._check_admin()
        self.log_file = Path("cleaner_pro_log.txt")
        self.report_file = Path("cleaner_pro_report.txt")
        self.stats = {
            "tarefas": {},
            "inicio": datetime.now(),
            "fim": None,
            "total_liberado": 0,
            "total_arquivos": 0,
            "duplicatas": 0
        }
        self._initialize_log()
        self._analyze_initial_disk()

    def _check_admin(self):
        """Verifica privilégios de administrador"""
        try:
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False

    def _initialize_log(self):
        """Inicializa arquivo de log"""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"{'='*80}\n")
            f.write(f"SYSTEM CLEANER PRO - {datetime.now()}\n")
            f.write(f"{'='*80}\n\n")

    def _analyze_initial_disk(self):
        """Analisa espaço em disco inicial"""
        print(Colors.format("\n📊 Analisando disco inicial...", Colors.CYAN))
        try:
            import ctypes
            root = Path("C:\\")
            total = ctypes.c_ulonglong(0)
            free = ctypes.c_ulonglong(0)

            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                str(root),
                ctypes.byref(free),
                ctypes.byref(total),
                None
            )

            self.stats["disco_inicial_total"] = total.value
            self.stats["disco_inicial_livre"] = free.value
            self.stats["disco_inicial_usado"] = total.value - free.value

            print(f"   Total: {self.format_bytes(total.value)}")
            print(f"   Usado: {self.format_bytes(total.value - free.value)}")
            print(f"   Livre: {self.format_bytes(free.value)}\n")
        except:
            print("   ⚠️  Não foi possível analisar disco\n")

    def format_bytes(self, size_bytes):
        """Converte bytes para formato legível"""
        if size_bytes == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def log(self, msg):
        """Registra em arquivo de log"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")

    def print_task_header(self, emoji, title):
        """Imprime cabeçalho de tarefa"""
        print(f"\n{Colors.format(f'{emoji} {title}', Colors.BOLD + Colors.CYAN)}")
        print("─" * 60)

    def print_success(self, msg, size=0, count=0):
        """Imprime mensagem de sucesso"""
        if size > 0:
            print(f"{Colors.format('✓', Colors.GREEN)} {msg}: {Colors.format(self.format_bytes(size), Colors.BOLD)} ({count} arquivos)")
        else:
            print(f"{Colors.format('✓', Colors.GREEN)} {msg}")

    def print_warning(self, msg):
        """Imprime aviso"""
        print(f"{Colors.format('⚠', Colors.YELLOW)} {msg}")

    def print_error(self, msg):
        """Imprime erro"""
        print(f"{Colors.format('✗', Colors.RED)} {msg}")

    def show_menu(self):
        """Menu principal interativo"""
        print("\n" + "=" * 80)
        print(Colors.format("🚀 SYSTEM CLEANER PRO v2.0", Colors.BOLD))
        print(Colors.format("Limpeza Profissional do Windows", Colors.DIM))
        print("=" * 80)

        options = [
            ("💾", "Limpar Cache de Aplicações"),
            ("🗑️ ", "Limpar Arquivos Temporários"),
            ("📥", "Limpar Downloads Antigos"),
            ("🔍", "Encontrar Arquivos Duplicados"),
            ("💿", "Análise Completa de Disco"),
            ("🛢️ ", "Limpar Lixeira"),
            ("📋", "Limpar Registro do Windows"),
            ("🌐", "Limpar Cache de Navegadores"),
            ("⚙️ ", "Limpar Cache Windows Update"),
            ("📱", "Limpar Temp do Winget/Chocolatey"),
            ("🖼️ ", "Limpar Miniaturas"),
            ("🔗", "Remover Atalhos Inválidos"),
            ("⚡", "LIMPEZA AUTOMÁTICA COMPLETA"),
            ("0️⃣ ", "Sair"),
        ]

        for i, (emoji, desc) in enumerate(options, 1):
            num = "A" if i == 13 else "0" if i == 14 else str(i)
            print(f"   {num:2s} - {emoji} {desc}")

        print("=" * 80)
        choice = input("\n👉 Escolha uma opção: ").strip().upper()
        return choice

    def clean_app_cache(self):
        """Limpa cache de aplicações"""
        self.print_task_header("💾", "Limpando Cache de Aplicações")

        cache_paths = [
            Path.home() / "AppData" / "Local" / "Temp",
            Path.home() / "AppData" / "LocalLow" / "Cache",
            Path.home() / "AppData" / "Local" / "CrashDumps",
            Path.home() / "AppData" / "Local" / "VirtualStore",
        ]

        total_freed = 0
        count = 0
        deleted_items = 0

        progress = ProgressBar(len(cache_paths), "Escaneando pastas")

        for cache_path in cache_paths:
            progress.update()

            if not cache_path.exists():
                continue

            try:
                for item in cache_path.glob("**/*"):
                    try:
                        if item.is_file() and not item.is_symlink():
                            size = item.stat().st_size
                            item.unlink()
                            total_freed += size
                            count += 1
                            deleted_items += 1
                    except (PermissionError, OSError):
                        pass
            except:
                pass

        progress.finish("Concluído")
        self.print_success("Cache limpo", total_freed, count)
        self.stats["tarefas"]["cache"] = {"size": total_freed, "files": count}
        self.stats["total_liberado"] += total_freed
        self.stats["total_arquivos"] += count
        return total_freed

    def clean_temp_files(self):
        """Limpa arquivos temporários"""
        self.print_task_header("🗑️ ", "Limpando Arquivos Temporários")

        temp_paths = [
            Path(os.getenv("TEMP", "")),
            Path(os.getenv("TMP", "")),
            Path("C:\\Windows\\Temp"),
        ]

        total_freed = 0
        count = 0

        # Conta arquivos primeiro
        total_files = 0
        for temp_path in temp_paths:
            if temp_path.exists():
                for item in temp_path.glob("**/*"):
                    if item.is_file():
                        total_files += 1

        progress = ProgressBar(total_files, "Deletando arquivos")

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
                            count += 1
                            progress.update()
                    except (PermissionError, OSError):
                        pass
            except:
                pass

        progress.finish("Concluído")
        self.print_success("Temp limpo", total_freed, count)
        self.stats["tarefas"]["temp"] = {"size": total_freed, "files": count}
        self.stats["total_liberado"] += total_freed
        self.stats["total_arquivos"] += count
        return total_freed

    def clean_browser_cache(self):
        """Limpa cache de navegadores"""
        self.print_task_header("🌐", "Limpando Cache de Navegadores")

        browsers = {
            "Chrome": Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
            "Edge": Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
        }

        total_freed = 0
        progress = ProgressBar(len(browsers), "Processando navegadores")

        for browser_name, cache_path in browsers.items():
            progress.update()

            if not cache_path.exists():
                self.print_warning(f"{browser_name} não encontrado")
                continue

            try:
                freed = 0
                count = 0
                for file in cache_path.rglob("*"):
                    if file.is_file():
                        try:
                            freed += file.stat().st_size
                            file.unlink()
                            count += 1
                        except:
                            pass

                print(f"   {browser_name}: {Colors.format(self.format_bytes(freed), Colors.GREEN)} ({count} arquivos)")
                total_freed += freed

            except Exception as e:
                self.print_error(f"Erro com {browser_name}: {e}")

        progress.finish("Concluído")
        self.stats["tarefas"]["navegadores"] = {"size": total_freed, "files": 0}
        self.stats["total_liberado"] += total_freed
        return total_freed

    def find_duplicates(self):
        """Encontra arquivos duplicados"""
        self.print_task_header("🔍", "Encontrando Arquivos Duplicados")

        paths_to_scan = [
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.home() / "Pictures",
            Path.home() / "Videos",
        ]

        file_hashes = defaultdict(list)

        # Conta arquivos
        total_files = sum(len(list(p.rglob("*"))) for p in paths_to_scan if p.exists())
        progress = ProgressBar(total_files, "Calculando hashes")

        for scan_path in paths_to_scan:
            if not scan_path.exists():
                continue

            try:
                for file in scan_path.rglob("*"):
                    progress.update()
                    if not file.is_file():
                        continue

                    try:
                        file_hash = self._get_file_hash(file)
                        if file_hash:
                            file_hashes[file_hash].append(file)
                    except:
                        pass
            except:
                pass

        progress.finish("Concluído")

        duplicates = {k: v for k, v in file_hashes.items() if len(v) > 1}

        if not duplicates:
            self.print_warning("Nenhum arquivo duplicado encontrado")
            return

        total_dup_size = 0
        total_dup_count = 0

        print(f"\n{Colors.format('Grupos de duplicatas encontrados:', Colors.BOLD)}\n")

        for idx, (file_hash, files) in enumerate(list(duplicates.items())[:10], 1):
            print(f"   Grupo {idx} ({len(files)} cópias):")
            for i, file in enumerate(files):
                size = file.stat().st_size
                marker = "✓ ORIGINAL" if i == 0 else "↳ DUPLICATA"
                print(f"      {marker}: {file} ({self.format_bytes(size)})")
                if i > 0:
                    total_dup_size += size
                    total_dup_count += 1

        if len(duplicates) > 10:
            print(f"\n   ... e mais {len(duplicates) - 10} grupos")

        print(f"\n{Colors.format(f'Total de duplicatas: {self.format_bytes(total_dup_size)} ({total_dup_count} arquivos)', Colors.BOLD)}")
        self.stats["duplicatas"] = total_dup_count

    def _get_file_hash(self, file_path, chunk_size=8192):
        """Calcula hash MD5"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def empty_recycle_bin(self):
        """Limpa lixeira"""
        self.print_task_header("🛢️ ", "Limpando Lixeira")

        print("   Processando...")
        try:
            subprocess.run(
                "powershell -Command \"Clear-RecycleBin -Force -Confirm:$false\"",
                shell=True,
                capture_output=True,
                timeout=10
            )
            self.print_success("Lixeira limpa com sucesso")
        except Exception as e:
            self.print_error(f"Erro ao limpar lixeira: {e}")

    def analyze_disk(self):
        """Análise de disco"""
        self.print_task_header("💿", "Análise Completa de Disco")

        try:
            import ctypes

            for drive_letter in ['C', 'D', 'E']:
                drive = f"{drive_letter}:\\"
                if not Path(drive).exists():
                    continue

                total = ctypes.c_ulonglong(0)
                free = ctypes.c_ulonglong(0)

                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    drive,
                    ctypes.byref(free),
                    ctypes.byref(total),
                    None
                )

                used = total.value - free.value
                percent = (used / total.value) * 100

                print(f"\n   📍 {drive}")
                print(f"      Total: {self.format_bytes(total.value)}")
                print(f"      Usado: {self.format_bytes(used)} ({percent:.1f}%)")
                print(f"      Livre: {self.format_bytes(free.value)}")

                bar_filled = int(30 * percent / 100)
                bar = "█" * bar_filled + "░" * (30 - bar_filled)
                print(f"      [{bar}]")

        except Exception as e:
            self.print_error(f"Erro ao analisar disco: {e}")

    def show_final_report(self):
        """Mostra relatório final completo"""
        self.stats["fim"] = datetime.now()
        duration = (self.stats["fim"] - self.stats["inicio"]).total_seconds()

        print("\n\n" + "=" * 80)
        print(Colors.format("📊 RELATÓRIO FINAL", Colors.BOLD + Colors.CYAN))
        print("=" * 80)

        print(f"\n{Colors.format('⏱️  Tempo total:', Colors.BOLD)} {duration:.1f} segundos\n")

        print(f"{Colors.format('💾 ESPAÇO LIBERADO:', Colors.BOLD)}")
        print(f"   Total: {Colors.format(self.format_bytes(self.stats['total_liberado']), Colors.GREEN + Colors.BOLD)}")
        print(f"   Arquivos: {Colors.format(str(self.stats['total_arquivos']), Colors.BOLD)}\n")

        if self.stats.get("duplicatas", 0) > 0:
            print(f"{Colors.format('📋 DUPLICATAS ENCONTRADAS:', Colors.BOLD)}")
            print(f"   Arquivos: {Colors.format(str(self.stats['duplicatas']), Colors.BOLD)}\n")

        print(f"{Colors.format('📈 DETALHAMENTO POR TAREFA:', Colors.BOLD)}")
        for task_name, data in self.stats["tarefas"].items():
            if data.get("size", 0) > 0:
                print(f"   • {task_name:.<30} {self.format_bytes(data['size']):>10}")

        # Análise de disco final
        if "disco_inicial_total" in self.stats:
            print(f"\n{Colors.format('💿 ANÁLISE DE DISCO:', Colors.BOLD)}")
            print(f"   Antes: {self.format_bytes(self.stats['disco_inicial_usado'])} usado")
            try:
                import ctypes
                total = ctypes.c_ulonglong(0)
                free = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:\\", ctypes.byref(free), ctypes.byref(total), None)
                usado_agora = total.value - free.value
                print(f"   Depois: {self.format_bytes(usado_agora)} usado")
                print(f"   Melhoria: {Colors.format(self.format_bytes(self.stats['disco_inicial_usado'] - usado_agora), Colors.GREEN)}")
            except:
                pass

        print("\n" + "=" * 80)
        print(Colors.format("✅ LIMPEZA CONCLUÍDA COM SUCESSO!", Colors.GREEN + Colors.BOLD))
        print("=" * 80)

        self._save_report()

    def _save_report(self):
        """Salva relatório em arquivo"""
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(f"SYSTEM CLEANER PRO - Relatório de Limpeza\n")
            f.write(f"{'='*80}\n")
            f.write(f"Data: {self.stats['fim']}\n")
            f.write(f"Duração: {(self.stats['fim'] - self.stats['inicio']).total_seconds():.1f}s\n\n")
            f.write(f"Total liberado: {self.format_bytes(self.stats['total_liberado'])}\n")
            f.write(f"Arquivos deletados: {self.stats['total_arquivos']}\n")
            f.write(f"Duplicatas encontradas: {self.stats.get('duplicatas', 0)}\n")

    def auto_clean_all(self):
        """Executa todas as limpezas"""
        print(Colors.format("\n⚡ INICIANDO LIMPEZA AUTOMÁTICA COMPLETA", Colors.BOLD + Colors.YELLOW))
        print("Isso pode levar alguns minutos...\n")

        tasks = [
            self.clean_app_cache,
            self.clean_temp_files,
            self.clean_browser_cache,
            self.empty_recycle_bin,
            self.find_duplicates,
            self.analyze_disk,
        ]

        total_tasks = len(tasks)
        for idx, task in enumerate(tasks, 1):
            print(Colors.format(f"\n[{idx}/{total_tasks}]", Colors.BOLD), end=" ")
            try:
                task()
            except Exception as e:
                self.print_error(f"Erro: {e}")

        self.show_final_report()

    def run(self):
        """Loop principal"""
        while True:
            choice = self.show_menu()

            if choice == "1":
                self.clean_app_cache()
            elif choice == "2":
                self.clean_temp_files()
            elif choice == "3":
                self.print_task_header("📥", "Downloads antigos")
                self.print_warning("Feature em desenvolvimento")
            elif choice == "4":
                self.find_duplicates()
            elif choice == "5":
                self.analyze_disk()
            elif choice == "6":
                self.empty_recycle_bin()
            elif choice == "7":
                self.print_task_header("📋", "Limpeza de Registro")
                self.print_warning("Requer privilégios elevados")
            elif choice == "8":
                self.clean_browser_cache()
            elif choice == "9":
                self.print_task_header("⚙️ ", "Windows Update")
                self.print_warning("Feature em desenvolvimento")
            elif choice == "A":
                self.auto_clean_all()
                break
            elif choice == "0":
                print("\n👋 Saindo...")
                break
            else:
                self.print_error("Opção inválida!")

            input(f"\n{Colors.format('Pressione ENTER para continuar...', Colors.DIM)}")


def main():
    """Função principal"""
    print("\n" + "="*80)
    print(Colors.format("🚀 SYSTEM CLEANER PRO v2.0", Colors.BOLD + Colors.CYAN))
    print(Colors.format("Limpeza Profissional do Windows", Colors.DIM))
    print("="*80)

    if len(sys.argv) > 1 and sys.argv[1] == "--admin-check":
        cleaner = SystemCleanerPro()
        if cleaner.is_admin:
            print(Colors.format("✓ Executando com privilégios de administrador", Colors.GREEN))
        else:
            print(Colors.format("⚠ Não está executando como administrador", Colors.YELLOW))
        return

    cleaner = SystemCleanerPro()
    if not cleaner.is_admin:
        print(Colors.format("\n⚠️ AVISO:", Colors.YELLOW + Colors.BOLD))
        print("Execute como ADMINISTRADOR para funcionalidade completa!")
        print("👉 Windows + X → Windows PowerShell (Admin)\n")

    cleaner.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Colors.format("\n\n👋 Programa interrompido pelo usuário", Colors.YELLOW))
    except Exception as e:
        print(Colors.format(f"\n❌ Erro fatal: {e}", Colors.RED))
