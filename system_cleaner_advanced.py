#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Cleaner ADVANCED - Professional Windows Cleaning Tool
Integra padrões de Win11Debloat: restore points, dry-run, structured logging, rollback
"""

import os
import sys
import json
import shutil
import subprocess
import ctypes
import hashlib
import time
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class Colors:
    """Códigos de cor ANSI para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

    @staticmethod
    def format(text, color):
        return f"{color}{text}{Colors.END}"


class ProgressBar:
    """Barra de progresso com ETA em tempo real"""
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


class SystemLogger:
    """Logger estruturado em JSON - Padrão Harden-Windows-Security"""
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.logs = []
        self.start_time = datetime.now()

    def log(self, level: str, category: str, message: str, details: Dict = None):
        """Registra evento estruturado"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "category": category,
            "message": message,
            "details": details or {}
        }
        self.logs.append(entry)

        # Também mostra no console
        color_map = {
            "INFO": Colors.CYAN,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "ACTION": Colors.BLUE
        }
        color = color_map.get(level, Colors.WHITE)
        print(f"{Colors.format(f'[{level:7}]', color)} {category}: {message}")

    def save(self):
        """Salva log em formato JSON"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "logs": self.logs
            }, f, indent=2, ensure_ascii=False)


class RestorePointManager:
    """Gerencia restore points - Padrão Win11Debloat"""
    def __init__(self, logger: SystemLogger):
        self.logger = logger
        self.restore_point_name = f"PreCleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def create_restore_point(self) -> bool:
        """Cria restore point antes de mudanças"""
        try:
            self.logger.log("ACTION", "RestorePoint", f"Criando restore point: {self.restore_point_name}")

            # Tenta via PowerShell (melhor método)
            ps_script = f"""
            $ErrorActionPreference = 'Stop'
            Checkpoint-Computer -Description '{self.restore_point_name}' -RestorePointType 'MODIFY_SETTINGS'
            """

            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.logger.log("SUCCESS", "RestorePoint", f"Restore point criado: {self.restore_point_name}")
                return True
            else:
                raise Exception(result.stderr)
        except Exception as e:
            self.logger.log("WARNING", "RestorePoint", f"Falha ao criar restore point: {str(e)}")
            return False

    def list_restore_points(self) -> List[str]:
        """Lista restore points disponíveis"""
        try:
            ps_script = "Get-ComputerRestorePoint | Select-Object -Property Description, CreationTime"
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.split('\n')
        except:
            return []


class DryRunMode:
    """Modo de prévia - Padrão BleachBit"""
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.preview_data = {
            "files_to_delete": [],
            "size_to_free": 0,
            "operations": []
        }

    def add_file(self, filepath: str, size: int):
        """Adiciona arquivo à prévia"""
        self.preview_data["files_to_delete"].append({
            "path": filepath,
            "size": size
        })
        self.preview_data["size_to_free"] += size

    def add_operation(self, operation: str, details: str):
        """Adiciona operação à prévia"""
        self.preview_data["operations"].append({
            "operation": operation,
            "details": details
        })

    def show_preview(self):
        """Exibe prévia das mudanças"""
        print("\n" + Colors.format("=" * 80, Colors.YELLOW))
        print(Colors.format("📋 PRÉVIA DO QUE SERÁ EXECUTADO (DRY-RUN)", Colors.YELLOW))
        print(Colors.format("=" * 80, Colors.YELLOW))

        if self.preview_data["files_to_delete"]:
            print(f"\n{Colors.format('Arquivos a deletar:', Colors.CYAN)} {len(self.preview_data['files_to_delete'])}")
            size_mb = self.preview_data["size_to_free"] / (1024 * 1024)
            print(f"{Colors.format('Espaço a liberar:', Colors.GREEN)} {size_mb:.2f} MB")

            if len(self.preview_data["files_to_delete"]) <= 10:
                for item in self.preview_data["files_to_delete"]:
                    print(f"  • {item['path']} ({item['size'] / 1024:.1f} KB)")

        if self.preview_data["operations"]:
            print(f"\n{Colors.format('Operações:', Colors.CYAN)}")
            for op in self.preview_data["operations"]:
                print(f"  ✓ {op['operation']}")
                if op['details']:
                    print(f"    → {op['details']}")

        print(Colors.format("=" * 80, Colors.YELLOW) + "\n")


class ConfigurationManager:
    """Gerencia configuração em JSON"""
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """Carrega configuração do arquivo JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(Colors.format(f"✓ Configuração carregada: {self.config_file}", Colors.GREEN))
        except FileNotFoundError:
            print(Colors.format(f"⚠ Arquivo de config não encontrado: {self.config_file}", Colors.YELLOW))
            self.config = {}

    def get_enabled_categories(self) -> List[str]:
        """Retorna categorias habilitadas"""
        categories = self.config.get("categories", {})
        return [cat for cat, data in categories.items() if data.get("enabled", True)]

    def is_dry_run_enabled(self) -> bool:
        """Verifica se dry-run está habilitado"""
        return self.config.get("operations", {}).get("dry_run_enabled", True)

    def should_create_restore_point(self) -> bool:
        """Verifica se deve criar restore point"""
        return self.config.get("operations", {}).get("create_restore_point", True)


class SystemCleanerAdvanced:
    """Sistema avançado de limpeza com padrões open source"""

    def __init__(self, config_file: Path = None):
        self.is_admin = self._check_admin()

        # Configuração
        self.config_file = config_file or Path("cleaner_config.json")
        self.config_manager = ConfigurationManager(self.config_file)

        # Logging
        self.log_file = Path("cleaner_advanced_log.json")
        self.logger = SystemLogger(self.log_file)

        # Restore point
        self.restore_point_manager = RestorePointManager(self.logger)

        # Dry-run
        self.dry_run_enabled = self.config_manager.is_dry_run_enabled()
        self.dry_run = DryRunMode(self.dry_run_enabled)

        # Estatísticas
        self.stats = {
            "inicio": datetime.now(),
            "fim": None,
            "total_liberado": 0,
            "total_arquivos_deletados": 0,
            "categorias_processadas": [],
            "erros": [],
            "avisos": []
        }

        self._show_header()
        self._check_requirements()

    def _check_admin(self) -> bool:
        """Verifica privilégios de administrador"""
        try:
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False

    def _show_header(self):
        """Mostra cabeçalho inicial"""
        print("\n" + Colors.format("╔" + "═" * 78 + "╗", Colors.BLUE))
        print(Colors.format("║ SYSTEM CLEANER ADVANCED - Windows Optimization Tool                      ║", Colors.BOLD))
        print(Colors.format("║ Integra padrões: Win11Debloat, TronScript, BleachBit, Harden-Windows    ║", Colors.BLUE))
        print(Colors.format("╚" + "═" * 78 + "╝\n", Colors.BLUE))

        status = Colors.format("✓ ADMIN", Colors.GREEN) if self.is_admin else Colors.format("✗ SEM ADMIN", Colors.RED)
        print(f"Status: {status}")
        print(f"Dry-run: {Colors.format('HABILITADO' if self.dry_run_enabled else 'DESABILITADO', Colors.YELLOW)}")
        print()

    def _check_requirements(self):
        """Verifica requisitos do sistema"""
        self.logger.log("INFO", "Requirements", "Verificando requisitos do sistema")

        if not self.is_admin:
            self.logger.log("WARNING", "Requirements", "Script executado sem privilégios de administrador")

    def expand_paths(self, paths: List[str]) -> List[Path]:
        """Expande variáveis de ambiente em caminhos"""
        expanded = []
        for path_str in paths:
            # Substitui variáveis de ambiente
            path_str = os.path.expandvars(path_str)
            expanded_path = Path(path_str)

            if expanded_path.exists():
                expanded.append(expanded_path)

        return expanded

    def scan_and_preview_files(self, locations: List[str], patterns: List[str]) -> Tuple[List[Path], int]:
        """Escaneia arquivos e mostra prévia (sem deletar)"""
        files_to_delete = []
        total_size = 0

        expanded_locations = self.expand_paths(locations)

        for location in expanded_locations:
            if not location.exists():
                continue

            try:
                for filepath in location.rglob('*'):
                    if filepath.is_file():
                        # Verifica padrões
                        should_delete = False

                        if not patterns or any(filepath.match(pattern) for pattern in patterns):
                            should_delete = True

                        # Verifica proteção de pastas críticas
                        if self._is_protected_path(filepath):
                            should_delete = False

                        if should_delete:
                            size = filepath.stat().st_size
                            files_to_delete.append(filepath)
                            total_size += size

                            if self.dry_run_enabled:
                                self.dry_run.add_file(str(filepath), size)
            except Exception as e:
                self.logger.log("WARNING", "Scan", f"Erro ao escanear {location}: {str(e)}")

        return files_to_delete, total_size

    def _is_protected_path(self, filepath: Path) -> bool:
        """Verifica se caminho é protegido"""
        protected = self.config_manager.config.get("security", {}).get("system_folders_protected", [])
        never_delete = self.config_manager.config.get("security", {}).get("never_delete_patterns", [])

        path_str = str(filepath).lower()

        for protected_folder in protected:
            if protected_folder.lower() in path_str:
                return True

        for pattern in never_delete:
            if pattern.lower() in path_str:
                return True

        return False

    def delete_files(self, files: List[Path], show_progress: bool = True) -> Tuple[int, int, List[str]]:
        """Deleta arquivos com feedback em tempo real"""
        deleted = 0
        failed = 0
        errors = []

        if not files:
            return 0, 0, []

        if show_progress:
            pbar = ProgressBar(len(files), "Deletando arquivos")

        for filepath in files:
            try:
                if filepath.is_file():
                    filepath.unlink()
                    deleted += 1
                    if show_progress:
                        pbar.update()
            except Exception as e:
                failed += 1
                errors.append(f"{filepath}: {str(e)}")
                self.logger.log("ERROR", "Delete", f"Falha ao deletar {filepath}: {str(e)}")
                if show_progress:
                    pbar.update()

        if show_progress:
            pbar.finish(f"Deletados: {deleted}, Falhados: {failed}")

        return deleted, failed, errors

    def clean_temporary_files(self) -> Dict:
        """Limpa arquivos temporários"""
        print(Colors.format("\n▶ Limpando Arquivos Temporários...", Colors.CYAN))

        config = self.config_manager.config.get("categories", {}).get("Temporary Files", {})
        locations = config.get("locations", [])
        patterns = config.get("patterns", [])

        files, total_size = self.scan_and_preview_files(locations, patterns)

        result = {
            "categoria": "Temporary Files",
            "arquivos_encontrados": len(files),
            "tamanho_total": total_size,
            "arquivos_deletados": 0,
            "tamanho_liberado": 0
        }

        if files:
            if self.dry_run_enabled:
                self.dry_run.add_operation("Limpeza de Temporários", f"{len(files)} arquivos, {total_size / (1024*1024):.2f} MB")
            else:
                deleted, failed, errors = self.delete_files(files)
                result["arquivos_deletados"] = deleted
                result["tamanho_liberado"] = total_size
                self.logger.log("SUCCESS", "Temporary", f"Deletados {deleted} arquivos, liberados {total_size / (1024*1024):.2f} MB")

        self.stats["categorias_processadas"].append(result)
        return result

    def clean_browser_cache(self) -> Dict:
        """Limpa cache do navegador"""
        print(Colors.format("\n▶ Limpando Cache do Navegador...", Colors.CYAN))

        config = self.config_manager.config.get("categories", {}).get("Browser Cache", {})
        locations = config.get("locations", [])

        files, total_size = self.scan_and_preview_files(locations, [])

        result = {
            "categoria": "Browser Cache",
            "arquivos_encontrados": len(files),
            "tamanho_total": total_size,
            "arquivos_deletados": 0,
            "tamanho_liberado": 0
        }

        if files:
            if self.dry_run_enabled:
                self.dry_run.add_operation("Limpeza de Cache", f"{len(files)} arquivos, {total_size / (1024*1024):.2f} MB")
            else:
                deleted, failed, errors = self.delete_files(files)
                result["arquivos_deletados"] = deleted
                result["tamanho_liberado"] = total_size
                self.logger.log("SUCCESS", "BrowserCache", f"Deletados {deleted} arquivos")

        self.stats["categorias_processadas"].append(result)
        return result

    def analyze_disk_usage(self) -> Dict:
        """Analisa uso de disco"""
        print(Colors.format("\n▶ Analisando Uso de Disco...", Colors.CYAN))

        disk_info = {}

        try:
            for drive in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
                drive_path = f"{drive}:\\"
                if os.path.exists(drive_path):
                    import shutil as sh
                    total, used, free = sh.disk_usage(drive_path)
                    percent = (used / total) * 100 if total > 0 else 0

                    disk_info[drive] = {
                        "total_gb": total / (1024**3),
                        "used_gb": used / (1024**3),
                        "free_gb": free / (1024**3),
                        "percent_used": percent
                    }

                    status = "🔴 CRÍTICO" if percent > 90 else "🟡 AVISO" if percent > 75 else "🟢 OK"
                    print(f"  {drive}:\\  {used / (1024**3):.1f}/{total / (1024**3):.1f} GB ({percent:.1f}%) {status}")
        except Exception as e:
            self.logger.log("ERROR", "DiskAnalysis", str(e))

        result = {
            "categoria": "Disk Analysis",
            "drives": disk_info
        }

        self.stats["categorias_processadas"].append(result)
        return result

    def run_full_cleanup(self):
        """Executa limpeza completa"""
        print(Colors.format("\n╔ INICIANDO LIMPEZA COMPLETA ╗", Colors.BLUE))

        # Criar restore point
        if self.config_manager.should_create_restore_point():
            self.restore_point_manager.create_restore_point()

        # Executar limpezas
        for category in self.config_manager.get_enabled_categories():
            if category == "Temporary Files":
                self.clean_temporary_files()
            elif category == "Browser Cache":
                self.clean_browser_cache()
            elif category == "Disk Analysis":
                self.analyze_disk_usage()

        # Mostrar prévia se dry-run habilitado
        if self.dry_run_enabled:
            self.dry_run.show_preview()
            print(Colors.format("\n⚠ MODO DRY-RUN ATIVADO", Colors.YELLOW))
            print("Nada foi deletado. Execute novamente com --no-dry-run para aplicar mudanças.\n")

    def generate_report(self):
        """Gera relatório final"""
        self.stats["fim"] = datetime.now()

        print("\n" + Colors.format("=" * 80, Colors.GREEN))
        print(Colors.format("📊 RELATÓRIO FINAL", Colors.BOLD))
        print(Colors.format("=" * 80, Colors.GREEN))

        print(f"\n{Colors.format('Duração:', Colors.CYAN)} {(self.stats['fim'] - self.stats['inicio']).total_seconds():.1f}s")
        print(f"{Colors.format('Categorias:', Colors.CYAN)} {len(self.stats['categorias_processadas'])}")

        total_liberado = sum(cat.get('tamanho_liberado', 0) for cat in self.stats['categorias_processadas'])
        print(f"{Colors.format('Total liberado:', Colors.GREEN)} {total_liberado / (1024**2):.2f} MB")

        if self.dry_run_enabled:
            print(f"{Colors.format('Status:', Colors.YELLOW)} Dry-run habilitado (nada foi deletado)")

        print("\n" + Colors.format("=" * 80, Colors.GREEN))

        # Salvar log
        self.logger.save()
        print(f"\n{Colors.format('✓ Log salvo:', Colors.GREEN)} {self.log_file}")


def main():
    """Função principal"""
    try:
        cleaner = SystemCleanerAdvanced()
        cleaner.run_full_cleanup()
        cleaner.generate_report()
    except KeyboardInterrupt:
        print(Colors.format("\n\n⚠ Operação cancelada pelo usuário", Colors.YELLOW))
    except Exception as e:
        print(Colors.format(f"\n✗ Erro: {str(e)}", Colors.RED))
        sys.exit(1)


if __name__ == "__main__":
    main()
