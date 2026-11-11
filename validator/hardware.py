"""
Hardware Checkers - Validação sem sistema operacional completo
Funciona com SystemRescueCD, Ubuntu Netboot ou em executáveis estáticos
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class HardwareSpec:
    """Especificações mínimas detectadas"""
    ram_gb: float
    cpu_cores: int
    cpu_model: str
    disk_gb: float
    disk_type: str
    architecture: str
    bios_vendor: str
    bios_version: str
    uefi: bool


def detect_bare_metal() -> HardwareSpec:
    """Detecta hardware sem depender de SO instalado"""
    
    ram_gb = _detect_ram_bare_metal()
    cpu_cores, cpu_model = _detect_cpu_bare_metal()
    disk_gb, disk_type = _detect_disk_bare_metal()
    arch = platform.machine()
    bios_vendor, bios_version, uefi = _detect_bios()
    
    return HardwareSpec(
        ram_gb=ram_gb,
        cpu_cores=cpu_cores,
        cpu_model=cpu_model,
        disk_gb=disk_gb,
        disk_type=disk_type,
        architecture=arch,
        bios_vendor=bios_vendor,
        bios_version=bios_version,
        uefi=uefi
    )


def _detect_ram_bare_metal() -> float:
    """Detecta RAM via /sys ou dmesg"""
    # Método 1: via sysfs (mais preciso)
    try:
        meminfo = Path("/sys/devices/system/memory/memory0")
        if meminfo.exists():
            mem_total = 0
            for mem_region in Path("/sys/devices/system/memory").glob("memory*"):
                if (mem_region / "end_page").exists():
                    end_path = mem_region / "end_page"
                    start_path = mem_region / "start_page"
                    if end_path.exists() and start_path.exists():
                        end = int(end_path.read_text().strip())
                        start = int(start_path.read_text().strip())
                        mem_total += (end - start + 1) * 4  # 4KB pages
            return round(mem_total / (1024**2), 2)  # GB
    except:
        pass
    
    # Método 2: via /proc/meminfo (requer kernel bootado)
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    return round(int(line.split()[1]) / (1024**2), 2)
    except:
        pass
    
    # Método 3: via dmidecode (requer root)
    try:
        result = subprocess.run(
            ["dmidecode", "-t", "memory"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            total = 0
            for line in result.stdout.split("\n"):
                if "Size:" in line and "No Module Installed" not in line:
                    size_str = line.split(":")[1].strip().split()[0]
                    if "GB" in size_str:
                        total += float(size_str.replace("GB", ""))
                    elif "MB" in size_str:
                        total += float(size_str.replace("MB", "")) / 1024
            return round(total, 2) if total > 0 else 0
    except:
        pass
    
    return 0.0


def _detect_cpu_bare_metal() -> tuple[int, str]:
    """Detecta CPU via /proc/cpuinfo ou lscpu"""
    cores = 0
    model = "unknown"
    
    # Método 1: /proc/cpuinfo
    try:
        with open("/proc/cpuinfo") as f:
            content = f.read()
            cores = content.count("processor")
            for line in content.split("\n"):
                if line.startswith("model name"):
                    model = line.split(":")[1].strip()
                    break
    except:
        pass
    
    # Método 2: lscpu
    if cores == 0:
        try:
            result = subprocess.run(["lscpu"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "CPU(s):" in line:
                        cores = int(line.split(":")[1].strip())
                    elif "Model name:" in line:
                        model = line.split(":")[1].strip()
        except:
            pass
    
    # Método 3: /sys/devices
    if cores == 0:
        try:
            cpu_path = Path("/sys/devices/system/cpu")
            if cpu_path.exists():
                cores = len(list(cpu_path.glob("cpu[0-9]*")))
        except:
            pass
    
    return cores, model


def _detect_disk_bare_metal() -> tuple[float, str]:
    """Detecta disco via /sys/block"""
    total_gb = 0.0
    disk_type = "unknown"
    
    try:
        for disk in Path("/sys/block").glob("sd*"):
            if disk.exists():
                # Tamanho em setores (512 bytes each)
                size_path = disk / "size"
                if size_path.exists():
                    sectors = int(size_path.read_text().strip())
                    gb = sectors * 512 / (1024**3)
                    total_gb += gb
                
                # Tipo de disco (SSD/HDD)
                queue_path = disk / "queue/rotational"
                if queue_path.exists():
                    rotational = queue_path.read_text().strip()
                    if rotational == "0":
                        disk_type = "SSD"
                    elif rotational == "1":
                        disk_type = "HDD"
    except:
        pass
    
    return round(total_gb, 2), disk_type


def _detect_bios() -> tuple[str, str, bool]:
    """Detecta info do BIOS/UEFI"""
    try:
        result = subprocess.run(
            ["dmidecode", "-t", "bios"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            vendor = "unknown"
            version = "unknown"
            uefi = False
            
            for line in result.stdout.split("\n"):
                if "Vendor:" in line:
                    vendor = line.split(":")[1].strip()
                elif "Version:" in line:
                    version = line.split(":")[1].strip()
                elif "UEFI" in line or "efi" in line.lower():
                    uefi = True
            
            return vendor, version, uefi
    except:
        pass
    
    return "unknown", "unknown", False


# Constantes de requisitos mínimos
MIN_RAM_GB = 8
MIN_CPU_CORES = 2
MIN_DISK_GB = 20
MIN_DISK_TYPE = "HDD"  # HDD aceito, SSD preferido


def validate_for_install(spec: HardwareSpec) -> dict:
    """Valida se hardware suporta instalação do SO"""
    
    checks = {
        "ram": spec.ram_gb >= MIN_RAM_GB,
        "cpu": spec.cpu_cores >= MIN_CPU_CORES,
        "disk": spec.disk_gb >= MIN_DISK_GB,
        "disk_type": spec.disk_type in ("SSD", "HDD"),
        "architecture": spec.architecture in ("x86_64", "AMD64", "aarch64"),
        "uefi": spec.uefi  # Recomendado, mas não obrigatório
    }
    
    score = sum(checks.values()) / len(checks) * 100
    
    return {
        "hardware": spec.__dict__,
        "checks": checks,
        "score": round(score, 1),
        "valid": score >= 50,  # 50% de checks passados
        "recommendations": _generate_recommendations(spec, checks)
    }


def _generate_recommendations(spec: HardwareSpec, checks: dict) -> list:
    """Gera recomendações baseadas na validação"""
    recs = []
    
    if not checks["ram"]:
        recs.append(f"RAM insuficiente ({spec.ram_gb}GB). Mínimo: {MIN_RAM_GB}GB")
    
    if not checks["cpu"]:
        recs.append(f"CPU insuficiente ({spec.cpu_cores} núcleos). Mínimo: {MIN_CPU_CORES} núcleos")
    
    if not checks["disk"]:
        recs.append(f"Espaço em disco insuficiente ({spec.disk_gb}GB). Mínimo: {MIN_DISK_GB}GB")
    
    if not checks["architecture"]:
        recs.append(f"Arquitetura não suportada: {spec.architecture}")
    
    if not checks["uefi"]:
        recs.append("BIOS detectado. UEFI recomendado para UEFI Boot")
    
    return recs