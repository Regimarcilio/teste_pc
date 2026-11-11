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

### Cenário 1: Máquina com 4GB RAM (Configuração Atual)
**Entrada**: 4GB RAM, 15GB disco, 2 núcleos, Python 3.9
**Saída**: ERRO - "RAM insuficiente (4GB/8GB requerido). Instale mais memória."

### Cenário 2: Máquina Nova
**Entrada**: 16GB RAM, 200GB disco, 8 núcleos, Python 3.11
**Saída**: SUCESSO - "Sistema compatível. Pronto para desenvolvimento."

### Cenário 3: Máquina Mac antiga
**Entrada**: macOS 10.15, 8GB RAM
**Saída**: ERRO - "macOS 11+ requerido.Atualize ou use alternative."

---

## 8. Próximos Passos

1. **Fase 1**: Criar estrutura `validator/` com módulos
2. **Fase 2**: Implementar funções de verificação
3. **Fase 3**: Criar CLI com argparse
4. **Fase 4**: Gerar documentação e instalação
5. **Fase 5**: Testes automatizados

---

*Documento criado: 2026-06-16*
*Versão: 1.0*