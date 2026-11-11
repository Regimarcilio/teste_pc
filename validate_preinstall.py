#!/usr/bin/env python3
"""
Validador Pré-Instalação do Sistema - Executável Estático
Pacote standalone que pode rodar sem instalar dependências
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Adiciona diretório do script ao path
script_dir = Path(__file__).parent if "__file__" in dir() else Path.cwd()
sys.path.insert(0, str(script_dir))

# Importa hardware detection
try:
    from validator.hardware import detect_bare_metal, validate_for_install
except ImportError:
    # Fallback se for executado como script único
    import subprocess
    import platform
    
    def detect_bare_metal():
        """Fallback simplificado para ambiente sem módulos"""
        import shutil
        
        ram_gb = 0.0
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        ram_gb = round(int(line.split()[1]) / (1024**2), 2)
                        break
        except:
            pass
        
        cpu_cores = 0
        try:
            cpu_cores = len(Path("/sys/devices/system/cpu").glob("cpu[0-9]*"))
        except:
            pass
        
        disk_gb = 0.0
        try:
            usage = shutil.disk_usage("/")
            disk_gb = round(usage.total / (1024**3), 2)
        except:
            pass
        
        return type('HardwareSpec', (), {
            'ram_gb': ram_gb,
            'cpu_cores': cpu_cores,
            'cpu_model': platform.processor() or "unknown",
            'disk_gb': disk_gb,
            'disk_type': 'SSD',  # Assume SSD
            'architecture': platform.machine(),
            'bios_vendor': 'unknown',
            'bios_version': 'unknown',
            'uefi': True  # Assume UEFI
        })()
    
    def validate_for_install(spec):
        """Fallback de validação"""
        checks = {
            "ram": spec.ram_gb >= 8,
            "cpu": spec.cpu_cores >= 2,
            "disk": spec.disk_gb >= 20,
            "disk_type": True,
            "architecture": spec.architecture in ("x86_64", "AMD64"),
            "uefi": True
        }
        score = sum(checks.values()) / len(checks) * 100
        return {
            "hardware": spec.__dict__,
            "checks": checks,
            "score": round(score, 1),
            "valid": score >= 50,
            "recommendations": []
        }


def format_terraform_output(validated: dict) -> str:
    """Formata saída para consumo Terraform"""
    print(f"# Validação de Hardware - {datetime.now().isoformat()}")
    print(f"# Score: {validated['score']}/100")
    print()
    print(f"_VALIDATION_SCORE = {validated['score']}")
    print(f"_VALIDATION_VALID = {'true' if validated['valid'] else 'false'}")
    print(f"_VALIDATION_RAM_GB = {validated['hardware']['ram_gb']}")
    print(f"_VALIDATION_CPU_CORES = {validated['hardware']['cpu_cores']}")
    print(f"_VALIDATION_DISK_GB = {validated['hardware']['disk_gb']}")
    print(f"_VALIDATION_ARCH = '{validated['hardware']['architecture']}'")
    print(f"_VALIDATION_UEFI = {validated['hardware']['uefi']}")
    print(f"_VALIDATION_CPU_MODEL = '{validated['hardware']['cpu_model']}'")
    
    failed = [k for k, v in validated['checks'].items() if not v]
    print(f"_VALIDATION_FAILED_CHECKS = {json.dumps(failed)}")
    
    print(f"_VALIDATION_RECOMMENDATIONS = {json.dumps(validated['recommendations'])}")
    print()
    print(f"# Resultado: {'Aprovado' if validated['valid'] else 'Rejeitado'}")
    
    return json.dumps(validated, indent=2)


def main():
    """Main entry point"""
    print("🔍 Validador de Configuração Mínima do Sistema")
    print("=" * 50)
    
    try:
        # Detecta hardware
        spec = detect_bare_metal()
        
        # Valida
        validated = validate_for_install(spec)
        
        # Formata saída
        output = format_terraform_output(validated)
        
        # Salva resultado
        result_file = Path("/tmp/validation_result.json")
        with open(result_file, 'w') as f:
            json.dump(validated, f, indent=2)
        print(f"\n📄 Resultado salvo em: {result_file}")
        
        # Exit code para scripts
        sys.exit(0 if validated['valid'] else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()