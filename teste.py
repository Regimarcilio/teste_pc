#!/usr/bin/env python3
"""
Sistema de Benchmark Multiplataforma
Avalia desempenho de CPU, Memória, Disco e Scripts
Compatível com Windows e Linux
"""

import subprocess
import platform
import time
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class SystemBenchmark:
    def __init__(self):
        self.os_type = platform.system()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "os": {
                "system": self.os_type,
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine()
            },
            "benchmarks": {}
        }
    
    def run_command(self, command, shell=True):
        """Executa comando e retorna output"""
        try:
            result = subprocess.run(
                command, 
                shell=shell, 
                capture_output=True, 
                text=True,
                timeout=60
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Erro ao executar {command}: {e}")
            return None
    
    def benchmark_cpu(self):
        """Benchmark de CPU usando sysbench se disponível"""
        print("[1/5] Executando benchmark de CPU...")
        
        # Teste simples de CPU (operação matemática intensiva)
        import time
        start_time = time.time()
        
        # Cálculo intensivo
        result = 0
        for i in range(10_000_000):
            result += i * i
        
        elapsed_time = time.time() - start_time
        
        self.results["benchmarks"]["cpu"] = {
            "time_seconds": round(elapsed_time, 2),
            "operations": "10,000,000 multiplicações",
            "method": "Python puro (multiplicação de inteiros)"
        }
        
        print(f"  ✓ CPU completou em {elapsed_time:.2f} segundos")
    
    def benchmark_memory(self):
        """Benchmark de memória RAM"""
        print("[2/5] Executando benchmark de memória...")
        
        # Teste de alocação/liberação de memória
        import time
        import gc
        
        # Aloca e libera grandes listas
        sizes = [100_000, 500_000, 1_000_000]
        times = []
        
        for size in sizes:
            start_time = time.time()
            data = [i for i in range(size)]
            del data
            gc.collect()
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        self.results["benchmarks"]["memory"] = {
            "avg_alloc_time_seconds": round(avg_time, 4),
            "test_sizes": sizes,
            "method": "Alocação e liberação de listas em Python"
        }
        
        print(f"  ✓ Memória: tempo médio de alocação {avg_time:.4f}s")
    
    def benchmark_disk(self):
        """Benchmark de disco usando dd (Linux) ou comando nativo (Windows)"""
        print("[3/5] Executando benchmark de disco...")
        
        test_file = "benchmark_test.tmp"
        file_sizes = [100, 500]  # MB
        
        results = []
        
        for size_mb in file_sizes:
            if self.os_type == "Windows":
                # Windows: uso de fsutil para criar arquivo
                subprocess.run(f'fsutil file createnew {test_file} {size_mb * 1024 * 1024}', shell=True)
                
                # Leitura
                start_read = time.time()
                with open(test_file, 'rb') as f:
                    f.read()
                read_time = time.time() - start_read
                
            else:  # Linux/Mac
                # Linux: criação com dd
                subprocess.run(f'dd if=/dev/zero of={test_file} bs=1M count={size_mb} status=none', shell=True)
                
                # Leitura
                start_read = time.time()
                with open(test_file, 'rb') as f:
                    f.read()
                read_time = time.time() - start_read
            
            # Limpeza
            os.remove(test_file)
            
            results.append({
                "size_mb": size_mb,
                "read_time_seconds": round(read_time, 2),
                "read_speed_mbps": round(size_mb / read_time, 2)
            })
        
        self.results["benchmarks"]["disk"] = results
        print(f"  ✓ Disco: teste de {file_sizes[0]}MB em {results[0]['read_speed_mbps']:.2f} MB/s")
    
    def benchmark_shell_script(self):
        """Compara desempenho de diferentes shells/scripts"""
        print("[4/5] Executando benchmark de scripts...")
        
        shell_results = {}
        
        # Script para testar (operações repetitivas)
        script_content = """
        # Teste de desempenho
        count=0
        for i in $(seq 1 10000); do
            count=$((count + i))
        done
        echo "Resultado: $count"
        """
        
        if self.os_type == "Windows":
            # PowerShell
            import tempfile
            ps_script = """
            $count = 0
            for ($i=1; $i -le 10000; $i++) {
                $count += $i
            }
            Write-Host "Resultado: $count"
            """
            
            start = time.time()
            subprocess.run(['powershell', '-Command', ps_script], capture_output=True, timeout=30)
            ps_time = time.time() - start
            shell_results["powershell"] = round(ps_time, 3)
            
            # Batch/CMD
            batch_script = """
            @echo off
            setlocal enabledelayedexpansion
            set count=0
            for /l %%i in (1,1,10000) do (
                set /a "count=!count!+%%i"
            )
            echo Resultado: !count!
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
                f.write(batch_script)
                batch_file = f.name
            
            start = time.time()
            subprocess.run([batch_file], capture_output=True, timeout=30)
            batch_time = time.time() - start
            shell_results["batch"] = round(batch_time, 3)
            os.unlink(batch_file)
            
        else:  # Linux
            # Bash
            start = time.time()
            subprocess.run(['bash', '-c', script_content], capture_output=True, timeout=30)
            bash_time = time.time() - start
            shell_results["bash"] = round(bash_time, 3)
            
            # Verificar se Perl está disponível
            perl_script = """
            $count = 0;
            for ($i=1; $i<=10000; $i++) {
                $count += $i;
            }
            print "Resultado: $count\\n";
            """
            
            try:
                start = time.time()
                subprocess.run(['perl', '-e', perl_script], capture_output=True, timeout=30)
                perl_time = time.time() - start
                shell_results["perl"] = round(perl_time, 3)
            except FileNotFoundError:
                shell_results["perl"] = "Não instalado"
        
        self.results["benchmarks"]["shell_scripts"] = shell_results
        
        print(f"  ✓ Scripts executados: {list(shell_results.keys())}")
    
    def benchmark_network(self):
        """Benchmark de rede (simples)"""
        print("[5/5] Executando benchmark de rede...")
        
        import urllib.request
        
        test_urls = [
            "https://www.google.com",
            "https://www.github.com"
        ]
        
        network_results = []
        
        for url in test_urls:
            try:
                start = time.time()
                response = urllib.request.urlopen(url, timeout=10)
                response.read()
                elapsed = time.time() - start
                
                network_results.append({
                    "url": url,
                    "response_time_seconds": round(elapsed, 2),
                    "status": response.getcode()
                })
            except Exception as e:
                network_results.append({
                    "url": url,
                    "error": str(e)
                })
        
        self.results["benchmarks"]["network"] = network_results
        print(f"  ✓ Rede: teste de latência completado")
    
    def detect_hardware(self):
        """Detecta informações básicas de hardware"""
        print("\n🔍 Detectando hardware...")
        
        hardware_info = {}
        
        if self.os_type == "Windows":
            # Windows: usando wmic
            cpu = self.run_command('wmic cpu get name')
            if cpu:
                hardware_info["cpu"] = cpu.split('\n')[1].strip()
            
            ram = self.run_command('wmic memorychip get capacity')
            if ram:
                ram_lines = ram.split('\n')[1:]
                total_ram_gb = sum([int(x.strip()) for x in ram_lines if x.strip()]) / (1024**3)
                hardware_info["ram_gb"] = round(total_ram_gb, 2)
        
        else:  # Linux
            # CPU info
            cpu_info = self.run_command('cat /proc/cpuinfo | grep "model name" | head -1')
            if cpu_info:
                hardware_info["cpu"] = cpu_info.split(':')[1].strip()
            
            # RAM info
            ram_info = self.run_command('free -h | grep Mem')
            if ram_info:
                parts = ram_info.split()
                hardware_info["ram_total"] = parts[1]
            
            # Informações adicionais
            hardware_info["kernel"] = self.run_command('uname -r')
        
        self.results["os"]["hardware"] = hardware_info
        
        for key, value in hardware_info.items():
            print(f"  • {key}: {value}")
    
    def run_all_benchmarks(self):
        """Executa todos os benchmarks"""
        print("=" * 60)
        print(f"🚀 INICIANDO BENCHMARK - {self.os_type}")
        print("=" * 60)
        
        self.detect_hardware()
        print("\n▶️  Executando testes de desempenho:\n")
        
        self.benchmark_cpu()
        self.benchmark_memory()
        self.benchmark_disk()
        self.benchmark_shell_script()
        self.benchmark_network()
        
        self.save_results()
        
    def save_results(self):
        """Salva resultados em arquivo JSON"""
        output_file = f"benchmark_results_{self.os_type.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS RESULTADOS")
        print("=" * 60)
        
        cpu_time = self.results["benchmarks"]["cpu"]["time_seconds"]
        print(f"⏱️  CPU: {cpu_time} segundos")
        
        memory_time = self.results["benchmarks"]["memory"]["avg_alloc_time_seconds"]
        print(f"💾 Memória: {memory_time} segundos (alocação média)")
        
        if self.results["benchmarks"]["disk"]:
            disk_speed = self.results["benchmarks"]["disk"][0]["read_speed_mbps"]
            print(f"💿 Disco: {disk_speed} MB/s (leitura {self.results['benchmarks']['disk'][0]['size_mb']}MB)")
        
        print(f"\n✅ Resultados salvos em: {output_file}")
        
        # Exibir comparativo se houver arquivo anterior
        self.compare_with_previous()

    def compare_with_previous(self):
        """Compara com resultados anteriores (úteis para comparar SOs)"""
        json_files = list(Path('.').glob('benchmark_results_*.json'))
        if len(json_files) >= 2:
            print("\n📈 Comparativo com teste anterior:")
            print("  (Execute este script no Windows e no Linux para comparação)")
            print("  Dica: Use um pendrive ou partição compartilhada para salvar os JSONs")

def main():
    benchmark = SystemBenchmark()
    
    try:
        benchmark.run_all_benchmarks()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante benchmark: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()