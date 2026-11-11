# SRS - Validação Remota de PCs (Terraform)

## Objetivo
Validar configuração mínima de 20 PCs antes da instalação do sistema operacional.

## Arquitetura Proposta

```
PCs Bare Metal (sem SO) 
       ↓ (Boot via USB/Network)
Validador em Executável Único
       ↓ (Auto-execução)
Coleta de Dados → API/Cloud
       ↓ (Relatório)
Terraform → Decisão de Instalação
```

## Tecnologias

1. **Ferramenta de Boot**: 
   - SystemRescueCD ou 
   - Ubuntu Server netboot ou 
   - Custom ISO com validador embutido

2. **Comunicação**:
   - HTTP API simples (Flask/FastAPI)
   - Ou envio direto via curl para backend

3. **Integração Terraform**:
   - External data source
   - Ou provisioner local-exec

---

## Implementação Proposta

### Opção A: Executável Auto-Contido (MAIS RECOMENDADO)

Criar um único executável que:
1. Não requer instalação
2. Roda em qualquer hardware x86_64 (Linux/Windows)
3. Valida e envia resultados automaticamente

```bash
# Boot via USB/Network
# Executável roda automaticamente
./validate_preinstall --json --upload http://tf-state.example.com
# Aplicação termina, sistema pode ser instalado
```

### Opção B: Script com Python embutido

Usar PyInstaller para criar executável com Python + dependências.

---

## Fluxo Terraform

```hcl
# 1. Prepara os PCs
resource "null_resource" "pc_validation" {
  count = 20
  
  provisioner "remote-exec" {
    inline = [
      # Upload executável via SCP
      "curl -o validate https://repo.example.com/validate",
      "chmod +x validate",
      
      # Execute validação
      "./validate --format terraform --timeout 60",
      
      # Verifica resultado
      "if [ $? -eq 0 ]; then echo 'OK'; else exit 1; fi"
    ]
  }
}

# 2. Condição de instalação do SO
resource "null_resource" "install_os" {
  count = try(
    [for r in null_resource.pc_validation[*] : r.id if r.triggers.install == "true"],
    []
  ).length > 0 ? 1 : 0
  
  provisioner "remote-exec" {
    # Instalação do SO
  }
}
```

---

## Estrutura de Arquivos

```
preinstall_validator/
├── validator/
│   ├── __init__.py
│   ├── cli.py              # Interface de usuário
│   ├── hardware.py         # Detecção de CPU, RAM, disco, arquitetura
│   ├── bios.py             # Detecção firmware (BIOS/UEFI)
│   ├── network.py          # Verificação de NIC
│   └── output.py           # Formatadores (JSON, Terraform, CSV)
├── validators/
│   ├── ram_checker.py
│   ├── cpu_checker.py
│   ├── disk_checker.py
│   └── bios_checker.py
├── build/
│   ├── Dockerfile.build    # Build do executável
│   └── Makefile
├── terraform/
│   └── main.tf             # Exemplo de uso
└── README.md
```

---

## Código de Validação

### hardware.py (versão resumida)
```python
# Verificação via dmesg/proc sem SO completo
def check_bare_metal():
    # DMI/SMBIOS via /sys/firmware/dmi/
    # CPU via /proc/cpuinfo
    # Memória via e820 map ou memtest
    # Disco via /sys/block/
```

### cli.py
```python
# Output formatado para Terraform
def terraform_output(report):
    return {
        "valid": report.score >= 70,
        "score": report.score,
        "failures": [c.name for c in report.checks.values() if not c.passed]
    }
```

---

## Próximos Passos

1. **Criar executável** com PyInstaller
2. **Criar API de upload** simples
3. **Documentar processo de boot** via USB/Network
4. **Criar template Terraform** para automação