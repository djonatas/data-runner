"""
Utilitários para manipulação de SQL
"""

import os
import re
from typing import Optional


def expand_env_vars(sql: str) -> str:
    """
    Expande variáveis de ambiente no formato ${env:VAR} no SQL
    
    Args:
        sql: SQL com possíveis variáveis de ambiente
        
    Returns:
        SQL com variáveis expandidas
    """
    pattern = r'\$\{env:([^}]+)\}'
    
    def replace_env_var(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))
    
    return re.sub(pattern, replace_env_var, sql)


def apply_limit(sql: str, limit: int) -> str:
    """
    Aplica LIMIT ao SQL se possível
    
    Args:
        sql: SQL original
        limit: Número máximo de linhas
        
    Returns:
        SQL com LIMIT aplicado
    """
    if not limit or limit <= 0:
        return sql
    
    # Remove espaços extras e quebras de linha
    sql_clean = ' '.join(sql.split())
    
    # Se já tem LIMIT, substitui
    if re.search(r'\bLIMIT\s+\d+', sql_clean, re.IGNORECASE):
        return re.sub(
            r'\bLIMIT\s+\d+',
            f'LIMIT {limit}',
            sql_clean,
            flags=re.IGNORECASE
        )
    
    # Se não tem LIMIT, adiciona no final
    return f"{sql_clean} LIMIT {limit}"


def sanitize_table_name(name: str) -> str:
    """
    Sanitiza nome de tabela para ser válido no DuckDB
    
    Args:
        name: Nome original da tabela
        
    Returns:
        Nome sanitizado
    """
    # Remove caracteres especiais e substitui por underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Remove underscores múltiplos
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove underscores do início e fim
    sanitized = sanitized.strip('_')
    
    # Se ficou vazio, usa nome padrão
    if not sanitized:
        sanitized = 'table'
    
    # Garante que comece com letra ou underscore
    if not re.match(r'^[a-zA-Z_]', sanitized):
        sanitized = f'table_{sanitized}'
    
    return sanitized


def get_default_target_table(query_id: str, job_type: str) -> str:
    """
    Gera nome padrão de tabela baseado no query_id e tipo
    
    Args:
        query_id: ID da query
        job_type: Tipo do job (carga ou batimento)
        
    Returns:
        Nome da tabela padrão
    """
    prefix = "stg" if job_type == "carga" else "val"
    return f"{prefix}_{query_id}"


def truncate_sql_for_log(sql: str, max_length: int = 200) -> str:
    """
    Trunca SQL para exibição em logs
    
    Args:
        sql: SQL original
        max_length: Tamanho máximo
        
    Returns:
        SQL truncado
    """
    if len(sql) <= max_length:
        return sql
    
    return sql[:max_length] + "..."
