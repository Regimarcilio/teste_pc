#!/usr/bin/env python3
"""
BENCHMARK COMPLETO COM DASHBOARD
- Coleta TODOS os dados do sistema (CPU, RAM, Discos, GPU, Rede, Processos)
- Executa teste de performance realista (VS Code + MySQL + Chrome)
- Apresenta resultados em dashboard organizado
"""

import subprocess
import time
import psutil
import threading
import os
import json
from datetime import datetime
from pathlib import Path
import random
import math
import platform
import sys
from collections import deque

# Configurações de cores
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class CompleteBenchmark:
    def __init__(self):
        self.work_dir = Path("test_workload")
        self.work_dir.mkdir(exist_ok=True)
        
        # Dados do sistema
        self.system_data = {}
        self.test_results = {}
        self.metrics_history = []
        
    def collect_system_data(self):
        """Coleta TODOS os dados do sistema"""
        print(f"{Colors.HEADER}{Colors.BOLD}🔍 COLETANDO DADOS DO SISTEMA...{Colors.END}")
        
        data = {}
        
        # 1. SISTEMA OPERACIONAL
        data["os"] = {
            "name": platform.system(),
            "version": platform.release(),
            "build": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node()
        }
        
        # 2. CPU
        cpu_info = {}
        try:
            # Nome da CPU
            if os.name == 'nt':
                result = subprocess.run('wmic cpu get name', shell=True, capture_output=True, text=True)
                if result.stdout and len(result.stdout.split('\n')) > 1:
                    cpu_info["name"] = result.stdout.split('\n')[1].strip()
            else:
                result = subprocess.run('cat /proc/cpuinfo | grep "model name" | head -1', 
                                      shell=True, capture_output=True, text=True)
                if result.stdout:
                    cpu_info["name"] = result.stdout.split(':')[1].strip()
            
            cpu_info["cores_physical"] = psutil.cpu_count(logical=False)
            cpu_info["cores_logical"] = psutil.cpu_count(logical=True)
            
            freq = psutil.cpu_freq()
            if freq:
                cpu_info["max_freq_mhz"] = round(freq.max)
                cpu_info["min_freq_mhz"] = round(freq.min)
                cpu_info["current_freq_mhz"] = round(freq.current)
            
            # Cache (Linux)
            if os.name != 'nt':
                try:
                    cache = subprocess.run('lscpu | grep "cache"', shell=True, capture_output=True, text=True).stdout
                    cpu_info["cache"] = [x.strip() for x in cache.split('\n') if x.strip()]
                except:
                    pass
        except:
            cpu_info["name"] = "Desconhecido"
        
        data["cpu"] = cpu_info
        
        # 3. MEMÓRIA RAM
        mem_info = {}
        try:
            mem = psutil.virtual_memory()
            mem_info["total_gb"] = round(mem.total / (1024**3), 2)
            mem_info["available_gb"] = round(mem.available / (1024**3), 2)
            mem_info["used_gb"] = round(mem.used / (1024**3), 2)
            mem_info["percent"] = mem.percent
            
            # Tipo e velocidade (Windows)
            if os.name == 'nt':
                try:
                    # Tipo
                    type_result = subprocess.run('wmic memorychip get memorytype', shell=True, capture_output=True, text=True)
                    types = {'24': 'DDR3', '26': 'DDR4', '32': 'DDR5'}
                    for line in type_result.stdout.split('\n'):
                        if line.strip() in types:
                            mem_info["type"] = types[line.strip()]
                            break
                    
                    # Velocidade
                    speed_result = subprocess.run('wmic memorychip get speed', shell=True, capture_output=True, text=True)
                    speeds = [x.strip() for x in speed_result.stdout.split('\n') if x.strip().isdigit()]
                    if speeds:
                        mem_info["speed"] = f"{speeds[0]} MHz"
                except:
                    pass
        except:
            mem_info["total_gb"] = 0
        
        data["memory"] = mem_info
        
        # 4. SWAP
        swap_info = {}
        try:
            swap = psutil.swap_memory()
            swap_info["total_gb"] = round(swap.total / (1024**3), 2) if swap.total > 0 else 0
            swap_info["used_gb"] = round(swap.used / (1024**3), 2) if swap.total > 0 else 0
            swap_info["percent"] = swap.percent if swap.total > 0 else 0
            swap_info["enabled"] = swap.total > 0
        except:
            swap_info["enabled"] = False
        
        data["swap"] = swap_info
        
        # 5. DISCOS
        disks = []
        try:
            for partition in psutil.disk_partitions():
                if os.name == 'nt':
                    if 'cdrom' in partition.opts or partition.fstype == '':
                        continue
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Tipo do disco
                    disk_type = "Desconhecido"
                    if os.name == 'nt':
                        cmd = f'powershell -command "Get-PhysicalDisk | Where-Object {{$_.DeviceNumber -eq (Get-Partition -DriveLetter {partition.mountpoint[0]} | Get-Disk).Number}} | Select-Object MediaType"'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if "SSD" in result.stdout:
                            disk_type = "SSD"
                        elif "HDD" in result.stdout:
                            disk_type = "HDD"
                    else:
                        result = subprocess.run(f'cat /sys/block/*/queue/rotational 2>/dev/null | head -1', 
                                               shell=True, capture_output=True, text=True)
                        if result.stdout.strip() == "0":
                            disk_type = "SSD"
                        elif result.stdout.strip() == "1":
                            disk_type = "HDD"
                    
                    disks.append({
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage.percent,
                        "type": disk_type
                    })
                except:
                    pass
        except:
            pass
        
        data["disks"] = disks
        
        # 6. GPU
        gpu_info = {}
        try:
            if os.name == 'nt':
                result = subprocess.run('wmic path win32_VideoController get name', shell=True, capture_output=True, text=True)
                if result.stdout and len(result.stdout.split('\n')) > 1:
                    gpu_info["name"] = result.stdout.split('\n')[1].strip()
                
                # Memória da GPU
                result = subprocess.run('wmic path win32_VideoController get AdapterRAM', shell=True, capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if line.strip().isdigit():
                        gpu_info["memory_mb"] = round(int(line.strip()) / (1024**2), 2)
                        break
            else:
                result = subprocess.run('lspci | grep VGA', shell=True, capture_output=True, text=True)
                if result.stdout:
                    gpu_info["name"] = result.stdout.strip()
        except:
            gpu_info["name"] = "Não detectado"
        
        data["gpu"] = gpu_info
        
        # 7. REDE
        network_info = []
        try:
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == 2:  # IPv4
                        network_info.append({
                            "interface": iface,
                            "ip": addr.address,
                            "netmask": addr.netmask
                        })
                        break
        except:
            pass
        
        data["network"] = network_info
        
        # 8. PROCESSOS EM EXECUÇÃO
        processes = []
        try:
            for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']), 
                             key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:15]:
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'] or "N/A",
                        "cpu_percent": round(proc.info['cpu_percent'] or 0, 1),
                        "memory_percent": round(proc.info['memory_percent'] or 0, 1),
                        "status": proc.info['status'] or "N/A"
                    })
                except:
                    pass
        except:
            pass
        
        data["processes"] = processes
        
        self.system_data = data
        return data

    def print_dashboard(self):
        """Exibe dashboard completo com todos os dados"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # ==================== CABEÇALHO ====================
        print(f"{Colors.CYAN}{'='*90}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}🖥️  DASHBOARD COMPLETO DO SISTEMA - {self.system_data.get('os', {}).get('name', 'Unknown')}{Colors.END}")
        print(f"{Colors.CYAN}{'='*90}{Colors.END}")
        
        # ==================== LINHA 1: SO ====================
        os_info = self.system_data.get('os', {})
        print(f"{Colors.BOLD}📋 SISTEMA:{Colors.END} {os_info.get('name', 'N/A')} {os_info.get('version', 'N/A')} ({os_info.get('architecture', 'N/A')})")
        print(f"   Hostname: {os_info.get('hostname', 'N/A')}")
        
        # ==================== LINHA 2: CPU ====================
        cpu_info = self.system_data.get('cpu', {})
        cpu_name = cpu_info.get('name', 'Não detectado')[:50]
        print(f"{Colors.BOLD}⚡ CPU:{Colors.END} {cpu_name}")
        print(f"   Núcleos: {cpu_info.get('cores_physical', 'N/A')} físicos / {cpu_info.get('cores_logical', 'N/A')} lógicos")
        if 'max_freq_mhz' in cpu_info:
            print(f"   Frequência: {cpu_info.get('min_freq_mhz', 0)} - {cpu_info.get('max_freq_mhz', 0)} MHz (atual: {cpu_info.get('current_freq_mhz', 0)} MHz)")
        if 'cache' in cpu_info:
            for cache_line in cpu_info['cache'][:2]:
                print(f"   {cache_line}")
        
        # ==================== LINHA 3: MEMÓRIA ====================
        mem_info = self.system_data.get('memory', {})
        mem_bar = self.create_bar(mem_info.get('percent', 0), 40)
        mem_color = self.get_color(mem_info.get('percent', 0))
        mem_type = f" {mem_info.get('type', '')} {mem_info.get('speed', '')}" if 'type' in mem_info else ""
        print(f"{Colors.BOLD}💾 RAM:{Colors.END} {mem_info.get('total_gb', 0):.2f} GB{mem_type}")
        print(f"   Usado: {mem_info.get('used_gb', 0):.2f} GB | Disponível: {mem_info.get('available_gb', 0):.2f} GB")
        print(f"   [{mem_color}{mem_bar}{Colors.END}] {mem_info.get('percent', 0):.1f}%")
        
        # ==================== LINHA 4: SWAP ====================
        swap_info = self.system_data.get('swap', {})
        if swap_info.get('enabled', False):
            swap_bar = self.create_bar(swap_info.get('percent', 0), 40)
            swap_color = self.get_color(swap_info.get('percent', 0))
            print(f"{Colors.BOLD}💿 SWAP:{Colors.END} {swap_info.get('total_gb', 0):.2f} GB")
            print(f"   Usado: {swap_info.get('used_gb', 0):.2f} GB")
            print(f"   [{swap_color}{swap_bar}{Colors.END}] {swap_info.get('percent', 0):.1f}%")
        else:
            print(f"{Colors.BOLD}💿 SWAP:{Colors.END} Desabilitado")
        
        # ==================== LINHA 5: DISCOS ====================
        disks = self.system_data.get('disks', [])
        if disks:
            print(f"{Colors.BOLD}💿 DISCOS:{Colors.END}")
            for disk in disks:
                disk_bar = self.create_bar(disk.get('percent', 0), 30)
                disk_color = self.get_color(disk.get('percent', 0))
                print(f"   {disk.get('mountpoint', 'N/A')} ({disk.get('type', 'Desconhecido')}) - {disk.get('filesystem', 'N/A')}")
                print(f"   Total: {disk.get('total_gb', 0):.2f} GB | Livre: {disk.get('free_gb', 0):.2f} GB")
                print(f"   [{disk_color}{disk_bar}{Colors.END}] {disk.get('percent', 0):.1f}%")
        
        # ==================== LINHA 6: GPU ====================
        gpu_info = self.system_data.get('gpu', {})
        if gpu_info.get('name'):
            print(f"{Colors.BOLD}🎮 GPU:{Colors.END} {gpu_info.get('name', 'N/A')[:50]}")
            if 'memory_mb' in gpu_info:
                print(f"   Memória: {gpu_info.get('memory_mb', 0):.0f} MB")
        
        # ==================== LINHA 7: REDE ====================
        network = self.system_data.get('network', [])
        if network:
            print(f"{Colors.BOLD}🌐 REDE:{Colors.END}")
            for iface in network[:2]:
                print(f"   {iface.get('interface', 'N/A')}: {iface.get('ip', 'N/A')}")
        
        # ==================== LINHA 8: PROCESSOS ====================
        processes = self.system_data.get('processes', [])
        if processes:
            print(f"{Colors.BOLD}🔝 TOP 10 PROCESSOS (por CPU):{Colors.END}")
            print(f"   {'PID':>6} {'NOME':<30} {'CPU%':>8} {'MEM%':>8} {'STATUS':<10}")
            print(f"   {'-'*6} {'-'*30} {'-'*8} {'-'*8} {'-'*10}")
            for proc in processes[:10]:
                cpu_color = self.get_color(proc.get('cpu_percent', 0))
                mem_color = self.get_color(proc.get('memory_percent', 0))
                print(f"   {proc.get('pid', 0):>6} {proc.get('name', 'N/A')[:30]:<30} {cpu_color}{proc.get('cpu_percent', 0):>7.1f}%{Colors.END} {mem_color}{proc.get('memory_percent', 0):>7.1f}%{Colors.END} {proc.get('status', 'N/A')[:10]:<10}")
        
        # ==================== LINHA 9: RESULTADOS DO TESTE ====================
        if self.test_results:
            self.print_test_results()
        
        print(f"{Colors.CYAN}{'='*90}{Colors.END}")

    def print_test_results(self):
        """Exibe resultados do teste de performance"""
        results = self.test_results
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}📊 RESULTADOS DO TESTE DE PERFORMANCE{Colors.END}")
        print(f"{Colors.CYAN}{'-'*90}{Colors.END}")
        
        # Métricas
        avg_cpu = results["averages"]["cpu"]
        avg_ram = results["averages"]["memory_percent"]
        avg_swap = results["averages"]["swap_percent"]
        max_ram = results["peaks"]["memory_percent"]
        
        print(f"{Colors.BOLD}📈 MÉTRICAS DURANTE O TESTE:{Colors.END}")
        print(f"   • CPU:    média {avg_cpu:.1f}%")
        print(f"   • RAM:    média {avg_ram:.1f}% (pico: {max_ram:.1f}%)")
        if avg_swap > 0:
            print(f"   • SWAP:   média {avg_swap:.1f}%")
        
        # Diagnóstico
        self.print_diagnosis()
        
        # Avaliação
        self.print_evaluation()

    def print_diagnosis(self):
        """Exibe diagnóstico baseado nos resultados"""
        results = self.test_results
        avg_ram = results["averages"]["memory_percent"]
        avg_swap = results["averages"]["swap_percent"]
        avg_cpu = results["averages"]["cpu"]
        max_ram = results["peaks"]["memory_percent"]
        cpu_cores = self.system_data.get('cpu', {}).get('cores_physical', 0)
        
        print(f"\n{Colors.BOLD}🔍 DIAGNÓSTICO:{Colors.END}")
        
        issues = []
        warnings = []
        
        # RAM
        if avg_ram > 80 or max_ram > 85:
            issues.append(f"{Colors.RED}🚨 CRÍTICO: RAM sobrecarregada! Média: {avg_ram:.1f}% | Pico: {max_ram:.1f}%{Colors.END}")
            issues.append(f"{Colors.RED}   • Com VS Code + Chrome + MySQL, você NÃO tem memória suficiente{Colors.END}")
            issues.append(f"{Colors.RED}   • SOLUÇÃO: AUMENTAR RAM para 16GB (prioridade máxima){Colors.END}")
        elif avg_ram > 70:
            warnings.append(f"{Colors.YELLOW}⚠️  ALTO: RAM em média {avg_ram:.1f}%{Colors.END}")
            warnings.append(f"{Colors.YELLOW}   • Pode começar a usar swap e travar com multitarefa{Colors.END}")
            warnings.append(f"{Colors.YELLOW}   • Considere upgrade para 16GB{Colors.END}")
        
        # SWAP
        if avg_swap > 15:
            issues.append(f"{Colors.RED}🚨 CRÍTICO: SWAP em uso! Média: {avg_swap:.1f}%{Colors.END}")
            issues.append(f"{Colors.RED}   • PC está usando DISCO como memória (100x mais lento){Colors.END}")
            issues.append(f"{Colors.RED}   • SOLUÇÃO: AUMENTAR RAM para 16GB AGORA!{Colors.END}")
        elif avg_swap > 5:
            warnings.append(f"{Colors.YELLOW}⚠️  SWAP em uso ({avg_swap:.1f}%){Colors.END}")
            warnings.append(f"{Colors.YELLOW}   • Sinal de que a RAM está sendo exigida{Colors.END}")
        
        # CPU (poucos núcleos)
        if cpu_cores <= 2 and avg_cpu > 60:
            warnings.append(f"{Colors.YELLOW}⚠️  CPU com {cpu_cores} núcleos - média {avg_cpu:.1f}%{Colors.END}")
            warnings.append(f"{Colors.YELLOW}   • Processador básico para multitarefa pesada{Colors.END}")
        
        # Exibe problemas
        if issues:
            print(f"\n{Colors.RED}❌ PROBLEMAS CRÍTICOS:{Colors.END}")
            for issue in issues:
                print(f"  {issue}")
        
        if warnings:
            print(f"\n{Colors.YELLOW}⚠️  AVISOS:{Colors.END}")
            for warning in warnings:
                print(f"  {warning}")
        
        if not issues and not warnings:
            print(f"\n{Colors.GREEN}✅ Sistema está saudável!{Colors.END}")

    def print_evaluation(self):
        """Exibe avaliação final"""
        results = self.test_results
        avg_ram = results["averages"]["memory_percent"]
        avg_swap = results["averages"]["swap_percent"]
        avg_cpu = results["averages"]["cpu"]
        max_ram = results["peaks"]["memory_percent"]
        cpu_cores = self.system_data.get('cpu', {}).get('cores_physical', 0)
        
        # Calcula score
        score = 100
        if avg_ram > 80 or max_ram > 85: score -= 35
        elif avg_ram > 70: score -= 20
        elif avg_ram > 60: score -= 10
        
        if avg_swap > 10: score -= 25
        elif avg_swap > 5: score -= 15
        
        if cpu_cores <= 2 and avg_cpu > 60: score -= 10
        if avg_cpu > 80: score -= 15
        
        score = max(0, min(100, score))
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}⭐ AVALIAÇÃO FINAL{Colors.END}")
        print(f"{Colors.CYAN}{'-'*90}{Colors.END}")
        
        if score >= 80:
            grade = f"{Colors.GREEN}🟢 BOM{Colors.END}"
            detail = "Sistema funciona bem para tarefas básicas"
        elif score >= 65:
            grade = f"{Colors.YELLOW}🟡 REGULAR{Colors.END}"
            detail = "Pode ter lentidão com multitarefa"
        elif score >= 50:
            grade = f"{Colors.YELLOW}🟠 RUIM{Colors.END}"
            detail = "Lentidão frequente com várias aplicações"
        else:
            grade = f"{Colors.RED}🔴 CRÍTICO{Colors.END}"
            detail = "Sistema sobrecarregado, precisa de upgrade urgente"
        
        print(f"\n  Nota: {score}/100")
        print(f"  Classificação: {grade}")
        print(f"  Status: {detail}")
        
        # Recomendações
        print(f"\n{Colors.BOLD}💡 RECOMENDAÇÕES:{Colors.END}")
        
        if avg_ram > 70 or avg_swap > 5:
            print(f"  {Colors.RED}1. PRIORIDADE #1: AUMENTAR RAM para 16GB{Colors.END}")
            print(f"     → Custo: R$ 150-250")
            print(f"     → Benefício: Elimina travamentos e melhora multitarefa")
        
        if avg_ram > 60:
            print(f"  {Colors.YELLOW}2. Enquanto não aumenta RAM:{Colors.END}")
            print(f"     • Feche aplicativos não utilizados")
            print(f"     • Use no máximo 5-8 abas no navegador")
            print(f"     • Evite VS Code + Chrome + MySQL simultaneamente")
        
        if cpu_cores <= 2:
            print(f"  {Colors.YELLOW}3. Otimizações para CPU com poucos núcleos:{Colors.END}")
            print(f"     • Use versões leves dos aplicativos")
            print(f"     • Desabilite animações e efeitos visuais")

    def create_bar(self, value, width):
        """Cria barra de progresso"""
        filled = int((min(value, 100) / 100) * width)
        return '█' * filled + '░' * (width - filled)

    def get_color(self, value):
        """Retorna cor baseada no valor"""
        if value < 50:
            return Colors.GREEN
        elif value < 75:
            return Colors.YELLOW
        else:
            return Colors.RED

    def run_performance_test(self):
        """Executa teste de performance realista"""
        print(f"\n{Colors.HEADER}{'='*90}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}🚀 INICIANDO TESTE DE PERFORMANCE REALISTA{Colors.END}")
        print(f"{Colors.HEADER}{'='*90}{Colors.END}")
        
        print(f"\n{Colors.BOLD}📋 CENÁRIO DO TESTE:{Colors.END}")
        print("  • VS Code: 2 instâncias editando arquivos")
        print("  • Chrome: 2 instâncias com múltiplas abas")
        print("  • MySQL: 2 conexões com consultas")
        print("  • Multitarefa: operações mistas")
        
        print(f"\n{Colors.YELLOW}⏳ Duração: 60 segundos{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Não use o PC durante o teste para resultados precisos{Colors.END}")
        
        input(f"\n{Colors.BOLD}Pressione ENTER para começar...{Colors.END}")
        
        # Coleta métricas iniciais
        initial_mem = psutil.virtual_memory()
        initial_swap = psutil.swap_memory()
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # ==================== SIMULA CARGA REAL ====================
        start_time = time.time()
        duration = 60
        
        # Funções dos workers
        def vscode_worker(worker_id):
            """Simula VS Code"""
            for i in range(80):
                file_path = self.work_dir / f"vscode_{worker_id}_{i}.tmp"
                try:
                    with open(file_path, 'w') as f:
                        for _ in range(100):
                            f.write(f"function test_{i}() {{\n")
                            f.write("  const data = [];\n")
                            f.write("  for (let j = 0; j < 100; j++) {\n")
                            f.write("    data.push(j * 2);\n")
                            f.write("  }\n")
                            f.write("  return data;\n")
                            f.write("}\n\n")
                    
                    # Simula busca
                    if i % 5 == 0:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            _ = content.count("function")
                    
                    os.remove(file_path)
                    time.sleep(0.02)
                except:
                    pass
        
        def chrome_worker(worker_id):
            """Simula Chrome com múltiplas abas"""
            data_chunks = []
            try:
                for _ in range(4):  # 4 abas
                    data_chunks.append(bytearray(8 * 1024 * 1024))  # 8MB por aba
                    time.sleep(0.05)
                
                # Simula renderização
                for _ in range(20):
                    _ = [i * i for i in range(5000)]
                    time.sleep(0.01)
                
                del data_chunks
            except:
                pass
        
        def mysql_worker(worker_id):
            """Simula MySQL"""
            try:
                # Cria dataset
                data = [{"id": i, "value": random.random() * 1000, "category": i % 10} for i in range(3000)]
                
                for i in range(150):
                    # SELECT com filtro
                    filtered = [d for d in data if d["value"] > 500]
                    # ORDER BY
                    sorted_data = sorted(filtered, key=lambda x: x["value"], reverse=True)[:100]
                    # GROUP BY
                    grouped = {}
                    for d in data[:1000]:
                        key = d["category"]
                        grouped[key] = grouped.get(key, 0) + 1
                    # JOIN (simulado)
                    result = []
                    for d in filtered[:50]:
                        result.append({**d, "extra": d["value"] * 2})
                    time.sleep(0.01)
            except:
                pass
        
        def multitask_worker():
            """Operações mistas"""
            try:
                for i in range(40):
                    # Cálculo pesado
                    _ = [math.sqrt(j) for j in range(2000)]
                    # I/O
                    file_path = self.work_dir / f"multi_{i}.tmp"
                    with open(file_path, 'w') as f:
                        f.write("x" * 5000)
                    with open(file_path, 'r') as f:
                        _ = f.read()
                    os.remove(file_path)
                    time.sleep(0.02)
            except:
                pass
        
        # Inicia threads
        threads = []
        for i in range(2):  # 2 VS Code
            threads.append(threading.Thread(target=vscode_worker, args=(i,)))
        for i in range(2):  # 2 Chrome
            threads.append(threading.Thread(target=chrome_worker, args=(i,)))
        for i in range(2):  # 2 MySQL
            threads.append(threading.Thread(target=mysql_worker, args=(i,)))
        threads.append(threading.Thread(target=multitask_worker))
        
        for t in threads:
            t.start()
        
        # Coleta métricas durante o teste
        self.metrics_history = []
        print("\n⏳ Executando teste...")
        
        try:
            while time.time() - start_time < duration:
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                cpu = psutil.cpu_percent(interval=0.5)
                
                self.metrics_history.append({
                    "cpu": cpu,
                    "memory_percent": mem.percent,
                    "memory_used_gb": round(mem.used / (1024**3), 2),
                    "swap_percent": swap.percent if swap.total > 0 else 0,
                    "swap_used_gb": round(swap.used / (1024**3), 2) if swap.total > 0 else 0
                })
                
                # Mostra progresso
                elapsed = time.time() - start_time
                bar_length = 30
                filled = int((elapsed / duration) * bar_length)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r  [{bar}] {elapsed:.0f}/{duration}s | CPU: {cpu:.1f}% | RAM: {mem.percent:.1f}% | Swap: {swap.percent:.1f}%", end='')
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️ Teste interrompido{Colors.END}")
        
        print()  # Nova linha
        
        # Aguarda threads
        for t in threads:
            t.join(timeout=2)
        
        # ==================== ANÁLISE ====================
        if self.metrics_history:
            avg_cpu = sum(m["cpu"] for m in self.metrics_history) / len(self.metrics_history)
            avg_ram = sum(m["memory_percent"] for m in self.metrics_history) / len(self.metrics_history)
            max_ram = max(m["memory_percent"] for m in self.metrics_history)
            avg_swap = sum(m["swap_percent"] for m in self.metrics_history) / len(self.metrics_history)
            max_swap = max(m["swap_percent"] for m in self.metrics_history)
        else:
            avg_cpu = avg_ram = avg_swap = max_ram = max_swap = 0
        
        self.test_results = {
            "duration": duration,
            "averages": {
                "cpu": round(avg_cpu, 1),
                "memory_percent": round(avg_ram, 1),
                "swap_percent": round(avg_swap, 1)
            },
            "peaks": {
                "memory_percent": round(max_ram, 1),
                "swap_percent": round(max_swap, 1)
            },
            "final": {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": {
                    "percent": psutil.virtual_memory().percent,
                    "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                    "available_gb": round(psutil.virtual_memory().available / (1024**3), 2)
                },
                "swap": {
                    "percent": psutil.swap_memory().percent if psutil.swap_memory().total > 0 else 0,
                    "used_gb": round(psutil.swap_memory().used / (1024**3), 2) if psutil.swap_memory().total > 0 else 0
                }
            }
        }
        
        # Limpeza
        for f in self.work_dir.glob("*"):
            if f.is_file():
                f.unlink()
        
        print(f"\n{Colors.GREEN}✅ Teste concluído!{Colors.END}")
        time.sleep(1)

    def save_results(self):
        """Salva resultados em JSON"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "system": self.system_data,
            "test_results": self.test_results,
            "metrics_history": self.metrics_history
        }
        
        filename = f"benchmark_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Colors.GREEN}✅ Resultados salvos em: {filename}{Colors.END}")

    def run(self):
        """Executa tudo"""
        # Coleta dados do sistema
        self.collect_system_data()
        
        # Exibe dashboard inicial
        self.print_dashboard()
        
        # Pergunta se quer executar teste
        print(f"\n{Colors.BOLD}🚀 Opções:{Colors.END}")
        print("  1. Executar teste de performance completo (recomendado)")
        print("  2. Apenas visualizar dados do sistema")
        
        choice = input(f"\n{Colors.BOLD}Escolha (1/2): {Colors.END}").strip()
        
        if choice == "1":
            self.run_performance_test()
            # Atualiza dashboard com resultados
            self.print_dashboard()
            self.save_results()
        else:
            print(f"\n{Colors.GREEN}✅ Dashboard exibido!{Colors.END}")
        
        print(f"\n{Colors.CYAN}{'='*90}{Colors.END}")
        print(f"{Colors.GREEN}✅ Benchmark concluído!{Colors.END}")

if __name__ == "__main__":
    tester = CompleteBenchmark()
    
    try:
        tester.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Teste interrompido pelo usuário{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro: {e}{Colors.END}")
        import traceback
        traceback.print_exc()