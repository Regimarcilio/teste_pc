#!/bin/bash
# ============================================================
# Bootstrap de Instalação com Validação Prévia
# Use este script nos 20 PCs após boot via USB/PXE
# ============================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  BOOTSTRAP - Instalação com Validação"
echo "=========================================="
echo ""

# 1. Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[AVISO] Execute como root para melhor compatibilidade${NC}"
fi

# 2. Baixa o validador
echo "[1/5] Baixando validador de hardware..."
if command -v curl &> /dev/null; then
    curl -fsSL -o /tmp/validate_preinstall \
        "https://raw.githubusercontent.com/meu-projeto/validator/main/validate_preinstall"
elif command -v wget &> /dev/null; then
    wget -q -O /tmp/validate_preinstall \
        "https://raw.githubusercontent.com/meu-projeto/validator/main/validate_preinstall"
else
    echo -e "${RED}[ERRO] Não encontrou curl ou wget${NC}"
    exit 1
fi

# 3. Torna executável
echo "[2/5] Preparando executável..."
chmod +x /tmp/validate_preinstall

# 4. Executa validação
echo "[3/5] Executando validação de hardware..."
/tmp/validate_preinstall > /tmp/validation_output.txt 2>&1
VALIDATION_EXIT=$?

# 5. Lê resultado
echo "[4/5] Analisando resultado..."
source /tmp/validation_output.txt 2>/dev/null || true

# 6. Decisão baseada no score
echo "[5/5] Decisão de instalação..."
echo ""

if [ "$VALIDATION_EXIT" -eq 0 ] && [ "$_VALIDATION_VALID" = "true" ]; then
    echo -e "${GREEN}✅ VALIDADO: Sistema apto para instalação${NC}"
    echo "   Score: $_VALIDATION_SCORE/100"
    echo "   CPU: $_VALIDATION_CPU_CORES núcleos"
    echo "   Disco: $_VALIDATION_DISK_GB GB"
    echo ""
    echo "🚀 Iniciando instalação do sistema operacional..."
    
    # Envia resultado para API/Terraform
    if [ -n "$TF_API_URL" ]; then
        curl -X POST -H "Content-Type: application/json" \
            -d @"terraform_validation.json" \
            "$TF_API_URL/validation" \
            -o /tmp/tf_result.json 2>/dev/null || true
    fi
    
    # Aqui você coloca o script de instalação do SO
    # Exemplo: install_ubuntu.sh, install_windows.sh, etc.
    
    # EXIT SUCCESS
    exit 0
    
else
    echo -e "${RED}❌ VALIDADO: Sistema NÃO apto para instalação${NC}"
    echo "   Score: $_VALIDATION_SCORE/100"
    echo ""
    echo "💡 Recomendações:"
    for rec in $(echo "$_VALIDATION_RECOMMENDATIONS" | python3 -c "import sys,json; [print(x) for x in json.load(sys.stdin)]"); do
        echo "   - $rec"
    done
    echo ""
    echo "🛑 Instalação CANCELADA. Corrija os problemas acima antes de continuar."
    
    # EXIT FAILURE
    exit 1
fi