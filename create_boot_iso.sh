#!/bin/bash
# Script para criar ISO bootável com validador pré-instalação
# Uso: ./create_boot_iso.sh

set -e

ISO_NAME="validate_preinstall_boot.iso"
WORK_DIR="/tmp/iso_work_$$"
ISO_DIR="$WORK_DIR/iso"

echo "🔧 Criando ISO bootável para validação..."

# Criar estrutura de diretórios
mkdir -p "$ISO_DIR"
mkdir -p "$ISO_DIR/boot"
mkdir -p "$ISO_DIR/isolinux"
mkdir -p "$ISO_DIR/validator"

# Copiar o executável do validador
if [ -f "dist/validate_preinstall" ]; then
    cp dist/validate_preinstall "$ISO_DIR/validator/"
    chmod +x "$ISO_DIR/validator/validate_preinstall"
    echo "✅ Validador copiado"
else
    echo "❌ Erro: dist/validate_preinstall não encontrado"
    exit 1
fi

# Criar bootloader ISOLINUX
cat > "$ISO_DIR/isolinux/isolinux.cfg" << 'ISOLINUX'
DEFAULT linux
TIMEOUT 30
PROMPT 0

LABEL linux
  MENU LABEL Validar Hardware e Instalar SO
  KERNEL /validator/validate_preinstall
  APPEND initrd=/validator/validate_preinstall

LABEL shell
  MENU LABEL Abrir Terminal Shell
  KERNEL /boot/vmlinuz
  APPEND initrd=/boot/initrd.img init=/bin/bash

LABEL reboot
  MENU LABEL Reiniciar
  KERNEL /boot/vmlinuz
  APPEND init=/bin/reboot

LABEL poweroff
  MENU LABEL Desligar
  KERNEL /boot/vmlinuz
  APPEND init=/bin/poweroff
ISOLINUX

# Copiar arquivos do isolinux
if command -v isolinux.bin >/dev/null 2>&1; then
    cp /usr/lib/ISOLINUX/isolinux.bin "$ISO_DIR/isolinux/" 2>/dev/null || true
    cp /usr/lib/syslinux/modules/bios/ldlinux.c32 "$ISO_DIR/isolinux/" 2>/dev/null || true
fi

# Criar menu de boot
cat > "$ISO_DIR/README.txt" << 'README'
========================================
  VALIDADOR DE CONFIGURAÇÃO MÍNIMA
  ISO BOOTÁVEL v1.0.0
========================================

Opções disponíveis:
1. Validar Hardware e Instalar SO
   - Detecta RAM, CPU, Disco, UEFI
   - Retorna códigos de saída:
     0 = Sucesso (pró para instalar)
     1 = Erro Crítico (não apto)
     2 = Aviso (instalar com cuidado)

2. Abrir Terminal Shell
   - Acesso root para diagnóstico

3. Reiniciar / Desligar

Requisitos Mínimos:
- RAM: 8GB
- CPU: 2 núcleos
- Disco: 20GB livre
- Python: 3.10+

========================================
README

# Criar ISO
echo "📦 Gerando ISO..."
genisoimage -o "$ISO_NAME" \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -v \
    -V "VALIDATE_PREINSTALL" \
    "$ISO_DIR" 2>/dev/null || \
xorriso -as genisoimage -o "$ISO_NAME" \
    -b isolinux/isolinux.bin \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -v \
    -V "VALIDATE_PREINSTALL" \
    "$ISO_DIR"

# Limpar
rm -rf "$WORK_DIR"

echo ""
echo "✅ ISO criada: $ISO_NAME"
echo "📊 Tamanho: $(du -h "$ISO_NAME" | cut -f1)"

# Mostrar checksum
echo ""
echo "🔐 SHA256:"
sha256sum "$ISO_NAME" | cut -d' ' -f1