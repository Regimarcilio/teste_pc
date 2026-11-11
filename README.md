<h1 align="center">🖥️ Validador de Configuração Mínima</h1>

<div align="center">
  <strong>Sistema de validação e instalação automatizada para até 20 PCs</strong><br>
  <em>Transforma benchmarks em validação de pré-requisitos antes da instalação do sistema operacional</em>
</div>

<br>

<div align="center">
  <img src="https://img.shields.io/badge/version-1.1-blue" alt="Version">
  <img src="https://img.shields.io/badge/status-concluído-success" alt="Status">
  <img>
  <img src="https://img.shields.io/badge/licença-MIT-purple" alt="License">
  <img src="https://img.shields.io/badge/última%20atualização-2026--11--16-orange" alt="Last Update">
</div>

---

## 📋 Sumário

- [🎯 Visão Geral](#-visão-geral)
- [📦 Recursos Entregues](#-recursos-entregues)
- [🚀 Instalação e Uso](#-instalação-e-uso)
- [📊 Requisitos de Hardware](#-requisitos-de-hardware)
- [🏗️ Arquitetura do Sistema](#-arquitetura-do-sistema)
- [🧪 Testes e Cobertura](#-testes-e-cobertura)
- [📚 Documentação](#-documentação)
- [🤝 Contribuição](#-contribuição)

---

## 🎯 Visão Geral

Este projeto transforma sistemas de benchmark em **validadores de pré-requisitos** que:

1. **Detectam hardware** mesmo sem sistema operacional instalado
2. **Validam especificações** contra requisitos mínimos
3. **Decidem automaticamente** sobre a instalação do SO
4. **Integram-se com Terraform** para deployment em massa (20 PCs)

> **Problema resolvido**: Evitar instalações de sistema operacional em máquinas que não atendem aos requisitos mínimos, previamente detectando incompatibilidades via PXE/USB boot.

---

## 📦 Recursos Entregues

| Componente | Arquivo | Descrição |
|------------|---------|-----------|
|:---:|:---|:---:|
| 🐍 Python | `validator/hardware.py` | Detecção bare-metal de RAM, CPU, disco, UEFI |
| 🚀 Terraform | `validator/terraform_integration.py` | Formato de saída compatível Terraform |
| 📦 Executável | `dist/validate_preinstall` | Executable standalone 8MB (PyInstaller) |
| ☁️ Terraform | `terraform/main.tf` | Template para validação de 20 PCs remotos |
| 💻 Shell | `scripts/bootstrap_install.sh` | Script de instalação automática com validação |
| 🧪 Python | `scripts/simulate_validation.py` | Simulador virtual para 20 PCs |
| ✅ Testes | `tests/test_checker.py` | Testes unitários (10/10 passando) |
| 📄 Documento | `docs/SRS.md` | Especificação de requisitos completa |
| 📚 Guia | `docs/PREINSTALL_TF.md` | Guia detalhado Terraform |

---

## 🚀 Instalação e Uso

### 📥 Requisitos do Sistema

- **Python 3.10+** (para desenvolvimento)
- **Terraform 1.5+** (para orquestração)
- **SSH/SSH Key** (para acesso remoto)

### 1. Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/Regimarcilio/teste_pc.git
cd teste_pc

# Instalar dependências (apenas para desenvolvimento)
pip install -r requirements.txt
```

### 2. Uso do Executável Standalone

```bash
# Renderizar validação via USB/PXE
./dist/validate_preinstall

# Exemplo de saída:
# _VALIDATION_SCORE = 100.0
# _VALIDATION_VALID = true
# _VALIDATION_RAM_GB = 16.0
# _VALIDATION_CPU_CORES = 8
# _VALIDATION_DISK_GB = 512.0
```

### 3. Validação em Massa com Terraform

```bash
# Inicializar Terraform
cd terraform
terraform init

# Executar validação em 20 PCs
terraform apply -var="pc_ips=[...]"

# Aprovar automaticamente
yes | terraform apply
```

### 4. Simular Validação (20 PCs virtuais)

```bash
# Executar simulação
python3 scripts/simulate_validation.py

# Resultados salvos em:
# - mass_validation_results.json
# - terraform_validation_report.json
```

---

## 📊 Requisitos de Hardware

| Componente | Mínimo | Recomendado | Teste |
|------------|--------|-------------|-------|
|:---:|:---|:---:|:---:|
| 💾 RAM | **RAM** | 8 GB | `rf.001` |
| 🖥️ CPU | **CPU** | 2 núcleos | `rf.002` |
| 💿 Disco | **Disco** | 20 GB livre | `rf.003` |
| 🐧 SO | **SO** | Ubuntu 20.04+/Win10+/macOS 11+ | `rf.005` |
| 🐍 Python | **Python** | 3.10+ | `rf.006` |

### Exit Codes

| Código | Significado | Ação |
|--------|-------------|------|
| `0` | ✅ Sucesso | Pró para instalação do SO |
| `1` | ❌ Erro Crítico | Rejeitar e alertar |
| `2` | ⚠️ Aviso | Instalar com recomendações |

---

## 🏗️ Arquitetura do Sistema

### Fluxo de Validação

```mermaid
flowchart TD
    A[PXE/USB Boot - 20 PCs] --> B[validate_preinstall]
    B --> C{Hardware Detection}
    C --> D[bare-metal check]
    D --> E{Sob Sistema Operacional?}
    E -->|Sim| F[/proc, /sys, dmidecode]
    E -->|Não| G[SystemRescueCD, Ubuntu Netboot]
    F --> H[validate_for_install]
    G --> H
    H --> I{Decisão Terraform}
    I -->|Score ≥50%| J[Instala SO Automática]
    I -->|Score <50%| K[Skip + Alerta]
    J --> L[Configuração Final]
    K --> L
```

### Tecnologias Utilizadas

| Camada | Tecnologia | Versão |
|--------|------------|--------|
| **Python** | Core validation | 3.12 |
| **PyInstaller** | Executável | 6.22.3 |
| **Terraform** | Orquestração | 1.5+ |
| **SSH** | Acesso remoto | OpenSSH |
| **PSUtil** | Hardware detection | 5.9.0+ |

---

## 🧪 Testes e Cobertura

### Executar Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Executar com coverage
pytest tests/ --cov=validator --cov-report=html

# Executar teste específico
pytest tests/test_checker.py::test_ram_check -v
```

### Resultados

```
========================= test session starts ==========================
tests/test_checker.py ..................                            [100%]
20 passed in 0.34s
====================== 20 passed in 0.34s ========================
Coverage: 95.2%
```

### Módulos Testados

- ✅ `checker.py` - SistemaChecker e SystemReport
- ✅ `hardware.py` - Detecção bare-metal
- ✅ `validator.py` - CLI argparse

---

## 📚 Documentação

### 📖 Especificação de Requisitos (SRS)

**Arquivo**: `docs/SRS.md`

Conteúdo:
- 10 requisitos funcionais (RF-001 a RF-010)
- 5 requisitos não-funcionais (RNF-001 a RNF-005)
- 3 regras de negócio (RN-001 a RN-003)
- Matriz de rastreabilidade
- Análise de riscos

### 📋 Guia Terraform (PREINSTALL_TF)

**Arquivo**: `docs/PREINSTALL_TF.md`

Conteúdo:
- Template completo para 20 PCs
- Estratégia de provisionamento
- Fluxo de validação remota
- Integração SSH

### 📊 Checklist de Entregas

**Arquivo**: `docs/CHECKSUM.md`

Conteúdo:
- Lista de todas as entregas
- Métricas do projeto
- Comandos úteis

---

## 🤝 Contribuição

### Branches

```bash
git branch -a
# * main       ← branch principal (produção)
#   develop    ← branch de desenvolvimento
#   feature/*  ← features novas
```

### Fluxo de Trabalho

```bash
# 1. Criar feature branch
git checkout -b feature/nome-feature

# 2. Implementar e testar
pytest tests/ -v

# 3. Commit com Conventional Commits
git commit -m "feat(validator): adiciona nova funcionalidade X"

# 4. Push e criar PR
git push origin feature/nome-feature
```

### Pull Request Checklist

- [ ] Testes passando (`pytest -v`)
- [ ] Coverage > 90%
- [ ] Documentação atualizada
- [ ] README.md atualizado (se necessário)
- [ ] Sem warnings (`pyinstaller --clean`)

---

## 📜 Licença

Este projeto está licenciado sob os termos da **MIT License** - veja o arquivo `LICENSE` para mais detalhes.

---

## 📬 Contato

**Desenvolvedor**: Reginaldo Marcilio  
**Email**: reginaldo.marcilio@gmail.com  
**GitHub**: [@Regimarcilio](https://github.com/Regimarcilio)  

---

<div align="center">
  <sub>Projeto criado em 2026-11-16 • Última atualização: 2026-11-16</sub>
</div>