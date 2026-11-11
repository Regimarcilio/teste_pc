"""
Terraform Integration - Formato saída para consumo por Terraform
"""

import json
import sys
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hardware import detect_bare_metal, validate_for_install


def format_terraform_output(validated: dict) -> str:
    """Formata saída para consumo direto por Terraform"""
    
    # Variáveis de ambiente para Terraform
    print(f"# Terraform validation output")
    print(f"_VALIDATION_SCORE = {validated['score']}")
    print(f"_VALIDATION_VALID = {'true' if validated['valid'] else 'false'}")
    print(f"_VALIDATION_RAM_GB = {validated['hardware']['ram_gb']}")
    print(f"_VALIDATION_CPU_CORES = {validated['hardware']['cpu_cores']}")
    print(f"_VALIDATION_DISK_GB = {validated['hardware']['disk_gb']}")
    print(f"_VALIDATION_ARCH = '{validated['hardware']['architecture']}'")
    print(f"_VALIDATION_UEFI = {validated['hardware']['uefi']}")
    print(f"_VALIDATION_SSD = {validated['hardware']['disk_type'] == 'SSD'}")
    
    # Identificadores de falhas (para criar varáveis de erro)
    failed_checks = [k for k, v in validated['checks'].items() if not v]
    if failed_checks:
        print(f"_VALIDATION_FAILED_CHECKS = {json.dumps(failed_checks)}")
    else:
        print(f"_VALIDATION_FAILED_CHECKS = []")
    
    # Recomendações em JSON
    print(f"_VALIDATION_RECOMMENDATIONS = {json.dumps(validated['recommendations'])}")
    
    return json.dumps(validated, indent=2)


def main():
    """Ponto de entrada para Terraform"""
    # Detecta hardware "bare metal"
    spec = detect_bare_metal()
    
    # Valida
    validated = validate_for_install(spec)
    
    # Formata para Terraform
    output = format_terraform_output(validated)
    
    # Também salva em arquivo se necessário
    report_path = Path("terraform_validation_report.json")
    with open(report_path, 'w') as f:
        json.dump(validated, f, indent=2)
    
    # Print final
    print(f"\n# Validação concluída")
    print(f"# Score: {validated['score']}/100")
    print(f"# Válido: {'SIM' if validated['valid'] else 'NÃO'}")
    if validated['recommendations']:
        print(f"# Recomendações: {', '.join(validated['recommendations'])}")
    
    # Código de saída para Terraform
    sys.exit(0 if validated['valid'] else 1)


if __name__ == "__main__":
    main()