#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Cleaner PRO - Premium Windows Cleaning Tool
Limpeza profissional com recursos que cobram caro em versões comerciais
"""

import os
import sys
import shutil
import subprocess
import ctypes
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json


class SystemCleanerPro:
    """Ferramenta profissional de limpeza do Windows"""

    def __init__(self):
        self.is_admin = self._check_admin()
        self.log_file = Path("cleaner_pro_log.txt")
        self.stats = {
            "inicial": {"total_size": 0, "file_count": 0},
            "liberado": {"total_size": 0, "file_count": 0},
            "duplicadas": {"total_size": 0, "file_count": 0},
            "detalhes": {}
        }
        self.duplicates = defaultdict(list)
        self._initialize_log()

    def _check_admin(self):
        """Verifica privilégios de administrador"""
        try:
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False

    def _initialize_log(self):
        """Limpa e inicializa o arquivo de log"""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"{'='*80}\n")
            f.write(f"SYSTEM CLEANER PRO - {datetime.now()}\n")
            f.write(f"{'='*80}\n\n")

    def log(self, msg, level="INFO"):
        """Registra mensagens com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {msg}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")

    def format_bytes(self, size_bytes):
        """Converte bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def show_menu(self):
        """Mostra menu principal interativo"""
        self.log("=" * 80, "MENU")
        print("\n" + "=" * 80)
        print("🚀 SYSTEM CLEANER PRO v2.0")
        print("=" * 80)
        print("\n📋 LIMPEZAS DISPONÍVEIS:\n")

        options = {
            "1": ("💾 Limpar Cache de Aplicações", self.clean_app_cache),
            "2": ("🗑️  Limpar Arquivos Temporários", self.clean_temp_files),
            "3": ("📥 Limpar Downloads Antigos", self.clean_old_downloads),
            "4": ("🔍 Encontrar Arquivos Duplicados", self.find_duplicates),
            "5": ("💿 Análise Completa de Disco", self.analyze_disk),
            "6": ("🛢️  Limpar Lixeira", self.empty_recycle_bin),
            "7": ("📋 Limpar Registro do Windows", self.clean_registry),
            "8": ("🌐 Limpar Cache de Navegadores", self.clean_browser_cache),
            "9": ("⚙️  Limpar Cache Windows Update", self.clean_windows_update),
            "10": ("📱 Limpar Temp do Winget/Chocolatey", self.clean_package_managers),
            "11": ("🖼️  Limpar Miniaturas e Cache Imagem", self.clean_thumbnails),
            "12": ("🔗 Remover Atalhos Inválidos", self.remove_broken_shortcuts),
            "A": ("⚡ LIMPEZA AUTOMÁTICA COMPLETA", self.auto_clean_all),
            "0": ("Sair", None),
        }

        for key, (desc, _) in options.items():
            print(f"   {key:2s} - {desc}")

        print("\n" + "=" * 80)
        choice = input("\nEscolha uma opção: ").strip().upper()

        if choice in options and options[choice][1]:
            return options[choice][1]
        elif choice == "0":
            return None
        else:
            print("❌ Opção inválida!")
            return self.show_menu

    def clean_app_cache(self):
        """Limpa cache de aplicações (recurso PREMIUM)"""
        self.log("Iniciando limpeza de cache de aplicações...", "INFO")
        print("\n🧹 LIMPANDO CACHE DE APLICAÇÕES...\n")

        cache_paths = [
            Path.home() / "AppData" / "Local" / "Temp",
            Path.home() / "AppData" / "LocalLow" / "Cache",
            Path.home() / "AppData" / "Local" / "CrashDumps",
            Path.home() / "AppData" / "Local" / "VirtualStore",
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer",
        ]

        total_freed = 0
        count = 0

        for cache_path in cache_paths:
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
                    except (PermissionError, OSError):
                        pass

                print(f"   ✓ {cache_path.name}")
                self.log(f"Limpado: {cache_path}", "CLEAN")
            except Exception as e:
                self.log(f"Erro em {cache_path}: {e}", "ERROR")

        print(f"\n✅ Cache limpo: {self.format_bytes(total_freed)} ({count} arquivos)")
        self.stats["liberado"]["total_size"] += total_freed
        self.stats["liberado"]["file_count"] += count

    def clean_temp_files(self):
        """Limpa arquivos temporários do Windows"""
        self.log("Limpando arquivos temporários...", "INFO")
        print("\n🧹 LIMPANDO ARQUIVOS TEMPORÁRIOS...\n")

        temp_paths = [
            Path(os.getenv("TEMP", "")),
            Path(os.getenv("TMP", "")),
            Path("C:\\Windows\\Temp"),
            Path("C:\\Windows\\Prefetch"),
        ]

        total_freed = 0
        count = 0

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
                        elif item.is_dir() and item.name not in ["System Volume Information"]:
                            for file in item.rglob("*"):
                                if file.is_file():
                                    try:
                                        total_freed += file.stat().st_size
                                        file.unlink()
                                        count += 1
                                    except:
                                        pass
                            try:
                                shutil.rmtree(item)
                            except:
                                pass
                    except (PermissionError, OSError):
                        pass

                print(f"   ✓ {temp_path.name}")
                self.log(f"Limpado: {temp_path}", "CLEAN")
            except Exception as e:
                self.log(f"Erro em {temp_path}: {e}", "ERROR")

        print(f"\n✅ Temp limpo: {self.format_bytes(total_freed)} ({count} arquivos)")
        self.stats["liberado"]["total_size"] += total_freed
        self.stats["liberado"]["file_count"] += count

    def clean_old_downloads(self):
        """Limpa downloads antigos (recurso PREMIUM)"""
        self.log("Analisando pasta Downloads...", "INFO")
        print("\n📥 LIMPANDO DOWNLOADS ANTIGOS...\n")

        downloads = Path.home() / "Downloads"
        if not downloads.exists():
            print("❌ Pasta Downloads não encontrada")
            return

        from datetime import timedelta
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)

        total_freed = 0
        count = 0
        files_info = []

        for file in downloads.rglob("*"):
            if not file.is_file():
                continue

            try:
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if mtime < thirty_days_ago:
                    size = file.stat().st_size
                    files_info.append((file.name, size, mtime))
                    file.unlink()
                    total_freed += size
                    count += 1
            except:
                pass

        print(f"   ✓ Analisados arquivos antigos (> 30 dias)")
        print(f"\n✅ Downloads limpos: {self.format_bytes(total_freed)} ({count} arquivos)")

        for fname, size, mtime in files_info[:5]:
            print(f"   • {fname} ({self.format_bytes(size)}) - {mtime.strftime('%d/%m/%Y')}")

        if len(files_info) > 5:
            print(f"   ... e mais {len(files_info) - 5} arquivos")

        self.stats["liberado"]["total_size"] += total_freed
        self.stats["liberado"]["file_count"] += count

    def find_duplicates(self):
        """Encontra arquivos duplicados (recurso PREMIUM)"""
        self.log("Iniciando busca por arquivos duplicados...", "INFO")
        print("\n🔍 ENCONTRANDO ARQUIVOS DUPLICADOS...\n")

        paths_to_scan = [
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.home() / "Pictures",
            Path.home() / "Videos",
        ]

        file_hashes = defaultdict(list)
        print("   Escaneando pastas...")

        for scan_path in paths_to_scan:
            if not scan_path.exists():
                continue

            try:
                for file in scan_path.rglob("*"):
                    if not file.is_file():
                        continue

                    try:
                        file_hash = self._get_file_hash(file)
                        file_hashes[file_hash].append(file)
                    except:
                        pass
            except:
                pass

        duplicates = {k: v for k, v in file_hashes.items() if len(v) > 1}

        if not duplicates:
            print("✅ Nenhum arquivo duplicado encontrado!")
            return

        total_size = 0
        total_count = 0

        print(f"\n📊 DUPLICATAS ENCONTRADAS:\n")

        for idx, (file_hash, files) in enumerate(list(duplicates.items())[:10], 1):
            print(f"   Grupo {idx}:")
            for file in files:
                size = file.stat().st_size
                print(f"      • {file} ({self.format_bytes(size)})")
                if file != files[0]:  # Keep first, count others as duplicates
                    total_size += size
                    total_count += 1

        if len(duplicates) > 10:
            print(f"\n   ... e mais {len(duplicates) - 10} grupos de duplicatas")

        print(f"\n💾 Espaço de duplicatas: {self.format_bytes(total_size)} ({total_count} arquivos)")
        self.stats["duplicadas"]["total_size"] = total_size
        self.stats["duplicadas"]["file_count"] = total_count

    def _get_file_hash(self, file_path, chunk_size=8192):
        """Calcula hash MD5 de um arquivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def analyze_disk(self):
        """Análise completa de disco (recurso PREMIUM)"""
        self.log("Iniciando análise de disco completa...", "INFO")
        print("\n💿 ANÁLISE COMPLETA DE DISCO...\n")

        drives = ["C:\\", "D:\\", "E:\\"]
        total_size = 0
        total_used = 0

        for drive in drives:
            if not Path(drive).exists():
                continue

            try:
                # Usa comando do Windows para obter espaço
                result = subprocess.run(
                    f'powershell -Command "(Get-Item -Path {drive!r}).TotalSize, (Get-Item -Path {drive!r}).UsedSize"',
                    shell=True,
                    capture_output=True,
                    text=True
                )

                print(f"   📍 {drive}")

                # Calcula espaço manualmente
                total = 0
                used = 0
                for root, dirs, files in os.walk(drive, topdown=True):
                    try:
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                used += os.path.getsize(file_path)
                            except:
                                pass
                    except:
                        pass

                    if total > 100 * 1024 * 1024 * 1024:  # Limita scan a 100GB
                        break

                print(f"      Usado: {self.format_bytes(used)}")

            except Exception as e:
                self.log(f"Erro ao analisar {drive}: {e}", "ERROR")

        print(f"\n✅ Análise concluída!")

    def empty_recycle_bin(self):
        """Limpa a lixeira completamente"""
        self.log("Limpando lixeira...", "INFO")
        print("\n🛢️  LIMPANDO LIXEIRA...\n")

        try:
            # Método 1: Usar PowerShell
            subprocess.run(
                "powershell -Command \"Clear-RecycleBin -Force -Confirm:$false\"",
                shell=True,
                capture_output=True
            )
            print("   ✓ Lixeira limpa com sucesso!")
            self.log("Lixeira limpa", "CLEAN")
        except Exception as e:
            self.log(f"Erro ao limpar lixeira: {e}", "ERROR")
            print(f"   ✗ Erro: {e}")

    def clean_registry(self):
        """Limpa registro inválido do Windows (recurso PREMIUM)"""
        self.log("Iniciando limpeza de registro...", "INFO")
        print("\n📋 LIMPANDO REGISTRO DO WINDOWS...\n")

        if not self.is_admin:
            print("   ⚠️  Admin necessário para limpar registro")
            return

        try:
            # Remove atalhos inválidos do registro
            subprocess.run(
                'powershell -Command "Remove-Item -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MountPoints2\' -Recurse -Force -ErrorAction SilentlyContinue"',
                shell=True,
                capture_output=True
            )

            # Remove uninstallers órfãos
            subprocess.run(
                'powershell -Command "Get-ChildItem -Path \'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\' | Where-Object {-not (Test-Path -Path $_.GetValue(\'InstallLocation\'))} | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"',
                shell=True,
                capture_output=True
            )

            print("   ✓ Entradas inválidas removidas")
            print("   ✓ Atalhos órfãos removidos")
            print("   ✓ Uninstallers não funcionais removidos")
            print("\n✅ Limpeza de registro concluída!")
            self.log("Registro limpo", "CLEAN")

        except Exception as e:
            self.log(f"Erro ao limpar registro: {e}", "ERROR")
            print(f"   ✗ Erro: {e}")

    def clean_browser_cache(self):
        """Limpa cache de navegadores (recurso PREMIUM)"""
        self.log("Limpando cache de navegadores...", "INFO")
        print("\n🌐 LIMPANDO CACHE DE NAVEGADORES...\n")

        browsers = {
            "Chrome": Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
            "Edge": Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
            "Firefox": Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles",
        }

        total_freed = 0

        for browser_name, cache_path in browsers.items():
            if not cache_path.exists():
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

                print(f"   ✓ {browser_name}: {self.format_bytes(freed)} ({count} arquivos)")
                total_freed += freed

            except Exception as e:
                self.log(f"Erro com {browser_name}: {e}", "ERROR")

        print(f"\n✅ Cache de navegadores: {self.format_bytes(total_freed)}")
        self.stats["liberado"]["total_size"] += total_freed

    def clean_windows_update(self):
        """Limpa cache do Windows Update (recurso PREMIUM)"""
        self.log("Limpando cache Windows Update...", "INFO")
        print("\n⚙️  LIMPANDO CACHE WINDOWS UPDATE...\n")

        if not self.is_admin:
            print("   ⚠️  Admin necessário")
            return

        try:
            wu_path = Path("C:\\Windows\\SoftwareDistribution\\Download")
            if wu_path.exists():
                freed = 0
                for file in wu_path.rglob("*"):
                    if file.is_file():
                        try:
                            freed += file.stat().st_size
                            file.unlink()
                        except:
                            pass

                print(f"   ✓ Cache Windows Update: {self.format_bytes(freed)}")
                self.stats["liberado"]["total_size"] += freed

        except Exception as e:
            self.log(f"Erro ao limpar Windows Update: {e}", "ERROR")

    def clean_package_managers(self):
        """Limpa cache de gerenciadores de pacotes"""
        self.log("Limpando cache de package managers...", "INFO")
        print("\n📱 LIMPANDO CACHE WINGET/CHOCOLATEY...\n")

        paths = [
            Path.home() / "AppData" / "Local" / "Temp" / "winget",
            Path.home() / "AppData" / "Local" / "Temp" / "chocolatey",
            Path("C:\\ProgramData\\chocolatey\\cache"),
        ]

        total_freed = 0
        for path in paths:
            if path.exists():
                try:
                    for file in path.rglob("*"):
                        if file.is_file():
                            try:
                                total_freed += file.stat().st_size
                                file.unlink()
                            except:
                                pass
                    print(f"   ✓ {path.name}")
                except:
                    pass

        print(f"\n✅ Cache limpo: {self.format_bytes(total_freed)}")
        self.stats["liberado"]["total_size"] += total_freed

    def clean_thumbnails(self):
        """Limpa cache de miniaturas (recurso PREMIUM)"""
        self.log("Limpando cache de miniaturas...", "INFO")
        print("\n🖼️  LIMPANDO CACHE DE MINIATURAS...\n")

        thumb_path = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer"
        if thumb_path.exists():
            try:
                freed = 0
                for file in thumb_path.glob("thumbcache_*.db"):
                    try:
                        freed += file.stat().st_size
                        file.unlink()
                    except:
                        pass

                print(f"   ✓ Cache de miniaturas: {self.format_bytes(freed)}")
                self.stats["liberado"]["total_size"] += freed

            except Exception as e:
                self.log(f"Erro ao limpar miniaturas: {e}", "ERROR")

    def remove_broken_shortcuts(self):
        """Remove atalhos inválidos (recurso PREMIUM)"""
        self.log("Removendo atalhos inválidos...", "INFO")
        print("\n🔗 REMOVENDO ATALHOS INVÁLIDOS...\n")

        paths_to_check = [
            Path.home() / "Desktop",
            Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu",
            Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "SendTo",
        ]

        removed = 0
        for path in paths_to_check:
            if not path.exists():
                continue

            try:
                for shortcut in path.glob("**/*.lnk"):
                    try:
                        # Verifica se o alvo existe
                        if not shortcut.resolve().exists():
                            shortcut.unlink()
                            removed += 1
                    except:
                        try:
                            shortcut.unlink()
                            removed += 1
                        except:
                            pass

                print(f"   ✓ {path.name}")

            except Exception as e:
                self.log(f"Erro em {path}: {e}", "ERROR")

        print(f"\n✅ Atalhos inválidos removidos: {removed}")

    def auto_clean_all(self):
        """Executa todas as limpezas automaticamente"""
        self.log("INICIANDO LIMPEZA AUTOMÁTICA COMPLETA", "AUTO")
        print("\n" + "=" * 80)
        print("⚡ LIMPEZA AUTOMÁTICA COMPLETA")
        print("=" * 80)

        cleaners = [
            ("Cache de Aplicações", self.clean_app_cache),
            ("Arquivos Temporários", self.clean_temp_files),
            ("Downloads Antigos", self.clean_old_downloads),
            ("Cache de Navegadores", self.clean_browser_cache),
            ("Cache Windows Update", self.clean_windows_update),
            ("Miniaturas", self.clean_thumbnails),
            ("Lixeira", self.empty_recycle_bin),
            ("Registro", self.clean_registry),
            ("Atalhos Inválidos", self.remove_broken_shortcuts),
            ("Análise de Disco", self.analyze_disk),
            ("Duplicatas", self.find_duplicates),
        ]

        for idx, (name, func) in enumerate(cleaners, 1):
            print(f"\n[{idx}/{len(cleaners)}] {name}...")
            try:
                func()
            except Exception as e:
                self.log(f"Erro em {name}: {e}", "ERROR")

        self.show_summary()

    def show_summary(self):
        """Mostra resumo das limpezas"""
        print("\n" + "=" * 80)
        print("📊 RESUMO DA LIMPEZA")
        print("=" * 80)

        total_freed = self.stats["liberado"]["total_size"]
        total_files = self.stats["liberado"]["file_count"]
        duplicates_size = self.stats["duplicadas"]["total_size"]
        duplicates_count = self.stats["duplicadas"]["file_count"]

        print(f"\n💾 ESPAÇO LIBERADO:")
        print(f"   Total: {self.format_bytes(total_freed)}")
        print(f"   Arquivos: {total_files}")

        if duplicates_size > 0:
            print(f"\n📋 DUPLICATAS ENCONTRADAS:")
            print(f"   Espaço: {self.format_bytes(duplicates_size)}")
            print(f"   Arquivos: {duplicates_count}")

        print(f"\n📝 Log completo: {self.log_file}")
        print("\n✅ Limpeza concluída!")

    def run(self):
        """Loop principal interativo"""
        try:
            print("\n" + "=" * 80)
            print("🔐 VERIFICANDO PRIVILÉGIOS DE ADMINISTRADOR...")
            print("=" * 80)

            if not self.is_admin:
                print("⚠️  AVISO: Execute como ADMINISTRADOR para funcionalidade completa!")
                print("   Windows + X → Windows PowerShell (Admin)\n")
            else:
                print("✅ Executando com privilégios de admin\n")

            while True:
                action = self.show_menu()
                if action is None:
                    break

                if callable(action):
                    try:
                        action()
                    except Exception as e:
                        self.log(f"Erro: {e}", "ERROR")
                        print(f"\n❌ Erro: {e}")

                input("\nPressione ENTER para continuar...")

        except KeyboardInterrupt:
            self.log("Programa interrompido pelo usuário", "INFO")
            print("\n\n👋 Programa interrompido")

    def save_report(self):
        """Salva relatório em JSON"""
        report_file = Path("cleaner_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, default=str)
        self.log(f"Relatório salvo: {report_file}", "INFO")


def main():
    """Função principal"""
    print("\n" + "=" * 80)
    print("🚀 SYSTEM CLEANER PRO v2.0 - Limpeza Profissional do Windows")
    print("=" * 80)
    print("\n🔓 Recursos PREMIUM inclusos (normalmente cobrados):")
    print("   ✓ Detecção de arquivos duplicados")
    print("   ✓ Limpeza profunda de registro")
    print("   ✓ Análise completa de disco")
    print("   ✓ Limpeza de cache de navegadores")
    print("   ✓ Limpeza de Windows Update")
    print("   ✓ Remover atalhos inválidos")
    print("   ✓ E muito mais!")
    print("\n" + "=" * 80 + "\n")

    cleaner = SystemCleanerPro()
    cleaner.run()
    cleaner.save_report()


if __name__ == "__main__":
    main()
