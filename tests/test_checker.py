"""
Testes do Validador
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from validator.checker import SystemChecker, CheckResult


class TestSystemChecker:
    """Testes do SystemChecker"""
    
    def setup_method(self):
        self.checker = SystemChecker()
    
    def test_check_ram_structure(self):
        """Verifica se check_ram retorna CheckResult válido"""
        result = self.checker.check_ram()
        
        assert isinstance(result, CheckResult)
        assert result.name == "RAM"
        assert isinstance(result.passed, bool)
        assert result.severity in ("error", "warning", "info")
        assert result.message
    
    def test_check_disk_structure(self):
        """Verifica se check_disk retorna CheckResult válido"""
        result = self.checker.check_disk()
        
        assert isinstance(result, CheckResult)
        assert result.name == "Disco"
        assert isinstance(result.passed, bool)
        assert result.severity == "error"
    
    def test_check_python_structure(self):
        """Verifica se check_python retorna CheckResult válido"""
        result = self.checker.check_python()
        
        assert isinstance(result, CheckResult)
        assert result.name == "Python"
        assert isinstance(result.passed, bool)
        assert result.severity == "error"
    
    def test_check_cpu_structure(self):
        """Verifica se check_cpu retorna CheckResult válido"""
        result = self.checker.check_cpu()
        
        assert isinstance(result, CheckResult)
        assert result.name == "CPU"
        assert isinstance(result.passed, bool)
        assert result.severity == "warning"
    
    def test_check_architecture_structure(self):
        """Verifica se check_architecture retorna CheckResult válido"""
        result = self.checker.check_architecture()
        
        assert isinstance(result, CheckResult)
        assert result.name == "Arquitetura"
        assert isinstance(result.passed, bool)
        assert result.severity == "warning"
    
    def test_check_mysql_structure(self):
        """Verifica se check_mysql retorna CheckResult válido"""
        result = self.checker.check_mysql()
        
        assert isinstance(result, CheckResult)
        assert result.name == "MySQL"
        assert isinstance(result.passed, bool)
        assert result.severity == "info"
    
    def test_check_all_returns_report(self):
        """Verifica se check_all retorna SystemReport completo"""
        report = self.checker.check_all()
        
        from validator.checker import SystemReport
        assert isinstance(report, SystemReport)
        assert report.status in ("success", "warning", "error")
        assert 0 <= report.score <= 100
        assert report.timestamp
        assert isinstance(report.checks, dict)
        assert len(report.checks) >= 7  # RAM, Disco, SO, Python, CPU, Arquitetura, MySQL
    
    def test_report_contains_required_checks(self):
        """Verifica se relatório contém todas verificações obrigatórias"""
        report = self.checker.check_all()
        
        required_checks = ["ram", "disk", "os", "python", "cpu", "architecture"]
        for check in required_checks:
            assert check in report.checks, f"Verificação {check} não encontrada"
    
    def test_score_calculation(self):
        """Verifica cálculo de score"""
        # Força um erro
        self.checker.MIN_RAM_GB = 999
        report = self.checker.check_all()
        assert report.score < 100
        
        # Reset
        self.checker.MIN_RAM_GB = 8


class TestCheckResult:
    """Testes do CheckResult dataclass"""
    
    def test_check_result_creation(self):
        """Verifica criação de CheckResult"""
        result = CheckResult(
            name="Teste",
            passed=True,
            value="10",
            required=">= 8",
            message="[OK] Teste",
            severity="error"
        )
        
        assert result.name == "Teste"
        assert result.passed is True
        assert result.value == "10"
        assert result.required == ">= 8"
        assert result.message == "[OK] Teste"
        assert result.severity == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])