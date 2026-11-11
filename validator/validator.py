"""
CLI Principal do Validador
Interface de linha de comando e saída formatada
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from .checker import SystemChecker, SystemReport, CheckResult


class SystemValidator:
    """Validador principal com CLI"""
    
    def __init__(self, verbose: bool = False, json_output: bool = False):
        self.verbose = verbose
        self.json_output = json_output
        self.checker = SystemChecker()
    
    def validate(self) -> SystemReport:
        """Executa validação completa"""
        if not self.json_output:
            print("🔍 VALIDANDO CONFIGURAÇÃO MÍNIMA DO SISTEMA")
            print("=" * 50)
        
        report = self.checker.check_all()
        
        if self.json_output:
            self._output_json(report)
        else:
            self._output_human(report)
        
        return report
    
    def _output_human(self, report: SystemReport):
        """Saída legível para humanos"""
        print()
        
        # Mostra cada verificação
        for check in report.checks.values():
            print(check.message)
            if self.verbose:
                print(f"   → Valor: {check.value}")
                print(f"   → Requisito: {check.required}")
                print()
        
        print()
        print("=" * 50)
        
        # Status final
        if report.status == "success":
            print(f"✅ SUCESSO - Score: {report.score}/100")
            print("   Sistema compatível para desenvolvimento!")
        elif report.status == "warning":
            print(f"⚠️  ATENÇÃO - Score: {report.score}/100")
            print("   Sistema funcional mas com limitações")
        else:
            print(f"🔴 ERRO - Score: {report.score}/100")
            print("   Sistema NÃO atende requisitos mínimos")
        
        # Recomendações
        if report.recommendations:
            print()
            print("💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print()
    
    def _output_json(self, report: SystemReport):
        """Saída JSON para CI/CD"""
        output = {
            "status": report.status,
            "score": report.score,
            "timestamp": report.timestamp,
            "checks": {},
            "recommendations": report.recommendations,
            "metadata": report.metadata
        }
        
        for name, check in report.checks.items():
            output["checks"][name] = {
                "passed": check.passed,
                "value": str(check.value),
                "required": str(check.required),
                "message": check.message,
                "severity": check.severity
            }
        
        print(json.dumps(output, indent=2, ensure_ascii=False))
    
    def get_exit_code(self, report: SystemReport) -> int:
        """Retorna código de saída para scripts"""
        if report.status == "success":
            return 0
        elif report.status == "warning":
            return 2
        else:
            return 1


def create_parser() -> argparse.ArgumentParser:
    """Cria parser de argumentos"""
    parser = argparse.ArgumentParser(
        description="Validador de Configuração Mínima do Sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python -m validator              # Verificação padrão
  python -m validator -v           # Modo verboso
  python -m validator --json       # Saída JSON para CI/CD
  python -m validator --save       # Salva resultado em arquivo
  
Códigos de saída:
  0 = Sucesso (todos requisitos atendidos)
  1 = Erro (requisitos críticos não atendidos)
  2 = Aviso (requisitos opcionais não atendidos)
        """
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Mostra detalhes de cada verificação"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída em formato JSON"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Salva resultado em validator_output.json"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Arquivo de saída personalizado"
    )
    
    parser.add_argument(
        "--min-ram",
        type=int,
        default=8,
        help="RAM mínima em GB (padrão: 8)"
    )
    
    parser.add_argument(
        "--min-disk",
        type=int,
        default=10,
        help="Disco livre mínimo em GB (padrão: 10)"
    )
    
    parser.add_argument(
        "--skip-optional",
        action="store_true",
        help="Pula verificações opcionais (MySQL, VS Code, Navegador)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def main():
    """Ponto de entrada principal"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Aplica configurações personalizadas
    checker = SystemChecker()
    
    if args.min_ram:
        checker.MIN_RAM_GB = args.min_ram
    if args.min_disk:
        checker.MIN_DISK_GB = args.min_disk
    
    validator = SystemValidator(verbose=args.verbose, json_output=args.json)
    validator.checker = checker
    
    try:
        report = validator.validate()
        
        # Salva arquivo se solicitado
        if args.save or args.output:
            output_file = args.output or "validator_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "status": report.status,
                    "score": report.score,
                    "timestamp": report.timestamp,
                    "checks": {k: {
                        "passed": v.passed,
                        "value": str(v.value),
                        "required": str(v.required),
                        "message": v.message,
                        "severity": v.severity
                    } for k, v in report.checks.items()},
                    "recommendations": report.recommendations,
                    "metadata": report.metadata
                }, f, indent=2, ensure_ascii=False)
            if not args.json:
                print(f"📄 Resultado salvo em: {output_file}")
        
        # Retorna código de saída
        sys.exit(validator.get_exit_code(report))
        
    except KeyboardInterrupt:
        print("\n⚠️  Validação interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}))
        else:
            print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()