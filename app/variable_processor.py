"""
Sistema de processamento de variáveis para queries SQL
"""

import re
from typing import Dict, Any, Optional
from .types import Variable, VariableType


class VariableProcessor:
    """Processador de variáveis para substituição em queries SQL"""
    
    def __init__(self, variables: Optional[Dict[str, Variable]] = None):
        """
        Inicializa o processador de variáveis
        
        Args:
            variables: Dicionário de variáveis disponíveis
        """
        self.variables = variables or {}
    
    def add_variable(self, variable: Variable):
        """Adiciona uma variável ao processador"""
        self.variables[variable.name] = variable
    
    def add_variables(self, variables: Dict[str, Variable]):
        """Adiciona múltiplas variáveis ao processador"""
        self.variables.update(variables)
    
    def get_variable_value(self, name: str) -> Any:
        """
        Obtém o valor de uma variável
        
        Args:
            name: Nome da variável
            
        Returns:
            Valor da variável processado conforme seu tipo
            
        Raises:
            KeyError: Se a variável não existir
        """
        if name not in self.variables:
            raise KeyError(f"Variável '{name}' não encontrada")
        
        variable = self.variables[name]
        return self._process_variable_value(variable.value, variable.type)
    
    def _process_variable_value(self, value: Any, var_type: VariableType) -> Any:
        """
        Processa o valor da variável conforme seu tipo
        
        Args:
            value: Valor bruto da variável
            var_type: Tipo da variável
            
        Returns:
            Valor processado
        """
        if var_type == VariableType.STRING:
            return str(value)
        elif var_type == VariableType.NUMBER:
            if isinstance(value, (int, float)):
                return value
            try:
                # Tenta converter para int primeiro, depois float
                if '.' not in str(value):
                    return int(value)
                else:
                    return float(value)
            except ValueError:
                raise ValueError(f"Não foi possível converter '{value}' para número")
        elif var_type == VariableType.BOOLEAN:
            if isinstance(value, bool):
                return value
            value_str = str(value).lower()
            if value_str in ('true', '1', 'yes', 'on', 'verdadeiro'):
                return True
            elif value_str in ('false', '0', 'no', 'off', 'falso'):
                return False
            else:
                raise ValueError(f"Não foi possível converter '{value}' para booleano")
        else:
            return value
    
    def process_sql(self, sql: str) -> str:
        """
        Processa uma query SQL substituindo variáveis
        
        Args:
            sql: Query SQL com variáveis no formato ${var:nome_variavel}
            
        Returns:
            Query SQL com variáveis substituídas
            
        Raises:
            KeyError: Se alguma variável não existir
            ValueError: Se algum valor não puder ser convertido
        """
        # Padrão para encontrar variáveis: ${var:nome_variavel}
        pattern = r'\$\{var:([^}]+)\}'
        
        def replace_variable(match):
            var_name = match.group(1).strip()
            value = self.get_variable_value(var_name)
            
            # Formatar o valor conforme o tipo
            if isinstance(value, str):
                # Escapar aspas simples para SQL
                escaped_value = value.replace("'", "''")
                return f"'{escaped_value}'"
            elif isinstance(value, bool):
                # Converter booleano para string SQL
                return 'TRUE' if value else 'FALSE'
            else:
                # Números e outros tipos
                return str(value)
        
        try:
            return re.sub(pattern, replace_variable, sql)
        except Exception as e:
            raise ValueError(f"Erro ao processar variáveis na query: {e}")
    
    def list_variables(self) -> Dict[str, Any]:
        """
        Lista todas as variáveis disponíveis
        
        Returns:
            Dicionário com nome e valor das variáveis
        """
        result = {}
        for name, variable in self.variables.items():
            try:
                result[name] = self.get_variable_value(name)
            except Exception as e:
                result[name] = f"<erro: {e}>"
        return result
    
    def validate_variables(self) -> Dict[str, str]:
        """
        Valida todas as variáveis e retorna erros encontrados
        
        Returns:
            Dicionário com nome da variável e erro (se houver)
        """
        errors = {}
        for name, variable in self.variables.items():
            try:
                self._process_variable_value(variable.value, variable.type)
            except Exception as e:
                errors[name] = str(e)
        return errors
