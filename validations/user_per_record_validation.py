"""
Validação de usuários por registro - Exemplo específico

Este arquivo demonstra validação por registro para dados de usuários,
executando validações específicas para cada linha dos dados.
"""

import pandas as pd
import re
from typing import Dict, Any
from app.validation_engine import ValidationResult

description = "Validação de usuários por registro com verificações de email, telefone e CPF"
requirements = [
    "Cada registro de usuário deve ter email válido",
    "Cada registro deve ter telefone válido (se presente)",
    "Cada registro deve ter CPF válido (se presente)",
    "Cada registro deve ter nome não nulo"
]


def validate_email(email: str) -> bool:
    """Valida formato de email"""
    if pd.isna(email) or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Valida formato de telefone brasileiro"""
    if pd.isna(phone) or not isinstance(phone, str):
        return False
    phone_clean = re.sub(r'[^\d]', '', phone)
    return len(phone_clean) in [10, 11]


def validate_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro"""
    if pd.isna(cpf) or not isinstance(cpf, str):
        return False
    
    cpf_clean = re.sub(r'[^\d]', '', cpf)
    
    if len(cpf_clean) != 11:
        return False
    
    if cpf_clean == cpf_clean[0] * 11:
        return False
    
    def calculate_digit(cpf_digits: str, multiplier: int) -> int:
        total = sum(int(digit) * (multiplier - i) for i, digit in enumerate(cpf_digits))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    first_digit = calculate_digit(cpf_clean[:9], 10)
    if int(cpf_clean[9]) != first_digit:
        return False
    
    second_digit = calculate_digit(cpf_clean[:10], 11)
    if int(cpf_clean[10]) != second_digit:
        return False
    
    return True


def validate_record(record: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
    """
    Valida um registro individual de usuário
    
    Args:
        record: Dados do registro (inclui _record_index)
        context: Contexto adicional
        
    Returns:
        ValidationResult para este registro específico
    """
    
    record_index = record.get('_record_index', 'N/A')
    errors = []
    warnings = []
    
    # Verificação 1: Nome obrigatório
    if 'name' not in record or pd.isna(record['name']) or not str(record['name']).strip():
        errors.append("Nome é obrigatório")
    else:
        name = str(record['name']).strip()
        if len(name) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")
        elif len(name) > 100:
            warnings.append("Nome muito longo (mais de 100 caracteres)")
    
    # Verificação 2: Email obrigatório e válido
    if 'email' not in record or pd.isna(record['email']) or not str(record['email']).strip():
        errors.append("Email é obrigatório")
    else:
        email = str(record['email']).strip()
        if not validate_email(email):
            errors.append("Email deve ter formato válido")
        elif len(email) > 255:
            warnings.append("Email muito longo (mais de 255 caracteres)")
    
    # Verificação 3: Telefone (se presente)
    if 'phone' in record and not pd.isna(record['phone']) and str(record['phone']).strip():
        phone = str(record['phone']).strip()
        if not validate_phone(phone):
            errors.append("Telefone deve ter formato válido (10 ou 11 dígitos)")
    
    # Verificação 4: CPF (se presente)
    if 'cpf' in record and not pd.isna(record['cpf']) and str(record['cpf']).strip():
        cpf = str(record['cpf']).strip()
        if not validate_cpf(cpf):
            errors.append("CPF deve ter formato válido")
    
    # Verificação 5: Idade (se presente)
    if 'age' in record and not pd.isna(record['age']) and record['age'] is not None:
        try:
            age = int(record['age'])
            if age < 0:
                errors.append("Idade deve ser positiva")
            elif age > 150:
                warnings.append("Idade muito alta (mais de 150 anos)")
        except (ValueError, TypeError):
            errors.append("Idade deve ser numérica")
    
    # Verificação 6: Status (se presente)
    if 'status' in record and not pd.isna(record['status']) and str(record['status']).strip():
        valid_statuses = ['active', 'inactive', 'pending', 'suspended', 'deleted']
        status = str(record['status']).lower().strip()
        if status not in valid_statuses:
            errors.append(f"Status inválido '{status}' (valores válidos: {valid_statuses})")
    
    # Verificação 7: Data de criação (se presente)
    if 'created_at' in record and not pd.isna(record['created_at']):
        try:
            # Tentar converter para datetime
            pd.to_datetime(record['created_at'])
        except (ValueError, TypeError):
            errors.append("Data de criação deve ter formato válido")
    
    # Determinar resultado
    if errors:
        return ValidationResult(
            success=False,
            message=f"Registro {record_index} inválido: {'; '.join(errors)}",
            details={
                "record_index": record_index,
                "errors": errors,
                "warnings": warnings,
                "record_data": {k: v for k, v in record.items() if k != '_record_index'}
            }
        )
    
    # Se há warnings, ainda é válido mas com avisos
    if warnings:
        return ValidationResult(
            success=True,
            message=f"Registro {record_index} válido com avisos: {'; '.join(warnings)}",
            details={
                "record_index": record_index,
                "errors": [],
                "warnings": warnings,
                "record_data": {k: v for k, v in record.items() if k != '_record_index'}
            }
        )
    
    # Registro completamente válido
    return ValidationResult(
        success=True,
        message=f"Registro {record_index} válido",
        details={
            "record_index": record_index,
            "errors": [],
            "warnings": [],
            "record_data": {k: v for k, v in record.items() if k != '_record_index'}
        }
    )


# Função de validação tradicional para compatibilidade
def validate(data: pd.DataFrame, context: Dict[str, Any] = None) -> ValidationResult:
    """
    Validação tradicional (executada uma vez para todo o dataset)
    """
    
    if data.empty:
        return ValidationResult(
            success=False,
            message="Nenhum dado de usuário encontrado",
            details={"row_count": 0}
        )
    
    # Verificações básicas no dataset completo
    required_columns = ['name', 'email']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        return ValidationResult(
            success=False,
            message=f"Colunas obrigatórias ausentes: {missing_columns}",
            details={"missing_columns": missing_columns}
        )
    
    # Contar problemas básicos
    total_records = len(data)
    null_names = data['name'].isnull().sum()
    null_emails = data['email'].isnull().sum()
    
    if null_names > 0 or null_emails > 0:
        return ValidationResult(
            success=False,
            message=f"Encontrados {null_names} nomes nulos e {null_emails} emails nulos",
            details={
                "total_records": total_records,
                "null_names": int(null_names),
                "null_emails": int(null_emails)
            }
        )
    
    return ValidationResult(
        success=True,
        message=f"Validação básica de usuários passou: {total_records} registros",
        details={"total_records": total_records}
    )
