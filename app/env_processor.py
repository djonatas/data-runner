"""
Processador de variáveis de ambiente para configurações
"""

import os
import re
from typing import Any, Dict
import logging
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnvironmentVariableProcessor:
    """Processa variáveis de ambiente em strings de configuração"""
    
    def __init__(self, load_dotenv_file: bool = True):
        self.logger = logger
        self._dotenv_loaded = False
        
        if load_dotenv_file:
            self._load_dotenv()
    
    def _load_dotenv(self):
        """Carrega arquivo .env se disponível"""
        if not DOTENV_AVAILABLE:
            self.logger.debug("python-dotenv não disponível, pulando carregamento de .env")
            return
        
        # Procurar arquivo .env em vários locais
        possible_paths = [
            Path.cwd() / '.env',  # Diretório atual
            Path.cwd().parent / '.env',  # Diretório pai
            Path(__file__).parent.parent / '.env',  # Raiz do projeto
            Path.home() / '.env',  # Home do usuário
        ]
        
        for env_path in possible_paths:
            if env_path.exists():
                self.logger.info(f"Carregando variáveis de ambiente de: {env_path}")
                load_dotenv(env_path, override=True)
                self._dotenv_loaded = True
                return
        
        self.logger.debug("Arquivo .env não encontrado em nenhum dos locais esperados")
    
    def is_dotenv_loaded(self) -> bool:
        """Retorna se o arquivo .env foi carregado"""
        return self._dotenv_loaded
    
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
