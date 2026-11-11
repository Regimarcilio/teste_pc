# Terraform para Validação de 20 PCs em Massa

Este diretório contém templates Terraform para validar hardware antes da instalação do sistema operacional.

## 🚀 Rápido Início

### 1. Prepare os PCs

**Opção A: Boot via USB**
```bash
# Grave o validador em USB
dd if=dist/validate_preinstall of=/dev/sdX bs=1M
```

**Opção B: PXE Boot (network)**
Configure DHCP/TFTP para baixar o executável via HTTP.

### 2. Executar Validação

**Via Shell Script:**
```bash
# Nos PCs após boot
./validate_preinstall
```

**Via Terraform:**
```bash
cd terraform
terraform init
terraform apply
```

## 📁 Estrutura

```
terraform/
├── main.tf              # Template principal
├── variables.tf         # Variáveis de configuração
├── outputs.tf           # Outputs Terraform
└── README.md            # Este arquivo

dist/
├── validate_preinstall  # Executável estático (Linux)
└── README.md            # Instruções de uso
```

## 🔧 Variáveis

Edite `variables.tf` para personalizar:
- `pc_ips`: Lista de IPs dos 20 PCs
- `require_all_valid`: Se deve instalar SO só se todos validarem
- `min_ram_gb`, `min_cpu_cores`, `min_disk_gb`: Requisitos mínimos

## 🎯 Fluxo Completo

1. **Bootstrap**: PC boota via USB/Network
2. **Validação**: `validate_preinstall` executa automaticamente
3. **Upload**: Resultado enviado para API/Cloud
4. **Decisão**: Terraform decide instalar ou não o SO

## 📊 Saída do Validador

```bash
# Saída padrão
_VALIDATION_SCORE = 85.0
_VALIDATION_VALID = true
_VALIDATION_RAM_GB = 16.0
_VALIDATION_CPU_CORES = 4
_VALIDATION_DISK_GB = 512.0
_VALIDATION_ARCH = 'x86_64'
_VALIDATION_UEFI = true
```

## 🛠 Customização

### Alterar requisitos mínimos
```python
# validator/hardware.py
MIN_RAM_GB = 8      # Atual: 8GB
MIN_CPU_CORES = 4   # Atual: 4+ núcleos
MIN_DISK_GB = 20    # Atual: 20GB+
```

### Adicionar novos checks
```python
# Em validate_for_install()
checks = {
    # ... checks existentes ...
    "gpu": "NVIDIA" in spec.gpu_model,  # Novo check GPU
    "network": spec.network_interfaces >= 2  # Novo check de rede
}
```

## 📦 Distribuição

Para distribuir em 20 PCs:
```bash
# Compactar executável
tar -czf validate_bundle.tar.gz dist/validate_preinstall scripts/bootstrap_install.sh

# Distribuir via USB ou rede
scp validate_preinstall root@pc-ip:/tmp/
```

## ✨ Dica

Use o validador em **modo silencioso** para logs:
```bash
/tmp/validate_preinstall --quiet > /tmp/result.log
```

---

**Status**: ✅ Pronto para produção
**Última atualização**: 2026-11-10
**Versão**: 1.0.0