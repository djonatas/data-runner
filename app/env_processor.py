"""
Processador de variáveis de ambiente para configurações
"""

import os
import re
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class EnvironmentVariableProcessor:
    """Processa variáveis de ambiente em strings de configuração"""
    
    def __init__(self):
        self.logger = logger
    
    def process_string(self, text: str) -> str:
        """
        Processa uma string substituindo variáveis de ambiente
        
        Args:
            text: String que pode conter variáveis ${env:VARIABLE_NAME}
            
        Returns:
            String com variáveis substituídas
        """
        if not isinstance(text, str):
            return text
        
        # Padrão para encontrar ${env:VARIABLE_NAME}
        pattern = r'\$\{env:([^}]+)\}'
        
        def replace_env_var(match):
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            
            if env_value is None:
                self.logger.warning(f"Variável de ambiente '{var_name}' não encontrada")
                return match.group(0)  # Mantém o padrão original se não encontrar
            
            self.logger.debug(f"Substituindo {match.group(0)} por valor da variável de ambiente '{var_name}'")
            return env_value
        
        return re.sub(pattern, replace_env_var, text)
    
    def process_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um dicionário recursivamente substituindo variáveis de ambiente
        
        Args:
            data: Dicionário com dados que podem conter variáveis de ambiente
            
        Returns:
            Dicionário com variáveis substituídas
        """
        if not isinstance(data, dict):
            return data
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.process_string(value)
            elif isinstance(value, dict):
                result[key] = self.process_dict(value)
            elif isinstance(value, list):
                result[key] = self.process_list(value)
            else:
                result[key] = value
        
        return result
    
    def process_list(self, data: list) -> list:
        """
        Processa uma lista recursivamente substituindo variáveis de ambiente
        
        Args:
            data: Lista com dados que podem conter variáveis de ambiente
            
        Returns:
            Lista com variáveis substituídas
        """
        if not isinstance(data, list):
            return data
        
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self.process_string(item))
            elif isinstance(item, dict):
                result.append(self.process_dict(item))
            elif isinstance(item, list):
                result.append(self.process_list(item))
            else:
                result.append(item)
        
        return result
