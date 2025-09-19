"""
Motor de validação de dados para o Data-Runner
"""

import importlib.util
import sys
import os
import json
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime
from .progress_bar import create_validation_progress_bar

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
    
    def execute_validation_per_record(self, validation_file: str, data: pd.DataFrame, 
                                     context: Dict[str, Any] = None) -> ValidationResult:
        """
        Executa uma validação por registro (uma vez para cada linha)
        
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
            if not hasattr(module, 'validate_record'):
                # Se não tem validate_record, usar validate (validação tradicional)
                return self.execute_validation(validation_file, data, context)
            
            validate_record_func = getattr(module, 'validate_record')
            if not callable(validate_record_func):
                raise ValueError("'validate_record' deve ser uma função")
            
            # Executar validação para cada registro
            logger.info(f"Executando validação por registro: {validation_file}")
            results = []
            failed_records = []
            error_records = []
            
            # Criar e iniciar barra de progresso
            progress_bar = create_validation_progress_bar(
                total=len(data),
                validation_file=validation_file,
                output_table=None
            )
            progress_bar.start()
            
            for index, record in data.iterrows():
                try:
                    # Converter Series para dict e adicionar índice
                    record_dict = record.to_dict()
                    record_dict['_record_index'] = index
                    
                    # Executar validação para este registro
                    result = validate_record_func(record_dict, context or {})
                    
                    # Converter resultado para ValidationResult se necessário
                    if isinstance(result, ValidationResult):
                        validation_result = result
                    elif isinstance(result, dict):
                        validation_result = ValidationResult(
                            success=result.get('success', False),
                            message=result.get('message', ''),
                            details=result.get('details', {})
                        )
                    elif isinstance(result, bool):
                        validation_result = ValidationResult(
                            success=result,
                            message="Validação executada com sucesso" if result else "Validação falhou"
                        )
                    else:
                        validation_result = ValidationResult(
                            success=True,
                            message=str(result)
                        )
                    
                    results.append({
                        'record_index': index,
                        'record_data': record_dict,
                        'validation_result': validation_result
                    })
                    
                    if not validation_result.success:
                        failed_records.append({
                            'index': index,
                            'record': record_dict,
                            'message': validation_result.message,
                            'details': validation_result.details
                        })
                    
                    # Atualizar barra de progresso com resultado
                    progress_bar.update_with_result(validation_result.success)
                
                except Exception as e:
                    error_records.append({
                        'index': index,
                        'record': record_dict if 'record_dict' in locals() else record.to_dict(),
                        'error': str(e)
                    })
                    logger.error(f"Erro na validação do registro {index}: {e}")
                    
                    # Atualizar barra de progresso (erro = falha)
                    progress_bar.update_with_result(False)
            
            # Finalizar barra de progresso
            progress_bar.finish()
            
            # Determinar resultado geral
            total_records = len(data)
            successful_records = total_records - len(failed_records) - len(error_records)
            
            if error_records:
                overall_success = False
                overall_message = f"Erro na validação: {len(error_records)} registro(s) com erro"
            elif failed_records:
                overall_success = False
                overall_message = f"Validação falhou: {len(failed_records)} de {total_records} registro(s) falharam"
            else:
                overall_success = True
                overall_message = f"Validação passou: {successful_records} registro(s) validados com sucesso"
            
            # Detalhes da validação
            details = {
                "validation_type": "per_record",
                "total_records": total_records,
                "successful_records": successful_records,
                "failed_records": len(failed_records),
                "error_records": len(error_records),
                "success_rate": round(successful_records / total_records * 100, 2) if total_records > 0 else 0,
                "failed_records_details": failed_records[:10],  # Limitar a 10 para não sobrecarregar
                "error_records_details": error_records[:10],   # Limitar a 10 para não sobrecarregar
                "context": context or {}
            }
            
            return ValidationResult(
                success=overall_success,
                message=overall_message,
                details=details
            )
                
        except Exception as e:
            logger.error(f"Erro ao executar validação por registro {validation_file}: {e}")
            return ValidationResult(
                success=False,
                message=f"Erro na validação por registro: {str(e)}",
                details={"error_type": type(e).__name__, "validation_type": "per_record"}
            )
    
    def execute_validation_per_record_with_output(self, validation_file: str, data: pd.DataFrame, 
                                                 context: Dict[str, Any] = None, 
                                                 repository=None, output_table: str = None,
                                                 pkey_field: str = None) -> ValidationResult:
        """
        Executa validação por registro e salva resultados na tabela de output
        
        Args:
            validation_file: Caminho do arquivo Python de validação
            data: DataFrame com os dados a serem validados
            context: Contexto adicional para a validação
            repository: Instância do DuckDBRepository
            output_table: Nome da tabela de output
            pkey_field: Campo chave primária
            
        Returns:
            ValidationResult com o resultado da validação
        """
        try:
            # Carregar módulo de validação
            module = self.load_validation_module(validation_file)
            
            # Verificar se tem função de validação
            if not hasattr(module, 'validate_record'):
                # Se não tem validate_record, usar validação tradicional
                return self.execute_validation(validation_file, data, context)
            
            validate_record_func = getattr(module, 'validate_record')
            if not callable(validate_record_func):
                raise ValueError("'validate_record' deve ser uma função")
            
            # Obter próximo número de execução
            execution_count = repository.get_next_execution_count(output_table) if repository and output_table else 1
            
            # Executar validação para cada registro
            logger.info(f"Executando validação por registro com output: {validation_file}")
            validation_records = []
            failed_records = []
            error_records = []
            executed_at = datetime.now().isoformat()
            
            # Criar e iniciar barra de progresso
            progress_bar = create_validation_progress_bar(
                total=len(data),
                validation_file=validation_file,
                output_table=output_table
            )
            progress_bar.start()
            
            for index, record in data.iterrows():
                try:
                    # Converter Series para dict e adicionar índice
                    record_dict = record.to_dict()
                    record_dict['_record_index'] = index
                    
                    # Obter chave primária
                    if pkey_field and pkey_field in record_dict:
                        pkey_value = str(record_dict[pkey_field])
                    else:
                        # Usar índice como chave se não especificado
                        pkey_value = str(index)
                    
                    # Executar validação para este registro
                    result = validate_record_func(record_dict, context or {})
                    
                    # Converter resultado para ValidationResult se necessário
                    if isinstance(result, ValidationResult):
                        validation_result = result
                    elif isinstance(result, dict):
                        validation_result = ValidationResult(
                            success=result.get('success', False),
                            message=result.get('message', ''),
                            details=result.get('details', {})
                        )
                    elif isinstance(result, bool):
                        validation_result = ValidationResult(
                            success=result,
                            message="Validação executada com sucesso" if result else "Validação falhou"
                        )
                    else:
                        validation_result = ValidationResult(
                            success=True,
                            message=str(result)
                        )
                    
                    # Criar ValidationRecord para salvar
                    validation_record = {
                        'execution_count': execution_count,
                        'pkey': pkey_value,
                        'result': 'success' if validation_result.success else 'error',
                        'message': validation_result.message,
                        'details': json.dumps(validation_result.details, ensure_ascii=False),
                        'input_data': json.dumps(record_dict, ensure_ascii=False),
                        'executed_at': executed_at
                    }
                    
                    validation_records.append(validation_record)
                    
                    if not validation_result.success:
                        failed_records.append({
                            'index': index,
                            'record': record_dict,
                            'message': validation_result.message,
                            'details': validation_result.details
                        })
                    
                    # Atualizar barra de progresso com resultado
                    progress_bar.update_with_result(validation_result.success)
                
                except Exception as e:
                    error_records.append({
                        'index': index,
                        'record': record_dict if 'record_dict' in locals() else record.to_dict(),
                        'error': str(e)
                    })
                    logger.error(f"Erro na validação do registro {index}: {e}")
                    
                    # Atualizar barra de progresso (erro = falha)
                    progress_bar.update_with_result(False)
            
            # Salvar resultados na tabela de output se configurado
            if repository and output_table and validation_records:
                from .types import ValidationRecord
                validation_objects = []
                for record in validation_records:
                    validation_objects.append(ValidationRecord(**record))
                
                repository.save_validation_records_batch(output_table, validation_objects)
                logger.info(f"Salvos {len(validation_records)} registros de validação na tabela {output_table}")
            
            # Finalizar barra de progresso
            progress_bar.finish()
            
            # Determinar resultado geral
            total_records = len(data)
            successful_records = total_records - len(failed_records) - len(error_records)
            
            if error_records:
                overall_success = False
                overall_message = f"Erro na validação: {len(error_records)} registro(s) com erro"
            elif failed_records:
                overall_success = False
                overall_message = f"Validação falhou: {len(failed_records)} de {total_records} registro(s) falharam"
            else:
                overall_success = True
                overall_message = f"Validação passou: {successful_records} registro(s) validados com sucesso"
            
            # Detalhes da validação
            details = {
                "validation_type": "per_record_with_output",
                "execution_count": execution_count,
                "output_table": output_table,
                "pkey_field": pkey_field,
                "total_records": total_records,
                "successful_records": successful_records,
                "failed_records": len(failed_records),
                "error_records": len(error_records),
                "success_rate": round(successful_records / total_records * 100, 2) if total_records > 0 else 0,
                "failed_records_details": failed_records[:10],  # Limitar a 10 para não sobrecarregar
                "error_records_details": error_records[:10],   # Limitar a 10 para não sobrecarregar
                "context": context or {}
            }
            
            return ValidationResult(
                success=overall_success,
                message=overall_message,
                details=details
            )
                
        except Exception as e:
            logger.error(f"Erro ao executar validação por registro com output {validation_file}: {e}")
            return ValidationResult(
                success=False,
                message=f"Erro na validação por registro com output: {str(e)}",
                details={"error_type": type(e).__name__, "validation_type": "per_record_with_output"}
            )
    
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
