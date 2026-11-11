# Template Terraform para Validação de 20 PCs

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    local = {
      source = "hashicorp/local"
    }
  }
}

# ---------------------------------------------------------
# 1. Provisionadores para validar hardware antes do SO
# ---------------------------------------------------------

# Define os IPs/hostname dos 20 PCs (exemplo com IPs estáticos)
# Em produção, use um arquivo dinâmico ou Terraform data source
variable "pc_ips" {
  description = "Lista de IPs dos 20 PCs para validação"
  type        = list(string)
  default = [
    "192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14",
    "192.168.1.15", "192.168.1.16", "192.168.1.17", "192.168.1.18", "192.168.1.19",
    "192.168.1.20", "192.168.1.21", "192.168.1.22", "192.168.1.23", "192.168.1.24",
    "192.168.1.25", "192.168.1.26", "192.168.1.27", "192.168.1.28", "192.168.1.29",
    "192.168.1.30"
  ]
}

# ---------------------------------------------------------
# 2. Executa validação em cada PC via provisioner
# ---------------------------------------------------------

resource "null_resource" "pc_validation" {
  count = length(var.pc_ips)
  
  provisioner "remote-exec" {
    # Executa comando remoto via SSH
    connection {
      type        = "ssh"
      host        = var.pc_ips[count.index]
      user        = "root"  # ou usuário padrão
      private_key = file("~/.ssh/id_rsa")  # chave SSH para acesso
    }
    
    inline = [
      # 1. Baixa o executável validador do repositório
      "curl -o /usr/local/bin/validate_preinstall https://raw.githubusercontent.com/meu-projeto/main/validator/terraform_integration.py || wget -O /usr/local/bin/validate_preinstall https://raw.githubusercontent.com/meu-projeto/main/validator/terraform_integration.py",
      
      # 2. Torna executável
      "chmod +x /usr/local/bin/validate_preinstall",
      
      # 3. Executa validação
      "/usr/local/bin/validate_preinstall --format terraform > /tmp/validation_${count.index}.txt",
      
      # 4. Lê o resultado
      "cat /tmp/validation_${count.index}.txt"
    ]
    
    # Condição: só continua se validação passar
    triggers = {
      install_os = length([
        for r in null_resource.pc_validation : r.mode == "apply"
      ]) > 0
    }
  }
  
  # Output: dados de validação para uso posterior
  provisioner "local-exec" {
    command = "echo '${jsonencode(lookup(null_resource.pc_validation[count.index].triggers, "valid", false))}' > /tmp/pc_${count.index}_valid.json"
  }
}

# ---------------------------------------------------------
# 3. Condição de instalação do SO
# ---------------------------------------------------------

# Considera que SO deve ser instalado apenas se TODOS os PCs validarem
# Ou se MAIORIA validar (configurável)
locals {
  all_valid = try(
    [for r in null_resource.pc_validation : lookup(r.triggers, "install_os", false)],
    []
  ) | length > 0,
  
  majority_valid = try(
    [for r in null_resource.pc_validation : r.mode == "apply"],
    []
  ) | length > length(var.pc_ips) / 2
}

# Recurso que instala o SO APENAS se a validação passar
resource "null_resource" "install_os" {
  count = local.majority_valid ? 1 : 0
  
  # ... provisionadores de instalação do SO ...
  provisioner "local-exec" {
    command = "echo 'Iniciando instalação do SO em ${length(var.pc_ips)} PCs ...'"
    # provisionadores reais: shell, file, etc.
  }
  
  # Se nenhum PC validou, cria recurso de alerta
  triggers = {
    validate_failed = local.majority_valid == false
  }
}

# ---------------------------------------------------------
# 4. Outputs para consulta
# ---------------------------------------------------------

output "validation_summary" {
  description = "Resumo da validação de todos os PCs"
  value = {
    total_pcs = length(var.pc_ips)
    all_valid = local.all_valid
    majority_valid = local.majority_valid
    valid_count = try(
      [for r in null_resource.pc_validation : lookup(r.triggers, "valid", false)],
      []
    ) | length
  }
}

output "pc_details" {
  description = "Detalhamento da validação por PC"
  value = {
    for r in null_resource.pc_validation : r.address => r.mode
  }
}