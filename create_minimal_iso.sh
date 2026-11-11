#!/bin/bash
# Script alternativo para criar ISO bootável minimalista
# Usa BusyBox e script direto

set -e

ISO_NAME="validate_preinstall_minimal.iso"
BUILD_DIR="/tmp/minimal_iso"
VALIDATOR="dist/validate_preinstall"

echo "🔧 Criando ISO minimal bootável..."

# Verificar se validador existe
if [ ! -f "$VALIDATOR" ]; then
    echo "❌ Validador não encontrado em $VALIDATOR"
    exit 1
fi

# Criar estrutura
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/boot/iso"

# Copiar validador
cp "$VALIDATOR" "$BUILD_DIR/boot/iso/"
chmod +x "$BUILD_DIR/boot/iso/validate_preinstall"

# Criar init script
cat > "$BUILD_DIR/boot/iso/init" << 'EOF'
#!/bin/sh
echo "========================================"
echo "  VALIDADOR DE CONFIGURAÇÃO MÍNIMA"
echo "  ISO MINIMAL v1.0.0"
echo "========================================"
echo ""
echo "Detectando hardware..."
echo ""

# Executar validador
cd /iso
./validate_preinstall || EXIT_CODE=$?

echo ""
echo "Exit code: ${EXIT_CODE:-0}"

case ${EXIT_CODE:-0} in
    0)
        echo "✅ Hardware apto para instalação!"
        echo "Pronto para instalar SO..."
        ;;
    1)
        echo "❌ Hardware NÃO apto!"
        echo "Pare de tentar instalar!"
        ;;
    2)
        echo "⚠️ Aviso: Verifique especificações"
        ;;
esac

echo ""
echo "Pressione Ctrl+C para sair ou aguarde 10 segundos..."
sleep 10
EOF

chmod +x "$BUILD_DIR/boot/iso/init"

# Criar menu de boot simples
cat > "$BUILD_DIR/boot/iso/menu.txt" << 'EOF'
========================================
  MENU DE BOOT - VALIDADOR
========================================

Opções:
  1. Validar Hardware (padrão)
  2. Shell Interativo
  3. Reiniciar
  4. Sair

Seleção: _
EOF

# Criar initramf
echo "📦 Gerando initramfs minimal..."

# Criar initrd usando cpio
cd "$BUILD_DIR/boot/iso"
find . | cpio -o -H newc 2>/dev/null | gzip > "$BUILD_DIR/boot/initrd.img" 2>/dev/null || echo "Aviso: Initrd criado com método alternativo"

# Se cpio não disponível, criar estrutura básica
if [ ! -f "$BUILD_DIR/boot/initrd.img" ]; then
    # Criar diretório raiz
    mkdir -p "$BUILD_DIR/rootfs/{bin,sbin,etc,proc,sys,usr/bin}"
    
    # Copiar validador
    cp /iso/validate_preinstall "$BUILD_DIR/rootfs/usr/bin/"
    
    # Criar init simples
    cat > "$BUILD_DIR/rootfs/init" << 'INIT'
#!/bin/sh
echo "========================================"
echo "  VALIDADOR DE CONFIGURAÇÃO MÍNIMA"
echo "========================================"

cd /usr/bin
./validate_preinstall

echo ""
echo "Resultado:"
echo "Exit code: $?"
echo "Pressione Ctrl+C para sair..."
sleep 30
INIT
    chmod +x "$BUILD_DIR/rootfs/init"
    
    # Simular initrd
    cd "$BUILD_DIR/rootfs"
    find . | cpio -o -H newc 2>/dev/null | gzip > "$BUILD_DIR/boot/initrd.img" || echo "Criar initrd manualmente"
fi

cd /home/project/PROJETOS/teste_pc

# Criar ISO final
echo "📀 Gerando ISO final..."

if command -v genisoimage >/dev/null 2>&1; then
    genisoimage -o "$ISO_NAME" \
        -b boot/initrd.img \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -J -R -v \
        -V "VALIDATE_MINIMAL" \
        "$BUILD_DIR" 2>/dev/null || \
    xorriso -as genisoimage -o "$ISO_NAME" \
        -b boot/initrd.img \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -J -R -v \
        "$BUILD_DIR"
else
    xorriso -as genisoimage -o "$ISO_NAME" \
        -b boot/initrd.img \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -J -R -v \
        "$BUILD_DIR"
fi

# Limpar
rm -rf "$BUILD_DIR"

echo ""
echo "✅ ISO minimal criada: $ISO_NAME"
echo "📊 Tamanho: $(du -h "$ISO_NAME" | cut -f1)"

# SHA256
echo ""
echo "🔐 SHA256:"
sha256sum "$ISO_NAME" | cut -d' ' -f1