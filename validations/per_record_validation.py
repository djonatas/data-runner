"""
Validação por registro - Exemplo para o Data-Runner

Este arquivo demonstra como criar validações que são executadas
uma vez para cada registro/linha dos dados.

Para usar este arquivo:
1. Copie para validations/nome_da_validacao.py
2. Modifique a função validate_record conforme sua necessidade
3. Configure um job do tipo 'validation' no jobs.json
"""

import pandas as pd
from typing import Dict, Any
from app.validation_engine import ValidationResult

# Metadados da validação (opcional)
description = "Validação por registro que verifica cada linha individualmente"
requirements = [
    "Coluna 'id' deve existir e ser numérica",
    "Coluna 'name' deve existir e não ser nula",
    "Coluna 'email' deve ter formato válido (se presente)",
    "Cada registro deve passar nas validações individuais"
]
examples = [
    "Validação individual de usuários",
    "Verificação de integridade por registro",
    "Validação de dados críticos linha por linha"
]


def validate_record(record: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
    """
    Função de validação executada uma vez para cada registro
    
    Args:
        record: Dicionário com os dados do registro (inclui _record_index)
        context: Contexto adicional (main_query_id, validation_query_id, etc.)
        
    Returns:
        ValidationResult com o resultado da validação para este registro
    """
    
    record_index = record.get('_record_index', 'N/A')
    checks = []
    
    # Verificação 1: ID deve existir e ser numérico
    if 'id' not in record:
        return ValidationResult(
            success=False,
            message=f"Registro {record_index}: Campo 'id' não encontrado",
            details={"record_index": record_index, "missing_field": "id"}
        )
    
    try:
        id_value = int(record['id'])
        if id_value <= 0:
            return ValidationResult(
                success=False,
                message=f"Registro {record_index}: ID deve ser maior que zero (valor: {id_value})",
                details={"record_index": record_index, "invalid_id": id_value}
            )
    except (ValueError, TypeError):
        return ValidationResult(
            success=False,
            message=f"Registro {record_index}: ID deve ser numérico (valor: {record['id']})",
            details={"record_index": record_index, "invalid_id": record['id']}
        )
    
    # Verificação 2: Nome deve existir e não ser nulo
    if 'name' not in record or pd.isna(record['name']) or not record['name']:
        return ValidationResult(
            success=False,
            message=f"Registro {record_index}: Campo 'name' é obrigatório",
            details={"record_index": record_index, "missing_field": "name"}
        )
    
    name = str(record['name']).strip()
    if len(name) < 2:
        return ValidationResult(
            success=False,
            message=f"Registro {record_index}: Nome deve ter pelo menos 2 caracteres (valor: '{name}')",
            details={"record_index": record_index, "invalid_name": name}
        )
    
    # Verificação 3: Email deve ter formato válido (se presente)
    if 'email' in record and not pd.isna(record['email']) and record['email']:
        email = str(record['email']).strip()
        if '@' not in email or '.' not in email:
            return ValidationResult(
                success=False,
                message=f"Registro {record_index}: Email inválido (valor: '{email}')",
                details={"record_index": record_index, "invalid_email": email}
            )
    
    # Verificação 4: Status deve ser válido (se presente)
    if 'status' in record and not pd.isna(record['status']) and record['status']:
        valid_statuses = ['active', 'inactive', 'pending', 'blocked']
        status = str(record['status']).lower().strip()
        if status not in valid_statuses:
            return ValidationResult(
                success=False,
                message=f"Registro {record_index}: Status inválido '{status}' (valores válidos: {valid_statuses})",
                details={
                    "record_index": record_index, 
                    "invalid_status": status,
                    "valid_statuses": valid_statuses
                }
            )
    
    # Verificação 5: Valores numéricos devem ser positivos (se presentes)
    numeric_fields = ['age', 'score', 'amount', 'quantity']
    for field in numeric_fields:
        if field in record and not pd.isna(record[field]) and record[field] is not None:
            try:
                value = float(record[field])
                if value < 0:
                    return ValidationResult(
                        success=False,
                        message=f"Registro {record_index}: Campo '{field}' deve ser positivo (valor: {value})",
                        details={"record_index": record_index, "invalid_field": field, "value": value}
                    )
            except (ValueError, TypeError):
                return ValidationResult(
                    success=False,
                    message=f"Registro {record_index}: Campo '{field}' deve ser numérico (valor: {record[field]})",
                    details={"record_index": record_index, "invalid_field": field, "value": record[field]}
                )
    
    # Se chegou até aqui, o registro é válido
    return ValidationResult(
        success=True,
        message=f"Registro {record_index} válido",
        details={
            "record_index": record_index,
            "validated_fields": list(record.keys()),
            "id": id_value,
            "name": name
        }
    )


# Função de validação tradicional (para compatibilidade)
def validate(data: pd.DataFrame, context: Dict[str, Any] = None) -> ValidationResult:
    """
    Função de validação tradicional (executada uma vez para todo o dataset)
    Esta função é mantida para compatibilidade com validações antigas.
    """
    
    if data.empty:
        return ValidationResult(
            success=False,
            message="Nenhum dado encontrado para validação",
            details={"row_count": 0}
        )
    
    # Verificar se tem as colunas obrigatórias
    required_columns = ['id', 'name']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        return ValidationResult(
            success=False,
            message=f"Colunas obrigatórias ausentes: {missing_columns}",
            details={"missing_columns": missing_columns}
        )
    
    # Contar registros com problemas básicos
    total_records = len(data)
    null_ids = data['id'].isnull().sum()
    null_names = data['name'].isnull().sum()
    
    if null_ids > 0 or null_names > 0:
        return ValidationResult(
            success=False,
            message=f"Encontrados {null_ids} IDs nulos e {null_names} nomes nulos",
            details={
                "total_records": total_records,
                "null_ids": int(null_ids),
                "null_names": int(null_names)
            }
        )
    
    return ValidationResult(
        success=True,
        message=f"Validação básica passou: {total_records} registros com campos obrigatórios",
        details={"total_records": total_records}
    )


# Funções utilitárias para validações comuns
def validate_email_format(email: str) -> bool:
    """Valida formato básico de email"""
    if pd.isna(email) or not isinstance(email, str):
        return False
    return '@' in email and '.' in email


def validate_numeric_positive(value: Any) -> bool:
    """Valida se um valor é numérico e positivo"""
    try:
        num_value = float(value)
        return num_value >= 0
    except (ValueError, TypeError):
        return False


def validate_string_not_empty(value: Any, min_length: int = 1) -> bool:
    """Valida se uma string não está vazia e tem tamanho mínimo"""
    if pd.isna(value) or value is None:
        return False
    return len(str(value).strip()) >= min_length
