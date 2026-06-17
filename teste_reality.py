#!/usr/bin/env python3
"""
TESTE DE PERFORMANCE REALISTA
Simula o uso real do PC com múltiplas aplicações
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

class RealWorldTest:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        self.work_dir = Path("test_workload")
        self.work_dir.mkdir(exist_ok=True)
        
    def monitor_resources(self, duration=60):
        """Monitora recursos em tempo real durante o teste"""
        print(f"\n📊 Monitorando recursos por {duration}s...")
        
        samples = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            sample = {
                "timestamp": time.time() - start_time,
                "cpu_percent": psutil.cpu_percent(interval=0.5),
                "memory": {
                    "used_gb": psutil.virtual_memory().used / (1024**3),
                    "percent": psutil.virtual_memory().percent
                },
                "swap": {
                    "used_gb": psutil.swap_memory().used / (1024**3),
                    "percent": psutil.swap_memory().percent
                },
                "disk_io": psutil.disk_io_counters()
            }
            samples.append(sample)
            
            # Mostra status a cada 5 segundos
            if int(sample["timestamp"]) % 5 == 0:
                mem_percent = sample["memory"]["percent"]
                swap_used = sample["swap"]["used_gb"]
                print(f"  ⏱️  {int(sample['timestamp'])}s | RAM: {mem_percent}% | Swap: {swap_used:.1f}GB | CPU: {sample['cpu_percent']}%")
        
        return samples

    def simulate_heavy_workload(self):
        """Simula carga pesada real"""
        print("\n" + "="*70)
        print("💻 SIMULANDO USO REAL - CENÁRIO PESADO")
        print("="*70)
        
        # Inicia monitoramento em thread separada
        monitor_thread = threading.Thread(target=self.monitor_resources, args=(60,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("\n🚀 Iniciando simulação de uso real...")
        start_time = time.time()
        
        # 1. SIMULA VS CODE ABERTO
        print("\n📝 [1/4] Abrindo VS Code (edição de arquivos)...")
        vscode_threads = []
        for i in range(3):  # 3 arquivos abertos
            t = threading.Thread(target=self.simulate_vscode, args=(i,))
            t.start()
            vscode_threads.append(t)
        
        # 2. SIMULA MYSQL RODANDO
        print("🗄️  [2/4] Iniciando MySQL (consultas)...")
        mysql_threads = []
        for i in range(2):  # 2 conexões simultâneas
            t = threading.Thread(target=self.simulate_mysql)
            t.start()
            mysql_threads.append(t)
        
        # 3. SIMULA NAVEGADOR (Chrome/Firefox)
        print("🌐 [3/4] Abrindo navegador (várias abas)...")
        browser_threads = []
        for i in range(4):  # 4 abas abertas
            t = threading.Thread(target=self.simulate_browser, args=(i,))
            t.start()
            browser_threads.append(t)
        
        # 4. SIMULA PROCESSOS EM SEGUNDO PLANO
        print("🔄 [4/4] Processos em segundo plano...")
        bg_threads = []
        for i in range(2):
            t = threading.Thread(target=self.simulate_background_process)
            t.start()
            bg_threads.append(t)
        
        # Aguarda conclusão
        all_threads = vscode_threads + mysql_threads + browser_threads + bg_threads
        
        # Monitora enquanto executa
        print("\n⏳ Executando carga por 30 segundos...")
        time.sleep(30)
        
        # Finaliza threads
        print("\n🛑 Finalizando simulação...")
        
        elapsed = time.time() - start_time
        
        # Coleta resultado final
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.results["tests"]["heavy_workload"] = {
            "duration": round(elapsed, 2),
            "final_memory": {
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent,
                "available_gb": round(mem.available / (1024**3), 2)
            },
            "final_swap": {
                "used_gb": round(swap.used / (1024**3), 2),
                "percent": swap.percent
            },
            "cpu_usage": psutil.cpu_percent(interval=1)
        }
        
        # Diagnóstico
        self.diagnose_issues()

    def simulate_vscode(self, file_id):
        """Simula operações do VS Code"""
        try:
            for _ in range(20):
                # Cria/edita arquivo
                file_path = self.work_dir / f"code_{file_id}_{random.randint(1,100)}.txt"
                with open(file_path, 'w') as f:
                    # Simula código
                    for line in range(100):
                        f.write(f"function test{line}() {{\n")
                        f.write("  return true;\n")
                        f.write("}\n\n")
                
                # Lê e processa
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Simula busca/realce de sintaxe
                    _ = content.count("function")
                
                # Deleta após um tempo
                if random.random() > 0.7:
                    os.remove(file_path)
                
                time.sleep(0.05)
        except Exception as e:
            pass

    def simulate_mysql(self):
        """Simula consultas MySQL"""
        try:
            data = list(range(10000))
            for _ in range(50):
                # Simula SELECT
                result = data[random.randint(0, 9999)]
                # Simula JOIN/ORDER BY
                sorted_data = sorted(data[:1000])
                # Simula GROUP BY
                grouped = {}
                for i in range(1000):
                    key = i % 10
                    if key not in grouped:
                        grouped[key] = []
                    grouped[key].append(i)
                time.sleep(0.02)
        except Exception as e:
            pass

    def simulate_browser(self, tab_id):
        """Simula navegador com várias abas"""
        try:
            # Simula carregamento de páginas
            pages = ["https://github.com", "https://stackoverflow.com", 
                    "https://youtube.com", "https://google.com"]
            
            for page in pages:
                # Simula renderização
                data = bytearray(1024 * 1024)  # 1MB por página
                # Simula JavaScript
                for i in range(100):
                    _ = i * i
                time.sleep(0.1)
        except Exception as e:
            pass

    def simulate_background_process(self):
        """Simula processos em segundo plano"""
        try:
            for _ in range(30):
                # Simula antivírus/update checker
                _ = [i for i in range(1000)]
                # Simula compressão de dados
                data = bytearray(1024 * 100)  # 100KB
                time.sleep(0.01)
        except Exception as e:
            pass

    def diagnose_issues(self):
        """Diagnostica gargalos"""
        print("\n" + "="*70)
        print("🔍 DIAGNÓSTICO DE GARGALOS")
        print("="*70)
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        issues = []
        
        # 1. VERIFICA MEMÓRIA
        if mem.percent > 85:
            issues.append({
                "severity": "CRÍTICO",
                "component": "MEMÓRIA RAM",
                "detail": f"Uso de {mem.percent}% (apenas {mem.available/1024**3:.1f}GB livre)",
                "solution": "Aumentar RAM para 16GB ou fechar aplicativos"
            })
        elif mem.percent > 70:
            issues.append({
                "severity": "ALTO",
                "component": "MEMÓRIA RAM",
                "detail": f"Uso de {mem.percent}%",
                "solution": "Considere aumentar RAM para 16GB"
            })
        
        # 2. VERIFICA SWAP
        if swap.used > 0 and swap.percent > 50:
            issues.append({
                "severity": "CRÍTICO",
                "component": "SWAP (DISCO USADO COMO MEMÓRIA)",
                "detail": f"Usando {swap.used/1024**3:.1f}GB de swap ({swap.percent}%)",
                "solution": "RAM insuficiente! O PC está usando o disco como memória (100x mais lento)"
            })
        elif swap.used > 0:
            issues.append({
                "severity": "MÉDIO",
                "component": "SWAP",
                "detail": f"Usando {swap.used/1024**3:.1f}GB de swap",
                "solution": "Fechar aplicativos não utilizados"
            })
        
        # 3. VERIFICA CPU
        if cpu > 80:
            issues.append({
                "severity": "ALTO",
                "component": "CPU",
                "detail": f"Uso de CPU em {cpu}%",
                "solution": "CPU sobrecarregada - verifique processos em segundo plano"
            })
        
        # 4. VERIFICA NÚCLEOS
        cpu_count = psutil.cpu_count()
        if cpu_count <= 2 and cpu > 60:
            issues.append({
                "severity": "ALTO",
                "component": "CPU (POUCOS NÚCLEOS)",
                "detail": f"Apenas {cpu_count} núcleos, uso de {cpu}%",
                "solution": "Processador básico - evite multitarefa pesada"
            })
        
        # Exibe diagnóstico
        if issues:
            print("\n🚨 PROBLEMAS IDENTIFICADOS:\n")
            for issue in issues:
                print(f"  [{issue['severity']}] {issue['component']}")
                print(f"    → {issue['detail']}")
                print(f"    💡 {issue['solution']}\n")
        else:
            print("\n✅ Sistema está saudável!")
        
        # Resumo final
        print("\n📊 RESUMO DO ESTADO ATUAL:")
        print(f"  • RAM: {mem.percent}% usado ({mem.used/1024**3:.1f}GB de {mem.total/1024**3:.1f}GB)")
        print(f"  • Swap: {swap.percent}% usado ({swap.used/1024**3:.1f}GB)")
        print(f"  • CPU: {cpu}%")
        print(f"  • Núcleos: {cpu_count}")
        
        # Avaliação final
        self.rate_performance(mem, swap, cpu)

    def rate_performance(self, mem, swap, cpu):
        """Avalia performance geral"""
        print("\n" + "="*70)
        print("⭐ AVALIAÇÃO DE PERFORMANCE")
        print("="*70)
        
        score = 100
        
        # Penalidades
        if mem.percent > 90:
            score -= 40
        elif mem.percent > 80:
            score -= 20
        elif mem.percent > 70:
            score -= 10
        
        if swap.percent > 50:
            score -= 30
        elif swap.percent > 20:
            score -= 15
        elif swap.percent > 0:
            score -= 5
        
        if cpu > 80:
            score -= 20
        elif cpu > 60:
            score -= 10
        
        if psutil.cpu_count() <= 2:
            score -= 15
        
        # Classificação
        score = max(0, min(100, score))
        
        if score >= 80:
            grade = "🟢 BOM"
            detail = "Sistema funciona bem para tarefas básicas"
        elif score >= 60:
            grade = "🟡 REGULAR"
            detail = "Pode ter lentidão com multitarefa"
        elif score >= 40:
            grade = "🟠 RUIM"
            detail = "Lentidão frequente, especialmente com várias apps"
        else:
            grade = "🔴 CRÍTICO"
            detail = "Sistema sobrecarregado, precisa de upgrade urgente"
        
        print(f"\n  Nota: {score}/100")
        print(f"  Classificação: {grade}")
        print(f"  Status: {detail}")
        
        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        if mem.percent > 80:
            print("  • 🆙 AUMENTAR RAM para 16GB (prioridade #1)")
        if swap.percent > 30:
            print("  • 🗑️  Fechar aplicativos em segundo plano")
        if cpu > 70:
            print("  • 🔍 Identificar processos que consomem CPU (Task Manager)")
        if score < 60:
            print("  • 🔄 Considere usar aplicativos mais leves")
            print("  • 💻 Para multitarefa pesada, recomenda-se upgrade de hardware")
        
        # Salva diagnóstico
        self.results["diagnosis"] = {
            "score": score,
            "grade": grade,
            "issues": issues if 'issues' in locals() else []
        }

    def save_results(self):
        """Salva resultados"""
        filename = f"real_world_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Resultados salvos em: {filename}")

    def run(self):
        """Executa teste"""
        print("="*70)
        print("🚀 TESTE DE PERFORMANCE REALISTA")
        print("="*70)
        print("\n⚠️  Este teste simula uso real de:")
        print("  • VS Code (3 arquivos abertos)")
        print("  • MySQL (2 conexões)")
        print("  • Navegador (4 abas)")
        print("  • Processos em segundo plano")
        print("\nO teste durará aproximadamente 60 segundos.")
        print("Por favor, não use o PC durante o teste.\n")
        
        input("Pressione ENTER para começar...")
        
        self.simulate_heavy_workload()
        self.save_results()
        
        print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test = RealWorldTest()
    test.run()