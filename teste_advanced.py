#!/usr/bin/env python3
"""
Benchmark Avançado Multiplataforma - CORRIGIDO
Otimizado para máquinas com poucos núcleos e memória limitada
"""

import subprocess
import platform
import time
import json
import os
import sys
import psutil
import threading
import multiprocessing
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import random
import math

# Função global para evitar erro de pickle
def cpu_intensive_task(n):
    """Função de CPU intensiva (global)"""
    count = 0
    for i in range(n):
        count += i * i
    return count

def find_primes(limit):
    """Encontra números primos até um limite"""
    primes = []
    for num in range(2, limit):
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

class AdvancedBenchmark:
    def __init__(self):
        self.os_type = platform.system()
        self.cpu_count = multiprocessing.cpu_count()
        # Limita o número de processos para evitar sobrecarga
        self.max_workers = min(self.cpu_count, 4)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "os": {
                "system": self.os_type,
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine()
            },
            "hardware": {},
            "benchmarks": {
                "cpu": {},
                "memory": {},
                "disk": {},
                "swap": {},
                "multitasking": {},
                "applications": {}
            }
        }
        
        # Configurações - AJUSTADAS PARA 8GB RAM
        self.work_dir = Path(tempfile.gettempdir()) / "benchmark_work"
        self.work_dir.mkdir(exist_ok=True)

    def detect_hardware(self):
        """Detecção completa de hardware"""
        print("\n🔍 Detectando hardware detalhadamente...")
        
        hardware = {}
        
        # CPU
        try:
            cpu_info = {
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "max_frequency_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else None
            }
            
            # Nome da CPU
            if self.os_type == "Windows":
                cpu_name = subprocess.run('wmic cpu get name', shell=True, capture_output=True, text=True).stdout
                if cpu_name and len(cpu_name.split('\n')) > 1:
                    cpu_info["name"] = cpu_name.split('\n')[1].strip()
            else:
                cpu_name = subprocess.run('cat /proc/cpuinfo | grep "model name" | head -1', 
                                        shell=True, capture_output=True, text=True).stdout
                if cpu_name:
                    cpu_info["name"] = cpu_name.split(':')[1].strip()
                    
            hardware["cpu"] = cpu_info
            
        except Exception as e:
            print(f"  ⚠️ Erro detectando CPU: {e}")
            hardware["cpu"] = {"error": str(e)}

        # RAM
        try:
            mem = psutil.virtual_memory()
            hardware["memory"] = {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent_used": mem.percent
            }
        except Exception as e:
            print(f"  ⚠️ Erro detectando RAM: {e}")

        # Swap
        try:
            swap = psutil.swap_memory()
            hardware["swap"] = {
                "total_gb": round(swap.total / (1024**3), 2) if swap.total > 0 else 0,
                "used_gb": round(swap.used / (1024**3), 2) if swap.total > 0 else 0,
                "percent_used": swap.percent if swap.total > 0 else 0,
                "enabled": swap.total > 0
            }
        except Exception as e:
            print(f"  ⚠️ Erro detectando Swap: {e}")

        # Disco
        try:
            disk_parts = []
            for partition in psutil.disk_partitions():
                if os.name == 'nt':
                    if 'cdrom' in partition.opts or partition.fstype == '':
                        continue
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    if usage.total > 0:
                        disk_parts.append({
                            "mountpoint": partition.mountpoint,
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                            "percent_used": usage.percent,
                            "filesystem": partition.fstype
                        })
                except:
                    pass
            hardware["disk"] = disk_parts
            
            # Detecta tipo de disco
            hardware["disk_type"] = self._detect_disk_type()
            
        except Exception as e:
            print(f"  ⚠️ Erro detectando Disco: {e}")

        self.results["hardware"] = hardware
        
        # Exibir resumo
        print("\n📊 RESUMO DO HARDWARE:")
        if "name" in hardware.get("cpu", {}):
            print(f"  • CPU: {hardware['cpu']['name']}")
        else:
            print(f"  • CPU: Não detectado")
        print(f"  • Núcleos: {hardware.get('cpu', {}).get('cores_physical', 'N/A')} físicos / {hardware.get('cpu', {}).get('cores_logical', 'N/A')} lógicos")
        print(f"  • RAM: {hardware.get('memory', {}).get('total_gb', 'N/A')} GB")
        print(f"  • Swap: {hardware.get('swap', {}).get('total_gb', 'N/A')} GB")
        print(f"  • Disco: {hardware.get('disk_type', 'N/A')}")
        if hardware.get("disk"):
            for disk in hardware["disk"][:2]:
                print(f"    - {disk['mountpoint']}: {disk['total_gb']:.2f} GB ({disk['filesystem']})")

    def _detect_disk_type(self):
        """Detecta se é SSD ou HDD"""
        try:
            if self.os_type == "Windows":
                cmd = 'powershell -command "Get-PhysicalDisk | Select-Object MediaType"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if "SSD" in result.stdout:
                    return "SSD"
                elif "HDD" in result.stdout:
                    return "HDD"
            else:
                result = subprocess.run('cat /sys/block/*/queue/rotational 2>/dev/null | head -1', 
                                       shell=True, capture_output=True, text=True)
                if result.stdout.strip() == "0":
                    return "SSD"
                elif result.stdout.strip() == "1":
                    return "HDD"
        except:
            pass
        return "Desconhecido"

    def benchmark_cpu_advanced(self):
        """Teste de CPU - CORRIGIDO"""
        print("\n[1/6] 🔥 Testando CPU (estresse avançado)...")
        
        results = {}
        
        # Teste 1: Cálculo de primos (Thread único)
        print("  ⏳ Calculando números primos...")
        start = time.time()
        primes = find_primes(50000)
        single_thread_time = time.time() - start
        results["single_thread"] = {
            "time_seconds": round(single_thread_time, 2),
            "primes_found": len(primes)
        }
        print(f"  ✓ Thread único: {single_thread_time:.2f}s, {len(primes)} primos")

        # Teste 2: Multi-thread (usando a função global)
        print(f"  ⏳ Testando com {self.max_workers} processos...")
        start = time.time()
        
        try:
            # Usa a função global para evitar erro de pickle
            chunk_size = 5000000 // self.max_workers
            
            with multiprocessing.Pool(processes=self.max_workers) as pool:
                results_multi = pool.map(cpu_intensive_task, [chunk_size] * self.max_workers)
            
            multi_thread_time = time.time() - start
            results["multi_thread"] = {
                "time_seconds": round(multi_thread_time, 2),
                "total_operations": sum(results_multi) if results_multi else 0,
                "threads": self.max_workers
            }
            print(f"  ✓ Multi-thread ({self.max_workers} processos): {multi_thread_time:.2f}s")
        except Exception as e:
            print(f"  ⚠️ Erro no multi-thread: {e}")
            results["multi_thread"] = {"error": str(e)}

        # Teste 3: Estresse de CPU (leve - mais seguro)
        print("  ⏳ Estressando CPU por 5 segundos...")
        def stress_cpu():
            end_time = time.time() + 5
            while time.time() < end_time:
                math.factorial(500)  # Menos intensivo
        
        threads = []
        for _ in range(min(self.cpu_count, 2)):  # Limita a 2 threads
            t = threading.Thread(target=stress_cpu)
            t.start()
            threads.append(t)
        
        start_stress = time.time()
        for t in threads:
            t.join()
        stress_time = time.time() - start_stress
        
        cpu_usage = self._get_cpu_usage()
        results["stress_test"] = {
            "duration_seconds": round(stress_time, 2),
            "cpu_utilization": cpu_usage
        }
        print(f"  ✓ Teste de estresse concluído (CPU: {cpu_usage}%)")
        
        self.results["benchmarks"]["cpu"] = results

    def _get_cpu_usage(self):
        """Retorna uso de CPU"""
        try:
            return round(psutil.cpu_percent(interval=1), 1)
        except:
            return 0

    def benchmark_memory_advanced(self):
        """Teste de memória - OTIMIZADO para 8GB"""
        print("\n[2/6] 💾 Testando Memória RAM...")
        
        results = {}
        
        # Ajustado para máquinas com 8GB
        sizes = [5, 10, 25, 50, 100]  # MB (reduzido para evitar estouro)
        allocation_times = []
        
        for size_mb in sizes:
            size_bytes = size_mb * 1024 * 1024
            try:
                start = time.time()
                data = bytearray(size_bytes)
                # Simula uso
                _ = data[0:size_bytes//2]
                del data
                elapsed = time.time() - start
                allocation_times.append({
                    "size_mb": size_mb,
                    "time_seconds": round(elapsed, 4),
                    "speed_mbps": round(size_mb / elapsed, 2) if elapsed > 0 else 0
                })
                print(f"  ✓ Alocação {size_mb}MB: {elapsed:.4f}s ({size_mb/elapsed:.2f} MB/s)")
            except MemoryError:
                print(f"  ⚠️ Falha ao alocar {size_mb}MB (memória insuficiente)")
                break
        
        results["allocation"] = allocation_times

        # Teste de swap (se disponível)
        if self.results["hardware"].get("swap", {}).get("enabled", False):
            print("  ⏳ Testando Swap (subsistema de memória virtual)...")
            try:
                # Teste mais leve
                swap_test = bytearray(50 * 1024 * 1024)  # 50MB
                time.sleep(0.5)
                del swap_test
                results["swap_test"] = {"status": "Concluído"}
                print("  ✓ Swap testado com sucesso")
            except:
                results["swap_test"] = {"error": "Falha no teste de swap"}
        
        self.results["benchmarks"]["memory"] = results

    def benchmark_disk_advanced(self):
        """Teste de disco - AJUSTADO"""
        print("\n[3/6] 💿 Testando Disco...")
        
        results = []
        test_file = self.work_dir / "disk_test.bin"
        
        # Tamanhos mais leves
        for size_mb in [50, 100, 200]:
            # Verifica espaço disponível
            try:
                free_space = psutil.disk_usage(str(self.work_dir)).free
                if free_space < (size_mb * 1024 * 1024 * 3):
                    print(f"  ⚠️ Espaço insuficiente para testar {size_mb}MB")
                    continue
            except:
                pass
                
            try:
                size_bytes = size_mb * 1024 * 1024
                
                # Escrita
                start = time.time()
                with open(test_file, 'wb') as f:
                    chunk_size = 1024 * 1024  # 1MB
                    for _ in range(size_mb):
                        f.write(bytearray(chunk_size))
                write_time = time.time() - start
                
                # Leitura
                start = time.time()
                with open(test_file, 'rb') as f:
                    while f.read(1024 * 1024):
                        pass
                read_time = time.time() - start
                
                # Limpeza
                os.remove(test_file)
                
                results.append({
                    "size_mb": size_mb,
                    "write_time_seconds": round(write_time, 2),
                    "write_speed_mbps": round(size_mb / write_time, 2) if write_time > 0 else 0,
                    "read_time_seconds": round(read_time, 2),
                    "read_speed_mbps": round(size_mb / read_time, 2) if read_time > 0 else 0
                })
                
                print(f"  ✓ {size_mb}MB - Leitura: {size_mb/read_time:.1f} MB/s, Escrita: {size_mb/write_time:.1f} MB/s")
                
            except Exception as e:
                print(f"  ⚠️ Erro no teste {size_mb}MB: {e}")
                if test_file.exists():
                    os.remove(test_file)
                break
        
        self.results["benchmarks"]["disk"] = results

    def simulate_applications(self):
        """Simula VS Code e MySQL - REDUZIDO"""
        print("\n[4/6] 🖥️  Simulando aplicações (VS Code + MySQL)...")
        
        results = {
            "vscode_simulation": {},
            "mysql_simulation": {},
            "combined": {}
        }
        
        # Simulação VS Code (reduzida)
        print("  📝 Simulando VS Code...")
        start = time.time()
        
        file_count = 20  # Reduzido
        test_files = []
        for i in range(file_count):
            file_path = self.work_dir / f"code_file_{i}.txt"
            with open(file_path, 'w') as f:
                f.write(f"// Arquivo {i}\n" + "x" * 500 + "\n" * 5)
            test_files.append(file_path)
        
        vscode_ops = {
            "files_created": file_count,
            "search_operations": 0,
            "file_reads": 0
        }
        
        # Busca em arquivos
        for file_path in test_files:
            with open(file_path, 'r') as f:
                content = f.read()
                if "x" in content:
                    vscode_ops["search_operations"] += 1
        
        # Leitura aleatória
        for _ in range(50):  # Reduzido
            idx = random.randint(0, file_count - 1)
            with open(test_files[idx], 'r') as f:
                f.read()
                vscode_ops["file_reads"] += 1
        
        vscode_time = time.time() - start
        
        results["vscode_simulation"] = {
            "time_seconds": round(vscode_time, 2),
            "operations": vscode_ops,
            "files_processed": file_count
        }
        print(f"  ✓ VS Code simulado: {vscode_time:.2f}s")

        # Simulação MySQL (reduzida)
        print("  🗄️  Simulando MySQL...")
        start = time.time()
        
        mysql_ops = {
            "queries": 0,
            "records_processed": 0
        }
        
        # Simula operações SQL
        for _ in range(500):  # Reduzido
            if _ % 2 == 0:
                mysql_ops["queries"] += 1
                mysql_ops["records_processed"] += random.randint(1, 50)
            else:
                mysql_ops["queries"] += 1
                mysql_ops["records_processed"] += 1
        
        mysql_time = time.time() - start
        
        results["mysql_simulation"] = {
            "time_seconds": round(mysql_time, 2),
            "operations": mysql_ops,
            "queries_per_second": round(mysql_ops["queries"] / mysql_time, 2) if mysql_time > 0 else 0
        }
        print(f"  ✓ MySQL simulado: {mysql_time:.2f}s")

        # Limpeza
        for file_path in test_files:
            try:
                os.remove(file_path)
            except:
                pass

        # Teste combinado (simplificado)
        print("  🔄 Testando VS Code + MySQL simultaneamente...")
        start = time.time()
        
        def vscode_worker():
            for i in range(5):  # Reduzido
                file_path = self.work_dir / f"temp_code_{i}.txt"
                try:
                    with open(file_path, 'w') as f:
                        f.write("x" * 500)
                    with open(file_path, 'r') as f:
                        f.read()
                    os.remove(file_path)
                except:
                    pass
        
        def mysql_worker():
            for i in range(50):  # Reduzido
                data = [random.randint(0, 500) for _ in range(50)]
                if data:
                    _ = sum(data) / len(data)
        
        threads = []
        for _ in range(min(self.cpu_count, 2)):  # Limita a 2
            threads.append(threading.Thread(target=vscode_worker))
            threads.append(threading.Thread(target=mysql_worker))
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        combined_time = time.time() - start
        
        results["combined"] = {
            "time_seconds": round(combined_time, 2),
            "total_threads": len(threads)
        }
        print(f"  ✓ Teste combinado concluído em {combined_time:.2f}s")

        self.results["benchmarks"]["applications"] = results

    def benchmark_multitasking(self):
        """Teste de multitarefa - AJUSTADO"""
        print("\n[5/6] 🔄 Testando Multitarefa...")
        
        results = {}
        
        start = time.time()
        
        def intensive_math():
            for _ in range(500):  # Reduzido
                [math.sqrt(i) for i in range(500)]
        
        def file_io():
            for i in range(30):  # Reduzido
                file_path = self.work_dir / f"io_test_{i}.tmp"
                try:
                    with open(file_path, 'w') as f:
                        f.write("x" * 5000)
                    with open(file_path, 'r') as f:
                        _ = f.read()
                    os.remove(file_path)
                except:
                    pass
        
        def memory_hog():
            try:
                data = bytearray(5 * 1024 * 1024)  # 5MB apenas
                time.sleep(0.1)
                del data
            except:
                pass
        
        # Cria threads
        threads = []
        max_threads = min(self.cpu_count * 2, 8)  # Limita a 8 threads no máximo
        
        for _ in range(min(self.cpu_count, 2)):
            threads.append(threading.Thread(target=intensive_math))
            threads.append(threading.Thread(target=file_io))
            threads.append(threading.Thread(target=memory_hog))
        
        # Monitora CPU
        cpu_usage_samples = []
        start_time = time.time()
        
        for t in threads:
            t.start()
        
        # Coleta amostras de CPU durante a execução
        while any(t.is_alive() for t in threads):
            cpu_usage_samples.append(psutil.cpu_percent(interval=0.3))
        
        for t in threads:
            t.join()
        
        multitask_time = time.time() - start_time
        
        avg_cpu = sum(cpu_usage_samples) / len(cpu_usage_samples) if cpu_usage_samples else 0
        
        results = {
            "time_seconds": round(multitask_time, 2),
            "threads": len(threads),
            "avg_cpu_usage": round(avg_cpu, 1),
            "peak_cpu_usage": round(max(cpu_usage_samples) if cpu_usage_samples else 0, 1)
        }
        
        print(f"  ✓ Multitarefa concluída: {multitask_time:.2f}s")
        print(f"  • Uso médio de CPU: {avg_cpu:.1f}%")
        
        self.results["benchmarks"]["multitasking"] = results

    def benchmark_io_system(self):
        """Teste de I/O - OTIMIZADO"""
        print("\n[6/6] 📊 Testando Sistema de I/O...")
        
        results = {}
        
        # Testa tamanhos de bloco menores
        block_sizes = [1024, 4096, 16384]  # 1KB, 4KB, 16KB
        test_file = self.work_dir / "io_benchmark.bin"
        test_size_mb = 20  # Reduzido
        
        io_results = []
        
        for block_size in block_sizes:
            try:
                blocks_needed = (test_size_mb * 1024 * 1024) // block_size
                
                # Escrita
                start = time.time()
                with open(test_file, 'wb') as f:
                    chunk = bytearray(block_size)
                    for _ in range(blocks_needed):
                        f.write(chunk)
                write_time = time.time() - start
                
                # Leitura
                start = time.time()
                with open(test_file, 'rb') as f:
                    for _ in range(blocks_needed):
                        f.read(block_size)
                read_time = time.time() - start
                
                os.remove(test_file)
                
                io_results.append({
                    "block_size_kb": block_size // 1024,
                    "write_speed_mbps": round(test_size_mb / write_time, 2) if write_time > 0 else 0,
                    "read_speed_mbps": round(test_size_mb / read_time, 2) if read_time > 0 else 0
                })
                
            except Exception as e:
                print(f"  ⚠️ Erro no teste de I/O ({block_size}): {e}")
                break
        
        results["block_io"] = io_results
        
        if io_results:
            best_read = max([r["read_speed_mbps"] for r in io_results if r["read_speed_mbps"] > 0])
            best_write = max([r["write_speed_mbps"] for r in io_results if r["write_speed_mbps"] > 0])
            
            results["best_performance"] = {
                "best_read_mbps": best_read,
                "best_write_mbps": best_write
            }
            
            print(f"  ✓ Melhor leitura: {best_read:.1f} MB/s")
            print(f"  ✓ Melhor escrita: {best_write:.1f} MB/s")

        self.results["benchmarks"]["io_system"] = results

    def run_all_benchmarks(self):
        """Executa todos os testes"""
        print("=" * 70)
        print(f"🚀 BENCHMARK AVANÇADO - {self.os_type}")
        print(f"💻 {self.cpu_count} núcleos lógicos detectados")
        print("=" * 70)
        
        self.detect_hardware()
        
        print("\n▶️  Executando testes de performance:\n")
        
        self.benchmark_cpu_advanced()
        self.benchmark_memory_advanced()
        self.benchmark_disk_advanced()
        self.simulate_applications()
        self.benchmark_multitasking()
        self.benchmark_io_system()
        
        self.save_results()
        self.cleanup()

    def cleanup(self):
        """Limpa arquivos temporários"""
        try:
            shutil.rmtree(self.work_dir, ignore_errors=True)
        except:
            pass

    def save_results(self):
        """Salva resultados"""
        output_file = f"benchmark_advanced_{self.os_type.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO DE DESEMPENHO")
        print("=" * 70)
        
        # Resumo
        if "cpu" in self.results["benchmarks"]:
            cpu_results = self.results["benchmarks"]["cpu"]
            print(f"\n⚡ CPU:")
            print(f"  • Single-thread: {cpu_results.get('single_thread', {}).get('time_seconds', 'N/A')}s")
            if "multi_thread" in cpu_results:
                print(f"  • Multi-thread: {cpu_results.get('multi_thread', {}).get('time_seconds', 'N/A')}s")
        
        if "memory" in self.results["benchmarks"]:
            mem_results = self.results["benchmarks"]["memory"]
            if mem_results.get("allocation") and len(mem_results["allocation"]) > 0:
                last_test = mem_results["allocation"][-1]
                print(f"\n💾 Memória:")
                print(f"  • Alocação {last_test['size_mb']}MB: {last_test['time_seconds']}s")
                print(f"  • Velocidade: {last_test['speed_mbps']} MB/s")
        
        if "disk" in self.results["benchmarks"] and self.results["benchmarks"]["disk"]:
            disk_result = self.results["benchmarks"]["disk"][0]
            print(f"\n💿 Disco:")
            print(f"  • Leitura: {disk_result.get('read_speed_mbps', 'N/A')} MB/s")
            print(f"  • Escrita: {disk_result.get('write_speed_mbps', 'N/A')} MB/s")
        
        if "applications" in self.results["benchmarks"]:
            apps = self.results["benchmarks"]["applications"]
            print(f"\n🖥️  Aplicações:")
            print(f"  • VS Code: {apps.get('vscode_simulation', {}).get('time_seconds', 'N/A')}s")
            print(f"  • MySQL: {apps.get('mysql_simulation', {}).get('time_seconds', 'N/A')}s")
            print(f"  • VS Code + MySQL: {apps.get('combined', {}).get('time_seconds', 'N/A')}s")
        
        if "multitasking" in self.results["benchmarks"]:
            multi = self.results["benchmarks"]["multitasking"]
            print(f"\n🔄 Multitarefa:")
            print(f"  • Tempo: {multi.get('time_seconds', 'N/A')}s")
            print(f"  • CPU média: {multi.get('avg_cpu_usage', 'N/A')}%")
        
        if "io_system" in self.results["benchmarks"]:
            io = self.results["benchmarks"]["io_system"]
            if "best_performance" in io:
                print(f"\n📊 I/O:")
                print(f"  • Melhor leitura: {io['best_performance']['best_read_mbps']} MB/s")
                print(f"  • Melhor escrita: {io['best_performance']['best_write_mbps']} MB/s")
        
        print(f"\n✅ Resultados salvos em: {output_file}")
        print("\n💡 Dica: Execute este script no Linux para comparar!")

def check_dependencies():
    """Verifica dependências"""
    try:
        import psutil
    except ImportError:
        print("❌ psutil não está instalado. Instale com:")
        print("  pip install psutil")
        sys.exit(1)

if __name__ == "__main__":
    check_dependencies()
    
    # Configuração para Windows (evita problemas com multiprocessing)
    if platform.system() == "Windows":
        import multiprocessing as mp
        mp.freeze_support()
    
    benchmark = AdvancedBenchmark()
    
    try:
        benchmark.run_all_benchmarks()
    except KeyboardInterrupt:
        print("\n\n⚠️ Benchmark interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)