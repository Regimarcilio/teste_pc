#!/usr/bin/env python3
"""
TESTE REALISTA - SIMULA USO REAL DE PRODUÇÃO
Mede exatamente o que você sente no dia a dia
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

class RealWorldTestV2:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios": {}
        }
        self.work_dir = Path("test_workload_real")
        self.work_dir.mkdir(exist_ok=True)
        
        # SIMULA USO REAL DE VERDADE
        self.vscode_files = 15  # 15 arquivos abertos
        self.chrome_tabs = 12   # 12 abas
        self.mysql_queries = 2000  # 2000 consultas
        self.duration = 120     # 2 minutos de teste

    def create_real_workload(self):
        """Cria carga REALÍSTICA"""
        print("\n" + "="*70)
        print("💻 TESTE REALISTA V2 - USO DE PRODUÇÃO")
        print("="*70)
        
        print(f"\n📋 Cenário:")
        print(f"  • VS Code: {self.vscode_files} arquivos abertos")
        print(f"  • Chrome: {self.chrome_tabs} abas")
        print(f"  • MySQL: {self.mysql_queries} consultas")
        print(f"  • Duração: {self.duration}s")
        print("\n⏳ Preparando...")
        
        # Limpa arquivos antigos
        for f in self.work_dir.glob("*.txt"):
            f.unlink()
        for f in self.work_dir.glob("*.tmp"):
            f.unlink()
        
        print("🚀 Iniciando teste REAL...\n")
        start_time = time.time()
        
        # 1. CRIA ARQUIVOS GRANDES (simula projetos reais)
        print("[1/5] Criando arquivos de projeto (arquivos grandes)...")
        big_files = []
        for i in range(self.vscode_files):
            file_path = self.work_dir / f"projeto_{i}.txt"
            with open(file_path, 'w') as f:
                # Arquivo de 100KB - 500KB (código real)
                size_kb = random.randint(100, 500)
                for _ in range(size_kb):
                    f.write(f"linha_{random.randint(1,1000)}: " + "x" * random.randint(10, 100) + "\n")
            big_files.append(file_path)
        print(f"  ✓ {len(big_files)} arquivos criados")
        
        # 2. SIMULA VS CODE (EDIÇÃO REAL)
        print("[2/5] Simulando VS Code (edição, busca, indexação)...")
        vscode_start = time.time()
        vscode_ops = 0
        
        # Simula digitação
        for i in range(50):  # 50 edições
            file = random.choice(big_files)
            with open(file, 'a') as f:
                f.write(f"// Nova função {i}\n")
                f.write("function process_data() {\n")
                f.write("  const result = [];\n")
                f.write("  for (let i = 0; i < 1000; i++) {\n")
                f.write("    result.push(i * 2);\n")
                f.write("  }\n")
                f.write("  return result;\n")
                f.write("}\n\n")
            vscode_ops += 1
            
            # Simula busca no projeto
            if i % 3 == 0:
                for file2 in random.sample(big_files, min(5, len(big_files))):
                    with open(file2, 'r') as f:
                        content = f.read()
                        _ = content.count("function")
                    vscode_ops += 1
            
            time.sleep(0.02)
        
        vscode_time = time.time() - vscode_start
        print(f"  ✓ VS Code: {vscode_time:.1f}s, {vscode_ops} operações")
        
        # 3. SIMULA CHROME (MÚLTIPLAS ABAS)
        print("[3/5] Simulando Chrome ({self.chrome_tabs} abas)...")
        chrome_start = time.time()
        chrome_ops = 0
        
        # Dados para simular páginas pesadas
        pages_data = []
        for i in range(self.chrome_tabs):
            # Cada aba tem 5-20MB de dados
            page_mb = random.randint(5, 20)
            page_data = bytearray(page_mb * 1024 * 1024)
            pages_data.append(page_data)
            chrome_ops += 1
            
            # Simula renderização
            time.sleep(0.01)
        
        # Simula scroll e interação
        for _ in range(100):
            tab = random.randint(0, self.chrome_tabs - 1)
            # Simula renderização de DOM
            _ = [i * i for i in range(5000)]
            chrome_ops += 1
            time.sleep(0.001)
        
        chrome_time = time.time() - chrome_start
        print(f"  ✓ Chrome: {chrome_time:.1f}s, {chrome_ops} operações")
        
        # 4. SIMULA MYSQL (CONSULTAS PESADAS)
        print(f"[4/5] Simulando MySQL ({self.mysql_queries} consultas)...")
        mysql_start = time.time()
        
        # Cria dados para simular banco
        data = {
            "users": [{"id": i, "name": f"user_{i}", "email": f"user{i}@test.com"} for i in range(10000)],
            "orders": [{"id": i, "user_id": random.randint(1, 1000), "value": random.random() * 1000} for i in range(50000)]
        }
        
        mysql_ops = 0
        for i in range(self.mysql_queries):
            # Simula SELECT complexo
            if i % 4 == 0:
                # JOIN entre tabelas
                result = []
                for user in data["users"][:1000]:
                    for order in data["orders"][:1000]:
                        if order["user_id"] == user["id"]:
                            result.append({**user, **order})
            elif i % 4 == 1:
                # GROUP BY com agregação
                totals = {}
                for order in data["orders"][:2000]:
                    key = order["user_id"]
                    if key not in totals:
                        totals[key] = 0
                    totals[key] += order["value"]
            elif i % 4 == 2:
                # ORDER BY com sorting
                sorted_users = sorted(data["users"][:5000], key=lambda x: x["name"])
            else:
                # UPDATE/INSERT
                data["users"].append({"id": len(data["users"]) + 1, "name": f"new_{i}", "email": f"new{i}@test.com"})
            
            mysql_ops += 1
            
            # A cada 100 queries, mostra progresso
            if i % 100 == 0:
                print(f"    ➜ {i}/{self.mysql_queries} queries...", end="\r")
        
        mysql_time = time.time() - mysql_start
        print(f"\n  ✓ MySQL: {mysql_time:.1f}s, {mysql_ops} consultas")
        
        # 5. MULTITAREFA SIMULTÂNEA
        print("[5/5] Testando multitarefa simultânea (VS Code + Chrome + MySQL)...")
        multitask_start = time.time()
        
        def heavy_operation():
            # Simula operação pesada
            for _ in range(10):
                _ = [math.sqrt(i) for i in range(10000)]
                time.sleep(0.001)
        
        threads = []
        # 6 threads simultâneas (simulando várias apps)
        for _ in range(6):
            t = threading.Thread(target=heavy_operation)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        multitask_time = time.time() - multitask_start
        print(f"  ✓ Multitarefa concluída: {multitask_time:.2f}s")
        
        total_time = time.time() - start_time
        
        # COLETA RESULTADOS FINAIS
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        # MEDE O QUE IMPORTAA - TEMPO DE RESPOSTA
        response_times = self.measure_response_times()
        
        self.results["scenarios"]["real_workload"] = {
            "total_duration": round(total_time, 2),
            "components": {
                "vscode": {
                    "time": round(vscode_time, 2),
                    "operations": vscode_ops,
                    "files": len(big_files)
                },
                "chrome": {
                    "time": round(chrome_time, 2),
                    "tabs": self.chrome_tabs,
                    "memory_mb": sum([len(p) for p in pages_data]) / (1024*1024)
                },
                "mysql": {
                    "time": round(mysql_time, 2),
                    "queries": mysql_ops,
                    "records": len(data["users"]) + len(data["orders"])
                },
                "multitasking": {
                    "time": round(multitask_time, 2),
                    "threads": 6
                }
            },
            "system_state": {
                "memory": {
                    "used_gb": round(mem.used / (1024**3), 2),
                    "available_gb": round(mem.available / (1024**3), 2),
                    "percent": mem.percent
                },
                "swap": {
                    "used_gb": round(swap.used / (1024**3), 2),
                    "percent": swap.percent
                },
                "cpu_percent": cpu,
                "response_times": response_times
            }
        }
        
        # DIAGNÓSTICO REAL
        self.diagnose_real_performance(mem, swap, cpu, response_times)
        
        # Limpeza
        for f in self.work_dir.glob("*"):
            if f.is_file():
                f.unlink()

    def measure_response_times(self):
        """Mede tempos de resposta REALISTAS"""
        print("\n⏱️  Medindo tempos de resposta...")
        
        response_times = {}
        
        # 1. Abrir arquivo pequeno
        test_file = self.work_dir / "response_test.txt"
        with open(test_file, 'w') as f:
            f.write("x" * 1000)
        
        start = time.time()
        with open(test_file, 'r') as f:
            _ = f.read()
        response_times["file_open_small"] = round((time.time() - start) * 1000, 2)  # ms
        
        # 2. Abrir arquivo grande
        big_file = self.work_dir / "response_test_big.txt"
        with open(big_file, 'w') as f:
            for _ in range(10000):
                f.write("x" * 100 + "\n")
        
        start = time.time()
        with open(big_file, 'r') as f:
            _ = f.read()
        response_times["file_open_large"] = round((time.time() - start) * 1000, 2)  # ms
        
        # 3. Processamento simples
        start = time.time()
        _ = [i * i for i in range(100000)]
        response_times["cpu_calculation"] = round((time.time() - start) * 1000, 2)  # ms
        
        # 4. Alocação de memória
        start = time.time()
        data = bytearray(10 * 1024 * 1024)
        del data
        response_times["memory_allocation"] = round((time.time() - start) * 1000, 2)  # ms
        
        # 5. Operação de disco
        disk_file = self.work_dir / "disk_test.tmp"
        start = time.time()
        with open(disk_file, 'wb') as f:
            f.write(bytearray(5 * 1024 * 1024))
        with open(disk_file, 'rb') as f:
            _ = f.read()
        os.remove(disk_file)
        response_times["disk_io"] = round((time.time() - start) * 1000, 2)  # ms
        
        # Limpeza
        os.remove(test_file)
        os.remove(big_file)
        
        print("  ✓ Medições concluídas")
        return response_times

    def diagnose_real_performance(self, mem, swap, cpu, response_times):
        """Diagnóstico REALISTA baseado no USO REAL"""
        print("\n" + "="*70)
        print("🔍 DIAGNÓSTICO DE PERFORMANCE REAL")
        print("="*70)
        
        issues = []
        warnings = []
        
        # 1. ANÁLISE DE MEMÓRIA (com base no uso real)
        if mem.percent > 85:
            issues.append(f"🚨 CRÍTICO: RAM em {mem.percent}% (apenas {mem.available/1024**3:.1f}GB livre)")
            issues.append(f"   → Com VS Code + Chrome + MySQL, você NÃO tem memória suficiente")
            issues.append(f"   → Solução: AUMENTAR RAM para 16GB (prioridade máxima)")
        elif mem.percent > 75:
            warnings.append(f"⚠️ ALTO: RAM em {mem.percent}%")
            warnings.append(f"   → Com multitarefa pesada, vai começar a usar swap e travar")
            warnings.append(f"   → Solução: Considerar upgrade para 16GB")
        elif mem.percent > 65:
            warnings.append(f"⚠️ MÉDIO: RAM em {mem.percent}%")
            warnings.append(f"   → Use com cuidado, evite muitas abas abertas")
        
        # 2. ANÁLISE DE SWAP
        if swap.used > 0:
            issues.append(f"🚨 CRÍTICO: Usando SWAP ({swap.used/1024**3:.1f}GB)")
            issues.append(f"   → RAM insuficiente! O PC está usando DISCO como memória")
            issues.append(f"   → Isso é 100x mais LENTO que RAM!")
            issues.append(f"   → SOLUÇÃO: AUMENTAR RAM para 16GB URGENTE")
        elif swap.percent > 10:
            warnings.append(f"⚠️ SWAP: {swap.percent}% usado")
            warnings.append(f"   → Sinal de que a RAM está sendo exigida")
        
        # 3. ANÁLISE DE CPU (POUCOS NÚCLEOS)
        cpu_count = psutil.cpu_count()
        if cpu_count <= 2 and cpu > 60:
            issues.append(f"🚨 CRÍTICO: CPU com {cpu_count} núcleos - uso em {cpu}%")
            issues.append(f"   → Processador básico NÃO aguenta multitarefa pesada")
            issues.append(f"   → Solução: Fechar apps, usar menos abas")
        
        # 4. ANÁLISE DE TEMPOS DE RESPOSTA
        # O QUE VOCÊ SENTE NO DIA A DIA
        response_issues = []
        
        if response_times.get("file_open_large", 0) > 100:
            response_issues.append(f"   • Arquivos grandes demoram {response_times['file_open_large']:.0f}ms para abrir (lento)")
        
        if response_times.get("cpu_calculation", 0) > 50:
            response_issues.append(f"   • Cálculos simples demoram {response_times['cpu_calculation']:.0f}ms (processador lento)")
        
        if response_times.get("memory_allocation", 0) > 20:
            response_issues.append(f"   • Alocação de memória demora {response_times['memory_allocation']:.0f}ms (RAM lenta)")
        
        if response_times.get("disk_io", 0) > 50:
            response_issues.append(f"   • I/O de disco demora {response_times['disk_io']:.0f}ms (SSD pode estar cheio ou lento)")
        
        if response_issues:
            warnings.append("⏱️ TEMPOS DE RESPOSTA (o que você sente):")
            warnings.extend(response_issues)
        
        # 5. EXIBE DIAGNÓSTICO
        if issues:
            print("\n❌ PROBLEMAS CRÍTICOS:")
            for issue in issues:
                print(f"  {issue}")
        
        if warnings:
            print("\n⚠️  AVISOS:")
            for warning in warnings:
                print(f"  {warning}")
        
        # 6. AVALIAÇÃO FINAL
        print("\n" + "="*70)
        print("📊 AVALIAÇÃO DE PERFORMANCE REAL")
        print("="*70)
        
        # Calcula score REAL
        score = 100
        if mem.percent > 80: score -= 30
        if mem.percent > 70: score -= 15
        if swap.used > 0: score -= 25
        if cpu_count <= 2: score -= 15
        if response_times.get("file_open_large", 0) > 100: score -= 10
        if response_times.get("cpu_calculation", 0) > 50: score -= 10
        
        score = max(0, min(100, score))
        
        if score >= 80:
            grade = "🟢 BOM"
            detail = "Sistema OK para tarefas básicas"
        elif score >= 65:
            grade = "🟡 REGULAR"
            detail = "Pode ter lentidão com multitarefa"
        elif score >= 50:
            grade = "🟠 RUIM"
            detail = "Lentidão frequente, especialmente com várias apps"
        else:
            grade = "🔴 CRÍTICO"
            detail = "Sistema sobrecarregado, precisa de upgrade"
        
        print(f"\n  Nota: {score}/100")
        print(f"  Classificação: {grade}")
        print(f"  Status: {detail}")
        
        # 7. RECOMENDAÇÕES PRÁTICAS
        print("\n💡 O QUE FAZER AGORA:")
        print("="*70)
        
        recommendations = []
        
        if mem.percent > 75 or swap.used > 0:
            recommendations.append("1. 🆙 PRIORIDADE #1: AUMENTAR RAM para 16GB")
            recommendations.append("   → Isso vai acabar com os travamentos")
        
        if response_times.get("file_open_large", 0) > 100:
            recommendations.append("2. 🗑️  Libere espaço no SSD (menos de 80% de uso)")
            recommendations.append("   → SSD cheio fica muito mais lento")
        
        if cpu_count <= 2:
            recommendations.append("3. 📉 Evite multitarefa pesada")
            recommendations.append("   → Use apenas o essencial (VS Code OU Chrome, não ambos)")
        
        recommendations.append("4. 🚫 Feche aplicativos em segundo plano")
        recommendations.append("5. 🔄 Use versões leves:")
        recommendations.append("   → VS Codium em vez de VS Code")
        recommendations.append("   → Firefox em vez de Chrome")
        recommendations.append("   → SQLite em vez de MySQL (se possível)")
        
        for rec in recommendations:
            print(f"  {rec}")
        
        # Salva diagnóstico
        self.results["diagnosis"] = {
            "score": score,
            "grade": grade,
            "issues": issues,
            "warnings": warnings,
            "recommendations": recommendations
        }
        
        # APRESENTA RESUMO DO QUE VOCÊ SENTE
        print("\n" + "="*70)
        print("🎯 O QUE SIGNIFICA NA PRÁTICA:")
        print("="*70)
        
        if mem.percent > 75:
            print("\n  Com VS Code + Chrome + MySQL aberto:")
            print("  • ⏰ VS Code vai demorar para abrir arquivos")
            print("  • 🐌 Digitação vai ter atraso (lag)")
            print("  • 💀 O PC pode congelar ao salvar")
            print("  • 🔄 Alternar entre apps será lento")
        elif mem.percent > 65:
            print("\n  Com VS Code + Chrome + MySQL aberto:")
            print("  • ✅ Funciona, mas fique atento ao uso de memória")
            print("  • ⚠️  Evite abrir muitas abas no navegador")
            print("  • ⚠️  Feche apps não utilizados")
        
        # Sugere upgrade
        if score < 65:
            print("\n" + "="*70)
            print("🛠️ UPGRADE RECOMENDADO")
            print("="*70)
            print("\n  Investimento sugerido:")
            print("  • RAM: +8GB (R$ 150-250) → ELIMINA TRAVAMENTOS")
            print("  • Total: ~R$ 200 → PC fica como novo")
            print("\n  Ou ajuste seu uso:")
            print("  • Use apenas 1 app pesado por vez")
            print("  • Mantenha máximo 5 abas no navegador")

    def save_results(self):
        """Salva resultados"""
        filename = f"real_test_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Resultados salvos em: {filename}")

    def run(self):
        """Executa teste"""
        print("="*70)
        print("🚀 TESTE DE PERFORMANCE - USO REAL DE VERDADE")
        print("="*70)
        print("\n📌 Este teste SIMULA SEU USO REAL:")
        print("  • VS Code com projetos reais")
        print("  • Chrome com múltiplas abas")
        print("  • MySQL com consultas pesadas")
        print("  • Mede o que VOCÊ SENTE (tempo de resposta)")
        print(f"\n⏱️  Duração: ~{self.duration//60} minutos")
        print("⚠️  Não use o PC durante o teste para resultados precisos\n")
        
        input("Pressione ENTER para começar...")
        
        self.create_real_workload()
        self.save_results()
        
        print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test = RealWorldTestV2()
    test.run()