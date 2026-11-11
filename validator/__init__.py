"""
Validador de Configuração Mínima do Sistema
Verifica pré-requisitos antes da instalação de software
"""

from .checker import SystemChecker
from .validator import SystemValidator

__version__ = "1.0.0"
__all__ = ["SystemChecker", "SystemValidator"]