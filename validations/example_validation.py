"""
Exemplo de arquivo de validação para o Data-Runner

Este arquivo demonstra como criar validações personalizadas que serão
executadas pelo motor de validação do Data-Runner.

Para usar este arquivo:
1. Copie para validations/nome_da_validacao.py
2. Modifique a função validate conforme sua necessidade
3. Configure um job do tipo 'validation' no jobs.json
"""

import pandas as pd
from typing import Dict, Any
from app.validation_engine import ValidationResult

# Metadados da validação (opcional)
description = "Validação de exemplo que verifica dados básicos"
requirements = [
    "Coluna 'id' deve existir",
    "Coluna 'name' deve existir e não ser nula",
    "Pelo menos 1 linha deve existir"
]
examples = [
    "Verifica se dados de usuários estão corretos",
    "Valida integridade de dados de produtos"
]


def validate(data: pd.DataFrame, context: Dict[str, Any] = None) -> ValidationResult:
    """
    Função principal de validação
    
    Args:
        data: DataFrame com os dados a serem validados
        context: Contexto adicional (main_query_id, validation_query_id, etc.)
        
    Returns:
        ValidationResult com o resultado da validação
    """
    
    # Verificar se há dados
    if data.empty:
        return ValidationResult(
            success=False,
            message="Nenhum dado encontrado para validação",
            details={"row_count": 0}
        )
    
    # Lista de verificações
    checks = []
    
    # Verificação 1: Existência de colunas obrigatórias
    required_columns = ['id', 'name']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        checks.append({
            "check": "colunas_obrigatorias",
            "status": "FAILED",
            "message": f"Colunas obrigatórias ausentes: {missing_columns}",
            "details": {"missing_columns": missing_columns}
        })
    else:
        checks.append({
            "check": "colunas_obrigatorias",
            "status": "PASSED",
            "message": "Todas as colunas obrigatórias estão presentes",
            "details": {"required_columns": required_columns}
        })
    
    # Verificação 2: Valores nulos em colunas críticas
    if 'name' in data.columns:
        null_names = data['name'].isnull().sum()
        if null_names > 0:
            checks.append({
                "check": "valores_nulos_name",
                "status": "FAILED",
                "message": f"Encontrados {null_names} valores nulos na coluna 'name'",
                "details": {"null_count": int(null_names)}
            })
        else:
            checks.append({
                "check": "valores_nulos_name",
                "status": "PASSED",
                "message": "Nenhum valor nulo encontrado na coluna 'name'",
                "details": {"null_count": 0}
            })
    
    # Verificação 3: Duplicatas na coluna ID
    if 'id' in data.columns:
        duplicate_ids = data['id'].duplicated().sum()
        if duplicate_ids > 0:
            checks.append({
                "check": "ids_duplicados",
                "status": "FAILED",
                "message": f"Encontrados {duplicate_ids} IDs duplicados",
                "details": {"duplicate_count": int(duplicate_ids)}
            })
        else:
            checks.append({
                "check": "ids_duplicados",
                "status": "PASSED",
                "message": "Nenhum ID duplicado encontrado",
                "details": {"duplicate_count": 0}
            })
    
    # Verificação 4: Formato de dados
    if 'id' in data.columns:
        # Verificar se IDs são numéricos
        try:
            numeric_ids = pd.to_numeric(data['id'], errors='coerce')
            invalid_ids = numeric_ids.isnull().sum()
            if invalid_ids > 0:
                checks.append({
                    "check": "formato_id",
                    "status": "FAILED",
                    "message": f"Encontrados {invalid_ids} IDs com formato inválido",
                    "details": {"invalid_count": int(invalid_ids)}
                })
            else:
                checks.append({
                    "check": "formato_id",
                    "status": "PASSED",
                    "message": "Todos os IDs têm formato válido",
                    "details": {"invalid_count": 0}
                })
        except Exception as e:
            checks.append({
                "check": "formato_id",
                "status": "ERROR",
                "message": f"Erro ao verificar formato de IDs: {str(e)}",
                "details": {"error": str(e)}
            })
    
    # Determinar resultado geral
    failed_checks = [check for check in checks if check["status"] == "FAILED"]
    error_checks = [check for check in checks if check["status"] == "ERROR"]
    
    if error_checks:
        overall_success = False
        overall_message = f"Erro na validação: {error_checks[0]['message']}"
    elif failed_checks:
        overall_success = False
        overall_message = f"Validação falhou: {len(failed_checks)} verificação(ões) falharam"
    else:
        overall_success = True
        overall_message = f"Validação passou: {len(checks)} verificação(ões) executadas com sucesso"
    
    # Detalhes da validação
    details = {
        "total_checks": len(checks),
        "passed_checks": len([c for c in checks if c["status"] == "PASSED"]),
        "failed_checks": len(failed_checks),
        "error_checks": len(error_checks),
        "row_count": len(data),
        "column_count": len(data.columns),
        "checks": checks,
        "context": context or {}
    }
    
    return ValidationResult(
        success=overall_success,
        message=overall_message,
        details=details
    )


# Função auxiliar para validações simples (opcional)
def validate_not_empty(data: pd.DataFrame) -> bool:
    """
    Validação simples: verifica se o DataFrame não está vazio
    
    Args:
        data: DataFrame a ser validado
        
    Returns:
        True se não estiver vazio, False caso contrário
    """
    return not data.empty


def validate_has_columns(data: pd.DataFrame, required_columns: list) -> bool:
    """
    Validação simples: verifica se o DataFrame tem as colunas necessárias
    
    Args:
        data: DataFrame a ser validado
        required_columns: Lista de colunas obrigatórias
        
    Returns:
        True se tem todas as colunas, False caso contrário
    """
    return all(col in data.columns for col in required_columns)
