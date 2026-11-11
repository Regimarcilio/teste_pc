# SRS - Validador de Configuração Mínima do Sistema

## 1. Introdução

### 1.1 Propósito
Transformar o sistema de benchmark em um **validador de pré-requisitos** que verifica se a máquina atende aos requisitos mínimos antes de instalar/rodar software desenvolvimento.

### 1.2 Escopo
- **IN**: Usuário executa script de validação antes de instalar VS Code, MySQL, navegadores pesados
- **OUT**: Status de compatibilidade com recomendações de hardware/software
- **FORA**: Benchmarks de performance, comparações entre máquinas

### 1.3 Definições
- **VALIDADOR**: Script que consulta hardware e retorna SUCESSO/ERRO/FALHA
- **REQUISITO MÍNIMO**: Especificação mínima para software funcionar adequadamente
- **SCORE**: Nota de 0-100 baseada em capacidade do sistema

---

## 2. Especificação dos Requisitos

### 2.1 Requisitos Funcionais

| ID | Título | Descrição | Prioridade | Critério de Aceitação |
|----|--------|-----------|------------|----------------------|
| RF-001 | Verificar Memória RAM | Detectar RAM e comparar com 8GB mínimo | CRÍTICA | Se RAM < 8GB → ERRO com mensagem clara |
| RF-002 | Verificar Espaço Disco | Verificar 10GB livres em disco principal | CRÍTICA | Se < 10GB → ERRO |
| RF-003 | Verificar Arquitetura | Confirmar 64-bit para suporte MySQL/Chrome | MÉDIA | Se 32-bit → ADVERTÊNCIA |
| RF-004 | Verificar CPU Cores | Mínimo 2 núcleos físicos | MÉDIA | Se < 2 → ADVERTÊNCIA |
| RF-005 | Verificar SO | Windows 10+/11 ou Linux/macOS recentes | CRÍTICA | SO antigo → ERRO |
| RF-006 | Verificar Python | Python 3.10+ disponível | CRÍTICA | Se < 3.10 → ERRO |
| RF-007 | Verificar MySQL Opcional | Detectar MySQL instalado | FLEXÍVEL | Se não encontrado → SUGESTÃO de instalar |
| RF-008 | Verificar Chrome/VSCode | Detetar IDEs e navegadores | FLEXÍVEL | Listar o que está instalado |
| RF-009 | Gerar Relatório JSON | Output estruturado para CI/CD | MÉDIA | `validator_output.json` criado |
| RF-010 | Código de Saída | Return code para scripts | CRÍTICA | 0=OK, 1=ERRO, 2=ADVERTÊNCIA |

### 2.2 Requisitos Não-Funcionais

| ID | Categorias | Especificação |
|----|------------|---------------|
| RNF-001 | **Performance** | Execução < 5 segundos em hardware mínimo |
| RNF-002 | **Portabilidade** | Windows 10+, Ubuntu 20.04+, macOS 11+ |
| RNF-003 | **Usabilidade** | Mensagem clara em até 3 linhas para cada erro |
| RNF-004 | **Observabilidade** | Log detalhado em modo verboso (`-v`) |
| RNF-005 | **Manutenibilidade** | Código modular, testável |

---

## 3. Regras de Negócio

### RN-001 - Decisão por Componente
```
SE RAM < 8GB → ERRO (não pode prosseguir)
SE Disco < 10GB livre → ERRO
SE SO < Windows 10 ou equivalente → ERRO
SE Python < 3.10 → ERRO
SE CPU < 2 núcleos → ADVERTÊNCIA
SE 32-bit → ADVERTÊNCIA
CASO CONTRÁRIO → SUCESSO
```

### RN-002 - Mensagens Padronizadas
```
✓ [OK] RAM: 16GB detectada (mínimo: 8GB)
✗ [ERRO] Disco: 5GB livre (mínimo: 10GB) - Limpeza requerida
⚠ [ATENÇÃO] CPU: 2 núcleos (recomendado: 4+)
```

### RN-003 - Saída em JSON
```json
{
  "status": "ERRO",
  "score": 35,
  "timestamp": "2026-06-16T10:30:00",
  "checks": {
    "ram": {"pass": false, "value": 4, "required": 8},
    "disk": {"pass": true, "value": 15, "required": 10},
    "cpu": {"pass": true, "value": 2, "required": 2}
  },
  "recommendations": ["Aumentar RAM para 16GB"]
}
```

---

## 4. Tabela de Rastreabilidade

| RF | RN | Teste | Arquivo |
|----|----|-------|---------|
| RF-001 | RN-001 | test_ram_check.py | validator/ram.py |
| RF-002 | RN-001 | test_disk_check.py | validator/disk.py |
| RF-003 | RN-001 | test_arch_check.py | validator/arch.py |
| RF-006 | RN-001 | test_python_check.py | validator/env.py |
| RF-010 | RN-002 | test_exit_code.py | validator/main.py |

---

## 5. Matriz de Decisão Final

| RAM | Disco | SO | Python | CPU | Resultado |
|-----|-------|-----|--------|-----|-----------|
| ≥8GB | ≥10GB | Válido | ≥3.10 | ≥2 | ✅ SUCESSO |
| <8GB | - | - | - | - | 🔴 ERRO |
| - | <10GB | - | - | - | 🔴 ERRO |
| - | - | Inválido | - | - | 🔴 ERRO |
| - | - | - | <3.10 | - | 🔴 ERRO |
| ≥8GB | ≥10GB | Válido | ≥3.10 | <2 | ⚠ ATENÇÃO |

---

## 6. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| MySQL não detectado | Média | Baixo | Sugerir instalação opcional |
| Diferentes comandos Linux | Alta | Médio | Use subprocess com fallback |
| Permissões insuficientes | Baixa | Alto | Mensagens claras de erro |

---

## 7. Análise de Cenários

### Cenário 1: PC com Hardware Adequado (Nova Máquina)
**Entrada**: 16GB RAM, 512GB SSD, 8 núcleos, x86_64, UEFI
**Saída**: SUCESSO - Score: 100/100, "Sistema apto para instalação"

### Cenário 2: PC com Hardware Mínimo
**Entrada**: 8GB RAM, 20GB SSD, 2 núcleos, x86_64, BIOS
**Saída**: SUCESSO - Score: 83.3/100, "Sistema apto com recomendações"

### Cenário 3: PC Rejeitado (Hardware Insuficiente)
**Entrada**: 4GB RAM, 128GB HDD, 2 núcleos, x86_64, BIOS
**Saída**: REJEITADO - Score: 66.7/100, "RAM insuficiente (4GB/8GB mínimo)"

### Cenário 4: Validação Bare-Metal (sem SO instalado)
**Entrada**: Sistema bootado via SystemRescueCD/USBDRIVE
**Saída**: Executa detect_bare_metal() via /proc, /sys, dmidecode
**Score 0-100** → Decisão de instalação automática via Terraform

---

## 8. Arquitetura de Validação Terraform (20 PCs)

### Fluxo de Validação em Massa
```
Boot PXE/USB → validate_preinstall → SSH → Terraform → Decisão
```

### Exit Codes
| Código | Significado | Ação Terraform |
|--------|-------------|----------------|
| 0 | ✅ Sucesso | Instala SO automática |
| 1 | ❌ Rejeitado | Skip, gera alerta |
| 2 | ⚠️ Aviso | Instala com recomendações |

### Saída Terraform
```bash
_VALIDATION_SCORE = 100.0
_VALIDATION_VALID = true
_VALIDATION_RAM_GB = 16.0
_VALIDATION_CPU_CORES = 8
_VALIDATION_DISK_GB = 512.0
_VALIDATION_ARCH = 'x86_64'
_VALIDATION_UEFI = true
_VALIDATION_FAILED_CHECKS = []
```

---

## 9. Próximos Passos

1. **Fase 1**: ✅ Criar estrutura `validator/` com módulos - CONCLUÍDO
2. **Fase 2**: ✅ Implementar funções de verificação bare-metal - CONCLUÍDO
3. **Fase 3**: ✅ Criar CLI com argparse e PyInstaller - CONCLUÍDO
4. **Fase 4**: ✅ Gerar documentação e templates Terraform - CONCLUÍDO
5. **Fase 5**: Executar validação real em 20 PCs físicos
6. **Fase 6**: Configurar PXE boot (DHCP/TFTP) para deploy em massa
7. **Fase 7**: Validar integração com pipeline de instalação do SO

---

## 10. Arquivos Entregues

| Arquivo | Função |
|---------|--------|
| `validator/hardware.py` | Detecção bare-metal de hardware |
| `validator/terraform_integration.py` | Saída compatível Terraform |
| `dist/validate_preinstall` | Executável standalone (Linux) |
| `terraform/main.tf` | Template para 20 PCs |
| `scripts/bootstrap_install.sh` | Script de instalação automática |
| `tests/test_checker.py` | Testes unitários (10/10 passando) |

---

*Documento atualizado: 2026-11-16*
*Versão: 1.1 (bare-metal + Terraform)*