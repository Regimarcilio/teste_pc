"""
Módulo de verificação do sistema
Todas as funções de checagem de hardware/software
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import json


@dataclass
class CheckResult:
    """Resultado de uma verificação individual"""
    name: str
    passed: bool
    value: Any
    required: Any
    message: str
    severity: str  # "error", "warning", "info"


@dataclass
class SystemReport:
    """Relatório completo do sistema"""
    status: str  # "success", "error", "warning"
    score: int
    timestamp: str
    checks: Dict[str, CheckResult] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SystemChecker:
    """Coletor de informações do sistema"""
    
    # Constantes de requisitos mínimos
    MIN_RAM_GB = 8
    MIN_DISK_GB = 10
    MIN_CPU_CORES = 2
    MIN_PYTHON_VERSION = (3, 10)
    MIN_WINDOWS_VERSION = (10, 0)
    MIN_MACOS_VERSION = (11, 0)
    MIN_UBUNTU_VERSION = (20, 4)
    
    def __init__(self):
        self.results: Dict[str, CheckResult] = {}
    
    def check_all(self) -> SystemReport:
        """Executa todas as verificações"""
        import datetime
        
        self.results = {}
        
        # Verificações críticas
        self.results["ram"] = self.check_ram()
        self.results["disk"] = self.check_disk()
        self.results["os"] = self.check_os()
        self.results["python"] = self.check_python()
        
        # Verificações de advertência
        self.results["cpu"] = self.check_cpu()
        self.results["architecture"] = self.check_architecture()
        
        # Verificações opcionais (software)
        self.results["mysql"] = self.check_mysql()
        self.results["vscode"] = self.check_vscode()
        self.results["chrome"] = self.check_chrome()
        
        # Compila relatório
        return self._build_report()
    
    def _build_report(self) -> SystemReport:
        """Constrói relatório final"""
        import datetime
        
        has_error = any(r.severity == "error" and not r.passed for r in self.results.values())
        has_warning = any(r.severity == "warning" and not r.passed for r in self.results.values())
        
        if has_error:
            status = "error"
        elif has_warning:
            status = "warning"
        else:
            status = "success"
        
        # Score 0-100
        score = self._calculate_score()
        
        # Recomendações
        recommendations = self._generate_recommendations()
        
        return SystemReport(
            status=status,
            score=score,
            timestamp=datetime.datetime.now().isoformat(),
            checks=self.results,
            recommendations=recommendations,
            metadata={
                "hostname": platform.node(),
                "platform": platform.platform(),
                "python_version": sys.version.split()[0]
            }
        )
    
    def _calculate_score(self) -> int:
        """Calcula score 0-100"""
        score = 100
        
        # Penalidades por erro
        for check in self.results.values():
            if not check.passed:
                if check.severity == "error":
                    score -= 25
                elif check.severity == "warning":
                    score -= 10
        
        return max(0, score)
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recs = []
        
        for check in self.results.values():
            if not check.passed:
                if check.name == "RAM":
                    recs.append(f"AUMENTAR RAM para {self.MIN_RAM_GB}GB (atual: {check.value}GB)")
                elif check.name == "Disco":
                    recs.append(f"Liberar espaço em disco (mínimo {self.MIN_DISK_GB}GB livres)")
                elif check.name == "Sistema Operacional":
                    recs.append("Atualizar sistema operacional para versão suportada")
                elif check.name == "Python":
                    recs.append(f"Atualizar Python para {self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]}+")
                elif check.name == "CPU":
                    recs.append("Considere CPU com 4+ núcleos para melhor performance")
                elif check.name == "Arquitetura":
                    recs.append("Sistema 32-bit detectado - use versão 64-bit")
                elif check.name == "MySQL":
                    recs.append("Instalar MySQL/MariaDB para banco de dados local")
                elif check.name == "VS Code":
                    recs.append("Instalar VS Code ou alternativa (VS Codium)")
                elif check.name == "Chrome":
                    recs.append("Instalar navegador moderno (Chrome/Firefox/Edge)")
        
        return recs
    
    # ============ VERIFICAÇÕES INDIVIDUAIS ============
    
    def check_ram(self) -> CheckResult:
        """Verifica memória RAM"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            ram_gb = round(mem.total / (1024**3), 1)
            
            passed = ram_gb >= self.MIN_RAM_GB
            
            if passed:
                return CheckResult(
                    name="RAM",
                    passed=True,
                    value=ram_gb,
                    required=f">= {self.MIN_RAM_GB}GB",
                    message=f"[OK] RAM: {ram_gb}GB detectada (mínimo: {self.MIN_RAM_GB}GB)",
                    severity="error"
                )
            else:
                return CheckResult(
                    name="RAM",
                    passed=False,
                    value=ram_gb,
                    required=f">= {self.MIN_RAM_GB}GB",
                    message=f"[ERRO] RAM: {ram_gb}GB detectada (mínimo: {self.MIN_RAM_GB}GB) - Insuficiente!",
                    severity="error"
                )
        except Exception as e:
            return CheckResult(
                name="RAM",
                passed=False,
                value="unknown",
                required=f">= {self.MIN_RAM_GB}GB",
                message=f"[ERRO] Falha ao detectar RAM: {e}",
                severity="error"
            )
    
    def check_disk(self) -> CheckResult:
        """Verifica espaço livre em disco"""
        try:
            # Diretório raiz do projeto ou home
            path = Path.cwd()
            if platform.system() == "Windows":
                path = Path(os.environ.get("SystemDrive", "C:") + "\\")
            
            usage = shutil.disk_usage(path)
            free_gb = round(usage.free / (1024**3), 1)
            total_gb = round(usage.total / (1024**3), 1)
            
            passed = free_gb >= self.MIN_DISK_GB
            
            if passed:
                return CheckResult(
                    name="Disco",
                    passed=True,
                    value=f"{free_gb}GB livres de {total_gb}GB",
                    required=f">= {self.MIN_DISK_GB}GB livres",
                    message=f"[OK] Disco: {free_gb}GB livres (mínimo: {self.MIN_DISK_GB}GB)",
                    severity="error"
                )
            else:
                return CheckResult(
                    name="Disco",
                    passed=False,
                    value=f"{free_gb}GB livres",
                    required=f">= {self.MIN_DISK_GB}GB livres",
                    message=f"[ERRO] Disco: {free_gb}GB livres (mínimo: {self.MIN_DISK_GB}GB) - Limpeza requerida!",
                    severity="error"
                )
        except Exception as e:
            return CheckResult(
                name="Disco",
                passed=False,
                value="unknown",
                required=f">= {self.MIN_DISK_GB}GB livres",
                message=f"[ERRO] Falha ao verificar disco: {e}",
                severity="error"
            )
    
    def check_os(self) -> CheckResult:
        """Verifica sistema operacional"""
        os_name = platform.system()
        os_version = platform.release()
        
        passed = True
        details = ""
        
        if os_name == "Windows":
            # Windows 10+ (build 10240+)
            try:
                major = int(os_version.split(".")[0])
                build = int(platform.version().split(".")[-1])
                if major < 10 or (major == 10 and build < 10240):
                    passed = False
                    details = "Windows 10 (build 10240) ou superior requerido"
            except:
                passed = False
                details = "Versão do Windows não reconhecida"
                
        elif os_name == "Darwin":  # macOS
            try:
                version = platform.mac_ver()[0]
                major, minor = map(int, version.split(".")[:2])
                if major < 11:
                    passed = False
                    details = f"macOS 11+ requerido (atual: {version})"
            except:
                passed = False
                details = "Versão do macOS não reconhecida"
                
        elif os_name == "Linux":
            # Verifica Ubuntu/Debian
            try:
                with open("/etc/os-release") as f:
                    content = f.read()
                if "UBUNTU" in content.upper():
                    import re
                    match = re.search(r'VERSION_ID="(\d+)\.(\d+)"', content)
                    if match:
                        major, minor = map(int, match.groups())
                        if major < 20 or (major == 20 and minor < 4):
                            passed = False
                            details = "Ubuntu 20.04+ requerido"
                elif "DEBIAN" in content.upper():
                    match = re.search(r'VERSION_ID="(\d+)"', content)
                    if match:
                        major = int(match.group(1))
                        if major < 11:
                            passed = False
                            details = "Debian 11+ requerido"
            except:
                # Linux genérico - assume OK se kernel >= 5.4
                try:
                    kernel = platform.release()
                    major = int(kernel.split(".")[0])
                    if major < 5:
                        passed = False
                        details = f"Kernel Linux 5.4+ recomendado (atual: {kernel})"
                except:
                    passed = True  # assume OK
        else:
            passed = False
            details = f"SO não suportado: {os_name}"
        
        if passed:
            return CheckResult(
                name="Sistema Operacional",
                passed=True,
                value=f"{os_name} {os_version}",
                required="Windows 10+ / macOS 11+ / Ubuntu 20.04+",
                message=f"[OK] SO: {os_name} {os_version}",
                severity="error"
            )
        else:
            return CheckResult(
                name="Sistema Operacional",
                passed=False,
                value=f"{os_name} {os_version}",
                required="Windows 10+ / macOS 11+ / Ubuntu 20.04+",
                message=f"[ERRO] SO: {os_name} {os_version} - {details}",
                severity="error"
            )
    
    def check_python(self) -> CheckResult:
        """Verifica versão do Python"""
        current = sys.version_info[:2]
        required = self.MIN_PYTHON_VERSION
        
        passed = current >= required
        version_str = f"{current[0]}.{current[1]}"
        required_str = f"{required[0]}.{required[1]}"
        
        if passed:
            return CheckResult(
                name="Python",
                passed=True,
                value=version_str,
                required=f">= {required_str}",
                message=f"[OK] Python: {version_str} (mínimo: {required_str})",
                severity="error"
            )
        else:
            return CheckResult(
                name="Python",
                passed=False,
                value=version_str,
                required=f">= {required_str}",
                message=f"[ERRO] Python: {version_str} (mínimo: {required_str}) - Atualize!",
                severity="error"
            )
    
    def check_cpu(self) -> CheckResult:
        """Verifica CPU"""
        try:
            import psutil
            physical = psutil.cpu_count(logical=False) or 0
            logical = psutil.cpu_count(logical=True) or 0
            
            passed = physical >= self.MIN_CPU_CORES
            
            if passed:
                return CheckResult(
                    name="CPU",
                    passed=True,
                    value=f"{physical} físicos / {logical} lógicos",
                    required=f">= {self.MIN_CPU_CORES} núcleos físicos",
                    message=f"[OK] CPU: {physical} núcleos físicos / {logical} lógicos",
                    severity="warning"
                )
            else:
                return CheckResult(
                    name="CPU",
                    passed=False,
                    value=f"{physical} físicos / {logical} lógicos",
                    required=f">= {self.MIN_CPU_CORES} núcleos físicos",
                    message=f"[ATENÇÃO] CPU: {physical} núcleos físicos (recomendado: {self.MIN_CPU_CORES}+)",
                    severity="warning"
                )
        except Exception as e:
            return CheckResult(
                name="CPU",
                passed=False,
                value="unknown",
                required=f">= {self.MIN_CPU_CORES} núcleos físicos",
                message=f"[ATENÇÃO] Falha ao detectar CPU: {e}",
                severity="warning"
            )
    
    def check_architecture(self) -> CheckResult:
        """Verifica arquitetura (64-bit)"""
        arch = platform.machine()
        is_64bit = "64" in arch.lower() or arch in ("x86_64", "AMD64", "aarch64", "arm64")
        
        passed = is_64bit
        
        if passed:
            return CheckResult(
                name="Arquitetura",
                passed=True,
                value=arch,
                required="64-bit",
                message=f"[OK] Arquitetura: {arch} (64-bit)",
                severity="warning"
            )
        else:
            return CheckResult(
                name="Arquitetura",
                passed=False,
                value=arch,
                required="64-bit",
                message=f"[ATENÇÃO] Arquitetura: {arch} (32-bit detectado - use 64-bit)",
                severity="warning"
            )
    
    def check_mysql(self) -> CheckResult:
        """Verifica MySQL/MariaDB"""
        mysql_paths = ["mysql", "mysqld", "mariadb"]
        found = False
        version = "não detectado"
        
        for cmd in mysql_paths:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                if result.returncode == 0:
                    found = True
                    version = result.stdout.split()[0] if result.stdout else "desconhecido"
                    break
            except:
                pass
        
        if found:
            return CheckResult(
                name="MySQL",
                passed=True,
                value=version,
                required="opcional",
                message=f"[OK] MySQL: {version} detectado",
                severity="info"
            )
        else:
            return CheckResult(
                name="MySQL",
                passed=False,
                value="não instalado",
                required="opcional",
                message="[INFO] MySQL: não detectado (opcional para desenvolvimento)",
                severity="info"
            )
    
    def check_vscode(self) -> CheckResult:
        """Verifica VS Code"""
        try:
            result = subprocess.run(
                ["code", "--version"],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                version = result.stdout.strip().split("\n")[0]
                return CheckResult(
                    name="VS Code",
                    passed=True,
                    value=version,
                    required="opcional",
                    message=f"[OK] VS Code: {version} detectado",
                    severity="info"
                )
        except:
            pass
        
        return CheckResult(
            name="VS Code",
            passed=False,
            value="não instalado",
            required="opcional",
            message="[INFO] VS Code: não detectado (instale para desenvolvimento)",
            severity="info"
        )
    
    def check_chrome(self) -> CheckResult:
        """Verifica Chrome/Chromium"""
        browsers = ["chrome", "google-chrome", "chromium", "msedge", "firefox"]
        found = None
        
        for browser in browsers:
            try:
                result = subprocess.run(
                    [browser, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                if result.returncode == 0:
                    found = result.stdout.strip().split("\n")[0]
                    break
            except:
                pass
        
        if found:
            return CheckResult(
                name="Navegador",
                passed=True,
                value=found,
                required="opcional",
                message=f"[OK] Navegador: {found} detectado",
                severity="info"
            )
        else:
            return CheckResult(
                name="Navegador",
                passed=False,
                value="não detectado",
                required="opcional",
                message="[INFO] Navegador: não detectado (instale Chrome/Firefox/Edge)",
                severity="info"
            )


def run_checks() -> SystemReport:
    """Função de conveniência"""
    checker = SystemChecker()
    return checker.check_all()