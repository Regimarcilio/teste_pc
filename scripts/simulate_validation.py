"""
Simulação de Validação em Massa (20 PCs)
Útil para testes antes da implementação real
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import List
import sys
sys.path.insert(0, "/home/project/PROJETOS/teste_pc")

from validator.hardware import validate_for_install, HardwareSpec


@dataclass
class SimulatedPC:
    """PC simulado para teste"""
    id: int
    hostname: str
    ip: str
    hardware: HardwareSpec
    validation_result: dict = None
    
    def validate(self):
        """Executa validação"""
        self.validation_result = validate_for_install(self.hardware)
        return self.validation_result


def generate_simulated_pcs(count: int = 20) -> List[SimulatedPC]:
    """Gera PCs simulados com specs variadas"""
    
    pc_list = []
    
    # Configurações pré-definidas para realismo
    configs = [
        # "Bom" (60% dos PCs) - Hardware novo
        {"ram": 16, "cpu": 8, "disk": 512, "type": "SSD", "arch": "x86_64", "uefi": True},
        # "Médio" (25% dos PCs) - Hardware adequado
        {"ram": 8, "cpu": 4, "disk": 256, "type": "SSD", "arch": "x86_64", "uefi": True},
        # "Baixo" (15% dos PCs) - Precisa de upgrade
        {"ram": 4, "cpu": 2, "disk": 128, "type": "HDD", "arch": "x86_64", "uefi": False},
    ]
    
    for i in range(1, count + 1):
        # Escolhe configuração aleatória
        config = random.choices(configs, weights=[0.6, 0.25, 0.15])[0]
        
        # Gera IP
        ip = f"192.168.1.{10 + i}"
        
        pc = SimulatedPC(
            id=i,
            hostname=f"pc-{i:03d}",
            ip=ip,
            hardware=HardwareSpec(
                ram_gb=config["ram"],
                cpu_cores=config["cpu"],
                cpu_model=f"Intel Core {['i5', 'i3', 'Celeron'][min(i % 3, 2)]}-{['10210U', '8250U', 'J1800'][min(i % 3, 3)]}",
                disk_gb=config["disk"],
                disk_type=config["type"],
                architecture=config["arch"],
                bios_vendor="American Megatrends",
                bios_version="5.12",
                uefi=config["uefi"]
            )
        )
        pc_list.append(pc)
    
    return pc_list


def run_mmass_validation():
    """Executa validação em massa"""
    
    print("=" * 60)
    print("SIMULAÇÃO DE VALIDAÇÃO - 20 PCs")
    print("=" * 60)
    print()
    
    # Gera PCs simulados
    pcs = generate_simulated_pcs(20)
    
    # Valida cada PC
    results = []
    for pc in pcs:
        result = pc.validate()
        results.append(result)
        
        status = "✅ APROVADO" if result['valid'] else "❌ REJEITADO"
        print(f"PC-{pc.id:02d} [{pc.ip}] {status} - Score: {result['score']}/100")
        if result['recommendations']:
            for rec in result['recommendations']:
                print(f"   ⚠️  {rec}")
    
    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    approved = sum(1 for r in results if r['valid'])
    rejected = len(results) - approved
    
    print(f"Total PCs: {len(results)}")
    print(f"Aprovados: {approved}")
    print(f"Rejeitados: {rejected}")
    print(f"Taxa de aprovação: {approved/len(results)*100:.1f}%")
    
    # Decisão Terraform
    majority = approved >= len(results) / 2
    print()
    print("DECISÃO TERRAFORM:")
    if majority:
        print(f"  ✅ Instalar SO em {approved} PCs (maioria aprovou)")
    else:
        print(f"  ❌ Cancelar instalação - menos de 50% aprovaram")
    
    return results, majority


def generate_terraform_output(results: list):
    """Gera saída compatível com Terraform"""
    
    approved_count = sum(1 for r in results if r['valid'])
    pcs_data = []
    
    for i, result in enumerate(results):
        pcs_data.append({
            "id": f"pc_{i+1:03d}",
            "valid": result['valid'],
            "score": result['score'],
            "ram_gb": result['hardware']['ram_gb'],
            "cpu_cores": result['hardware']['cpu_cores'],
            "disk_gb": result['hardware']['disk_gb'],
            "checks_passed": sum(1 for v in result['checks'].values() if v)
        })
    
    output = {
        "total_pcs": len(results),
        "approved_count": approved_count,
        "majority_approved": approved_count >= len(results) / 2,
        "pcs": pcs_data,
        "validation_timestamp": "2026-11-16T00:00:00"
    }
    
    return output


if __name__ == "__main__":
    results, major_approved = run_mmass_validation()
    
    print()
    print("=" * 60)
    print("SAÍDA PARA TERRAFORM (JSON)")
    print("=" * 60)
    
    tf_output = generate_terraform_output(results)
    print(json.dumps(tf_output, indent=2))
    
    # Salva para uso posterior
    with open("mass_validation_results.json", "w") as f:
        json.dump(tf_output, f, indent=2)
    
    print()
    print("📄 Resultados salvos em: mass_validation_results.json")