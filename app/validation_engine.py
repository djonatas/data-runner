"""
Motor de validação de dados para o Data-Runner
"""

import importlib.util
import sys
import os
import json
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class ValidationResult:
    """Resultado de uma validação"""
    
    def __init__(self, success: bool, message: str = "", details: Dict[str, Any] = None):
        self.success = success
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário"""
        return {
            "success": self.success,
            "message": self.message,
            "details": self.details
        }
    
    def to_json(self) -> str:
        """Converte resultado para JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class ValidationEngine:
    """Motor para execução de validações personalizadas"""
    
    def __init__(self, base_path: str = "validations"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self._loaded_modules: Dict[str, Any] = {}
    
    def load_validation_module(self, validation_file: str) -> Any:
        """
        Carrega um módulo de validação dinamicamente
        
        Args:
            validation_file: Caminho do arquivo Python de validação
            
        Returns:
            Módulo carregado
            
        Raises:
            ImportError: Se não conseguir carregar o módulo
            FileNotFoundError: Se o arquivo não existir
        """
        # Caminho completo do arquivo
        if not validation_file.endswith('.py'):
            validation_file += '.py'
        
        # Tentar caminho relativo primeiro
        validation_path = self.base_path / validation_file
        if not validation_path.exists():
            # Tentar caminho absoluto
            validation_path = Path(validation_file)
            if not validation_path.exists():
                raise FileNotFoundError(f"Arquivo de validação não encontrado: {validation_file}")
        
        # Verificar se já foi carregado
        cache_key = str(validation_path.absolute())
        if cache_key in self._loaded_modules:
            return self._loaded_modules[cache_key]
        
        try:
            # Carregar módulo dinamicamente
            spec = importlib.util.spec_from_file_location("validation_module", validation_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Não foi possível criar spec para {validation_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["validation_module"] = module
            spec.loader.exec_module(module)
            
            # Cache do módulo
            self._loaded_modules[cache_key] = module
            
            logger.info(f"Módulo de validação carregado: {validation_path}")
            return module
            
        except Exception as e:
            logger.error(f"Erro ao carregar módulo de validação {validation_path}: {e}")
            raise ImportError(f"Erro ao carregar módulo de validação: {e}")
    
    def execute_validation(self, validation_file: str, data: pd.DataFrame, 
                          context: Dict[str, Any] = None) -> ValidationResult:
        """
        Executa uma validação
        
        Args:
            validation_file: Caminho do arquivo Python de validação
            data: DataFrame com os dados a serem validados
            context: Contexto adicional para a validação
            
        Returns:
            ValidationResult com o resultado da validação
        """
        try:
            # Carregar módulo de validação
            module = self.load_validation_module(validation_file)
            
            # Verificar se tem função de validação
            if not hasattr(module, 'validate'):
                raise ValueError("Módulo de validação deve ter uma função 'validate'")
            
            validate_func = getattr(module, 'validate')
            if not callable(validate_func):
                raise ValueError("'validate' deve ser uma função")
            
            # Executar validação
            logger.info(f"Executando validação: {validation_file}")
            result = validate_func(data, context or {})
            
            # Converter resultado para ValidationResult se necessário
            if isinstance(result, ValidationResult):
                return result
            elif isinstance(result, dict):
                return ValidationResult(
                    success=result.get('success', False),
                    message=result.get('message', ''),
                    details=result.get('details', {})
                )
            elif isinstance(result, bool):
                return ValidationResult(
                    success=result,
                    message="Validação executada com sucesso" if result else "Validação falhou"
                )
            else:
                # Tentar converter para string
                return ValidationResult(
                    success=True,
                    message=str(result)
                )
                
        except Exception as e:
            logger.error(f"Erro ao executar validação {validation_file}: {e}")
            return ValidationResult(
                success=False,
                message=f"Erro na validação: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    def get_validation_info(self, validation_file: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um módulo de validação
        
        Args:
            validation_file: Caminho do arquivo Python de validação
            
        Returns:
            Dicionário com informações do módulo
        """
        try:
            module = self.load_validation_module(validation_file)
            
            info = {
                "file": validation_file,
                "has_validate": hasattr(module, 'validate'),
                "has_description": hasattr(module, 'description'),
                "has_requirements": hasattr(module, 'requirements'),
                "has_examples": hasattr(module, 'examples')
            }
            
            if hasattr(module, 'description'):
                info['description'] = module.description
            
            if hasattr(module, 'requirements'):
                info['requirements'] = module.requirements
            
            if hasattr(module, 'examples'):
                info['examples'] = module.examples
            
            return info
            
        except Exception as e:
            return {
                "file": validation_file,
                "error": str(e),
                "has_validate": False
            }
    
    def list_validation_files(self) -> list:
        """
        Lista todos os arquivos de validação disponíveis
        
        Returns:
            Lista de arquivos .py no diretório de validações
        """
        if not self.base_path.exists():
            return []
        
        return [
            f.name for f in self.base_path.iterdir()
            if f.is_file() and f.suffix == '.py'
        ]


# Função utilitária para criar validações simples
def create_simple_validation(validation_func: Callable[[pd.DataFrame], bool], 
                           description: str = "") -> ValidationResult:
    """
    Cria um resultado de validação simples
    
    Args:
        validation_func: Função que recebe DataFrame e retorna bool
        description: Descrição da validação
        
    Returns:
        ValidationResult
    """
    try:
        # Esta função seria usada em módulos de validação
        pass
    except Exception as e:
        return ValidationResult(
            success=False,
            message=f"Erro na validação: {str(e)}"
        )
