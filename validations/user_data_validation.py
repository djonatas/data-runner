"""
Validação de dados de usuários

Este arquivo contém validações específicas para dados de usuários,
incluindo verificações de email, telefone, CPF, etc.
"""

import pandas as pd
import re
from typing import Dict, Any
from app.validation_engine import ValidationResult

description = "Validação de dados de usuários com verificações de email, telefone e CPF"
requirements = [
    "Coluna 'email' deve existir e ter formato válido",
    "Coluna 'phone' deve existir e ter formato válido",
    "Coluna 'cpf' deve existir e ter formato válido (se presente)",
    "Nenhum email duplicado deve existir"
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
    
    # Remove caracteres não numéricos
    phone_clean = re.sub(r'[^\d]', '', phone)
    
    # Telefone deve ter 10 ou 11 dígitos
    return len(phone_clean) in [10, 11]


def validate_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro"""
    if pd.isna(cpf) or not isinstance(cpf, str):
        return False
    
    # Remove caracteres não numéricos
    cpf_clean = re.sub(r'[^\d]', '', cpf)
    
    # CPF deve ter 11 dígitos
    if len(cpf_clean) != 11:
        return False
    
    # Verificar se todos os dígitos são iguais
    if cpf_clean == cpf_clean[0] * 11:
        return False
    
    # Algoritmo de validação de CPF
    def calculate_digit(cpf_digits: str, multiplier: int) -> int:
        total = sum(int(digit) * (multiplier - i) for i, digit in enumerate(cpf_digits))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Calcular primeiro dígito verificador
    first_digit = calculate_digit(cpf_clean[:9], 10)
    if int(cpf_clean[9]) != first_digit:
        return False
    
    # Calcular segundo dígito verificador
    second_digit = calculate_digit(cpf_clean[:10], 11)
    if int(cpf_clean[10]) != second_digit:
        return False
    
    return True


def validate(data: pd.DataFrame, context: Dict[str, Any] = None) -> ValidationResult:
    """
    Valida dados de usuários
    
    Args:
        data: DataFrame com dados de usuários
        context: Contexto adicional
        
    Returns:
        ValidationResult com o resultado da validação
    """
    
    if data.empty:
        return ValidationResult(
            success=False,
            message="Nenhum dado de usuário encontrado",
            details={"row_count": 0}
        )
    
    checks = []
    
    # Verificação 1: Colunas obrigatórias
    required_columns = ['email', 'phone']
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
    
    # Verificação 2: Emails válidos
    if 'email' in data.columns:
        invalid_emails = data['email'].apply(lambda x: not validate_email(x)).sum()
        total_emails = len(data['email'].dropna())
        
        if invalid_emails > 0:
            checks.append({
                "check": "emails_validos",
                "status": "FAILED",
                "message": f"Encontrados {invalid_emails} emails inválidos de {total_emails} total",
                "details": {
                    "invalid_count": int(invalid_emails),
                    "total_count": int(total_emails),
                    "valid_percentage": round((total_emails - invalid_emails) / total_emails * 100, 2)
                }
            })
        else:
            checks.append({
                "check": "emails_validos",
                "status": "PASSED",
                "message": "Todos os emails são válidos",
                "details": {"total_count": int(total_emails)}
            })
    
    # Verificação 3: Emails duplicados
    if 'email' in data.columns:
        duplicate_emails = data['email'].duplicated().sum()
        if duplicate_emails > 0:
            checks.append({
                "check": "emails_duplicados",
                "status": "FAILED",
                "message": f"Encontrados {duplicate_emails} emails duplicados",
                "details": {"duplicate_count": int(duplicate_emails)}
            })
        else:
            checks.append({
                "check": "emails_duplicados",
                "status": "PASSED",
                "message": "Nenhum email duplicado encontrado",
                "details": {"duplicate_count": 0}
            })
    
    # Verificação 4: Telefones válidos
    if 'phone' in data.columns:
        invalid_phones = data['phone'].apply(lambda x: not validate_phone(x)).sum()
        total_phones = len(data['phone'].dropna())
        
        if invalid_phones > 0:
            checks.append({
                "check": "telefones_validos",
                "status": "FAILED",
                "message": f"Encontrados {invalid_phones} telefones inválidos de {total_phones} total",
                "details": {
                    "invalid_count": int(invalid_phones),
                    "total_count": int(total_phones),
                    "valid_percentage": round((total_phones - invalid_phones) / total_phones * 100, 2)
                }
            })
        else:
            checks.append({
                "check": "telefones_validos",
                "status": "PASSED",
                "message": "Todos os telefones são válidos",
                "details": {"total_count": int(total_phones)}
            })
    
    # Verificação 5: CPFs válidos (se presente)
    if 'cpf' in data.columns:
        invalid_cpfs = data['cpf'].apply(lambda x: not validate_cpf(x)).sum()
        total_cpfs = len(data['cpf'].dropna())
        
        if total_cpfs > 0:  # Só valida se há CPFs
            if invalid_cpfs > 0:
                checks.append({
                    "check": "cpfs_validos",
                    "status": "FAILED",
                    "message": f"Encontrados {invalid_cpfs} CPFs inválidos de {total_cpfs} total",
                    "details": {
                        "invalid_count": int(invalid_cpfs),
                        "total_count": int(total_cpfs),
                        "valid_percentage": round((total_cpfs - invalid_cpfs) / total_cpfs * 100, 2)
                    }
                })
            else:
                checks.append({
                    "check": "cpfs_validos",
                    "status": "PASSED",
                    "message": "Todos os CPFs são válidos",
                    "details": {"total_count": int(total_cpfs)}
                })
        else:
            checks.append({
                "check": "cpfs_validos",
                "status": "SKIPPED",
                "message": "Nenhum CPF encontrado para validação",
                "details": {"total_count": 0}
            })
    
    # Verificação 6: Dados nulos críticos
    critical_columns = ['email', 'phone']
    null_summary = {}
    
    for col in critical_columns:
        if col in data.columns:
            null_count = data[col].isnull().sum()
            null_summary[col] = int(null_count)
    
    if any(null_summary.values()):
        checks.append({
            "check": "dados_nulos_criticos",
            "status": "FAILED",
            "message": f"Dados nulos encontrados em colunas críticas",
            "details": {"null_counts": null_summary}
        })
    else:
        checks.append({
            "check": "dados_nulos_criticos",
            "status": "PASSED",
            "message": "Nenhum dado nulo em colunas críticas",
            "details": {"null_counts": null_summary}
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
        overall_message = f"Validação de usuários passou: {len(checks)} verificação(ões) executadas com sucesso"
    
    # Detalhes da validação
    details = {
        "total_checks": len(checks),
        "passed_checks": len([c for c in checks if c["status"] == "PASSED"]),
        "failed_checks": len(failed_checks),
        "error_checks": len(error_checks),
        "skipped_checks": len([c for c in checks if c["status"] == "SKIPPED"]),
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
