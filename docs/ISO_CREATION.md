# ISO Bootável - Guia de Criação

## 📋 Visão Geral

Esta seção documenta como criar uma ISO bootável com o validador de configuração mínima.

## 📦 Opções Disponíveis

### 1. ISO completa com isolinux
```bash
./create_boot_iso.sh
```
- Resultado: `validate_preinstall_boot.iso`
- Tamanho: ~15-20MB
- Requer: genisoimage ou xorriso
- Boot: ISOLINUX

### 2. ISO minimal
```bash
./create_minimal_iso.sh
```
- Resultado: `validate_preinstall_minimal.iso`
- Tamanho: ~8MB (apenas validador)
- Boot: Initrd direto

## 🚀 Manualmente (caso scripts falhem)

### Passo 1: Estrutura básica
```bash
mkdir -p iso/boot iso/isolinux iso/validator
cp dist/validate_preinstall iso/validator/
```

### Passo 2: Configurar isolinux
```bash
# Criar isolinux.cfg
cat > iso/isolinux/isolinux.cfg << 'EOF'
DEFAULT validate
TIMEOUT 30

LABEL validate
  MENU LABEL Validar e Instalar SO
  KERNEL /validator/validate_preinstall
EOF
```

### Passo 3: Gerar ISO
```bash
genisoimage -o validate_preinstall.iso \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R \
    iso/
```

## 📂 Conteúdo da ISO

```
validate_preinstall.iso
├── isolinux/
│   ├── isolinux.cfg
│   └── isolinux.bin
├── validator/
│   └── validate_preinstall (executável 8MB)
├── boot/
│   └── README.txt
└── README.txt
```

## 🎯 Boot via PXE

### DHCP Server
```bash
#dhcp-option=66,"servidor.pxe"
#dhcp-option=67,"pxelinux.0"
```

### TFTP Server
```bash
# Colocar arquivos em /var/tftpboot/
cp validate_preinstall.iso /var/tftpboot/
```

## 🔒 Segurança

- Validador executa como root
- Saída em texto claro
- Sem gravação em disco
- Ideal para ambientes de pré-instalação

## 📊 Testes

```bash
# Testar ISO em VirtualBox
VBoxManage createvm --name "ValidateTest" --register
VBoxManage startvm "ValidateTest" --type emergent
```

## 🆘 Troubleshooting

### Erro: "genisoimage: command not found"
```bash
sudo apt-get install genisoimage
```

### Erro: "xorriso: command not found"
```bash
sudo apt-get install xorriso
```

### Erro: "Permission denied"
```bash
chmod +x dist/validate_preinstall
```