"""
Gerenciamento de conexões de banco de dados
"""

import sqlite3
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from .types import Connection, ConnectionType, ConnectionParams


class DatabaseConnection(ABC):
    """Interface para conexões de banco de dados"""
    
    @abstractmethod
    def execute_query(self, sql: str) -> pd.DataFrame:
        """Executa uma query e retorna DataFrame"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Testa se a conexão está funcionando"""
        pass
    
    @abstractmethod
    def close(self):
        """Fecha a conexão"""
        pass
    
    def set_schema(self, schema: str):
        """Define o schema padrão para queries (implementação opcional)"""
        pass
    
    def get_schema(self) -> Optional[str]:
        """Retorna o schema padrão configurado"""
        return getattr(self.params, 'schema', None)
    
    def _apply_schema_to_query(self, sql: str) -> str:
        """Aplica o schema padrão à query SQL se necessário"""
        schema = self.get_schema()
        if not schema:
            return sql
        
        # Para PostgreSQL, MySQL e MSSQL, adiciona schema prefix quando necessário
        # Esta é uma implementação básica - pode ser expandida conforme necessário
        return sql


class SQLiteConnection(DatabaseConnection):
    """Conexão SQLite"""
    
    def __init__(self, params: ConnectionParams):
        self.params = params
        self.connection: Optional[sqlite3.Connection] = None
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtém conexão SQLite"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.params.filepath)
        return self.connection
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """Executa query SQLite"""
        conn = self._get_connection()
        return pd.read_sql_query(sql, conn)
    
    def test_connection(self) -> bool:
        """Testa conexão SQLite"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def close(self):
        """Fecha conexão SQLite"""
        if self.connection:
            self.connection.close()
            self.connection = None


class PostgreSQLConnection(DatabaseConnection):
    """Conexão PostgreSQL"""
    
    def __init__(self, params: ConnectionParams):
        self.params = params
        self.connection = None
        self._import_psycopg()
    
    def _import_psycopg(self):
        """Importa psycopg2 dinamicamente"""
        try:
            import psycopg2
            self.psycopg2 = psycopg2
        except ImportError:
            raise ImportError(
                "psycopg2 não está instalado. Instale com: pip install psycopg2-binary"
            )
    
    def _get_connection(self):
        """Obtém conexão PostgreSQL"""
        if self.connection is None:
            self.connection = self.psycopg2.connect(
                host=self.params.host,
                port=self.params.port,
                database=self.params.database,
                user=self.params.user,
                password=self.params.password,
                **(self.params.extra_params or {})
            )
            # Configura schema padrão se especificado
            if self.params.schema:
                cursor = self.connection.cursor()
                cursor.execute(f"SET search_path TO {self.params.schema}")
                self.connection.commit()
        return self.connection
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """Executa query PostgreSQL"""
        conn = self._get_connection()
        return pd.read_sql_query(sql, conn)
    
    def set_schema(self, schema: str):
        """Define o schema padrão para queries PostgreSQL"""
        self.params.schema = schema
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SET search_path TO {schema}")
            self.connection.commit()
    
    def test_connection(self) -> bool:
        """Testa conexão PostgreSQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def close(self):
        """Fecha conexão PostgreSQL"""
        if self.connection:
            self.connection.close()
            self.connection = None


class MySQLConnection(DatabaseConnection):
    """Conexão MySQL (estrutura pronta)"""
    
    def __init__(self, params: ConnectionParams):
        self.params = params
        self.connection = None
        self._import_mysql()
    
    def _import_mysql(self):
        """Importa mysql-connector-python dinamicamente"""
        try:
            import mysql.connector
            self.mysql = mysql.connector
        except ImportError:
            raise ImportError(
                "mysql-connector-python não está instalado. Instale com: pip install mysql-connector-python"
            )
    
    def _get_connection(self):
        """Obtém conexão MySQL"""
        if self.connection is None:
            self.connection = self.mysql.connect(
                host=self.params.host,
                port=self.params.port,
                database=self.params.database,
                user=self.params.user,
                password=self.params.password,
                **(self.params.extra_params or {})
            )
            # Configura schema padrão se especificado
            if self.params.schema:
                cursor = self.connection.cursor()
                cursor.execute(f"USE {self.params.schema}")
        return self.connection
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """Executa query MySQL"""
        conn = self._get_connection()
        return pd.read_sql_query(sql, conn)
    
    def set_schema(self, schema: str):
        """Define o schema padrão para queries MySQL"""
        self.params.schema = schema
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {schema}")
    
    def test_connection(self) -> bool:
        """Testa conexão MySQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def close(self):
        """Fecha conexão MySQL"""
        if self.connection:
            self.connection.close()
            self.connection = None


class MSSQLConnection(DatabaseConnection):
    """Conexão MSSQL (estrutura pronta)"""
    
    def __init__(self, params: ConnectionParams):
        self.params = params
        self.connection = None
        self._import_pymssql()
    
    def _import_pymssql(self):
        """Importa pymssql dinamicamente"""
        try:
            import pymssql
            self.pymssql = pymssql
        except ImportError:
            raise ImportError(
                "pymssql não está instalado. Instale com: pip install pymssql"
            )
    
    def _get_connection(self):
        """Obtém conexão MSSQL"""
        if self.connection is None:
            self.connection = self.pymssql.connect(
                server=self.params.host,
                port=self.params.port,
                database=self.params.database,
                user=self.params.user,
                password=self.params.password,
                **(self.params.extra_params or {})
            )
            # Configura schema padrão se especificado
            if self.params.schema:
                cursor = self.connection.cursor()
                cursor.execute(f"USE {self.params.schema}")
        return self.connection
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """Executa query MSSQL"""
        conn = self._get_connection()
        return pd.read_sql_query(sql, conn)
    
    def set_schema(self, schema: str):
        """Define o schema padrão para queries MSSQL"""
        self.params.schema = schema
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {schema}")
    
    def test_connection(self) -> bool:
        """Testa conexão MSSQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def close(self):
        """Fecha conexão MSSQL"""
        if self.connection:
            self.connection.close()
            self.connection = None


class OracleConnection(DatabaseConnection):
    """Conexão Oracle"""
    
    def __init__(self, params: ConnectionParams):
        self.params = params
        self.connection = None
        self._import_cx_oracle()
    
    def _import_cx_oracle(self):
        """Importa cx_Oracle dinamicamente"""
        try:
            import cx_Oracle
            self.cx_Oracle = cx_Oracle
        except ImportError:
            raise ImportError(
                "cx_Oracle não está instalado. Instale com: pip install cx_Oracle"
            )
    
    def _get_connection(self):
        """Obtém conexão Oracle"""
        if self.connection is None:
            # Verificar se é conexão via TNS Names
            if self._is_tns_connection():
                dsn = self.params.database  # Usar diretamente o TNS Name
            else:
                # Construir DSN (Data Source Name) para Oracle
                dsn = self.cx_Oracle.makedsn(
                    self.params.host,
                    self.params.port,
                    service_name=self.params.database
                )
            
            self.connection = self.cx_Oracle.connect(
                user=self.params.user,
                password=self.params.password,
                dsn=dsn,
                **(self.params.extra_params or {})
            )
            
            # Configura schema padrão se especificado
            if self.params.schema:
                cursor = self.connection.cursor()
                cursor.execute(f"ALTER SESSION SET CURRENT_SCHEMA = {self.params.schema}")
                self.connection.commit()
        return self.connection
    
    def _is_tns_connection(self) -> bool:
        """Verifica se é uma conexão via TNS Names"""
        # Se não tem host ou porta, assume que é TNS Names
        if not self.params.host or not self.params.port:
            return True
        
        # Se o database contém caracteres especiais de TNS (parênteses, etc)
        if '(' in self.params.database or ')' in self.params.database:
            return True
            
        # Se tem parâmetro tns_name explícito
        if hasattr(self.params, 'tns_name') and self.params.tns_name:
            return True
            
        return False
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """Executa query Oracle"""
        conn = self._get_connection()
        return pd.read_sql_query(sql, conn)
    
    def set_schema(self, schema: str):
        """Define o schema padrão para queries Oracle"""
        self.params.schema = schema
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"ALTER SESSION SET CURRENT_SCHEMA = {schema}")
            self.connection.commit()
    
    def test_connection(self) -> bool:
        """Testa conexão Oracle"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def close(self):
        """Fecha conexão Oracle"""
        if self.connection:
            self.connection.close()
            self.connection = None


class CSVConnection(DatabaseConnection):
    """Conexão para leitura de arquivos CSV"""
    
    def __init__(self, params: ConnectionParams):
        self.params = params
        self._validate_csv_params()
    
    def _validate_csv_params(self):
        """Valida parâmetros específicos do CSV"""
        if not self.params.csv_file:
            raise ValueError("csv_file é obrigatório para conexões CSV")
        
        if not os.path.exists(self.params.csv_file):
            raise ValueError(f"Arquivo CSV não encontrado: {self.params.csv_file}")
    
    def _get_csv_params(self) -> Dict[str, Any]:
        """Obtém parâmetros para leitura do CSV"""
        params = {
            'sep': self.params.csv_separator or ',',
            'encoding': self.params.csv_encoding or 'utf-8',
            'header': 0 if self.params.csv_has_header is not False else None
        }
        
        # Adicionar parâmetros extras se existirem
        if self.params.extra_params:
            params.update(self.params.extra_params)
        
        return params
    
    def execute_query(self, sql: Optional[str] = None) -> pd.DataFrame:
        """
        Lê arquivo CSV e retorna DataFrame
        
        Args:
            sql: Ignorado para conexões CSV (mantido para compatibilidade)
            
        Returns:
            DataFrame com dados do CSV
        """
        try:
            csv_params = self._get_csv_params()
            df = pd.read_csv(self.params.csv_file, **csv_params)
            return df
        except Exception as e:
            raise ValueError(f"Erro ao ler arquivo CSV {self.params.csv_file}: {e}")
    
    def test_connection(self) -> bool:
        """Testa se o arquivo CSV pode ser lido"""
        try:
            self.execute_query()
            return True
        except Exception:
            return False
    
    def close(self):
        """Não há conexão para fechar em arquivos CSV"""
        pass
    
    def get_file_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o arquivo CSV"""
        if not os.path.exists(self.params.csv_file):
            return {"error": "Arquivo não encontrado"}
        
        try:
            stat = os.stat(self.params.csv_file)
            return {
                "file_path": self.params.csv_file,
                "file_size": stat.st_size,
                "modified_time": stat.st_mtime,
                "separator": self.params.csv_separator or ',',
                "encoding": self.params.csv_encoding or 'utf-8',
                "has_header": self.params.csv_has_header is not False
            }
        except Exception as e:
            return {"error": str(e)}


class ConnectionFactory:
    """Fábrica de conexões"""
    
    _connection_classes = {
        ConnectionType.SQLITE: SQLiteConnection,
        ConnectionType.POSTGRES: PostgreSQLConnection,
        ConnectionType.MYSQL: MySQLConnection,
        ConnectionType.MSSQL: MSSQLConnection,
        ConnectionType.ORACLE: OracleConnection,
        ConnectionType.CSV: CSVConnection,
    }
    
    @classmethod
    def create_connection(cls, connection: Connection) -> DatabaseConnection:
        """
        Cria uma conexão baseada na configuração
        
        Args:
            connection: Configuração da conexão
            
        Returns:
            Instância de DatabaseConnection
            
        Raises:
            ValueError: Se tipo de conexão não suportado
        """
        if connection.type not in cls._connection_classes:
            raise ValueError(f"Tipo de conexão não suportado: {connection.type}")
        
        # Processar variáveis de ambiente nos parâmetros da conexão
        from .env_processor import EnvironmentVariableProcessor
        env_processor = EnvironmentVariableProcessor()
        
        # Converter params para dict, processar variáveis e criar nova instância
        params_dict = connection.params.__dict__.copy()
        processed_params = env_processor.process_dict(params_dict)
        
        # Criar nova instância de ConnectionParams com valores processados
        processed_params_obj = connection.params.__class__(**processed_params)
        
        connection_class = cls._connection_classes[connection.type]
        return connection_class(processed_params_obj)
    
    @classmethod
    def get_supported_types(cls) -> list:
        """Retorna lista de tipos de conexão suportados"""
        return list(cls._connection_classes.keys())


def create_connection_with_schema(connection: Connection, schema: Optional[str] = None) -> DatabaseConnection:
    """
    Cria uma conexão e configura o schema se especificado
    
    Args:
        connection: Configuração da conexão
        schema: Schema opcional para sobrescrever o configurado
        
    Returns:
        Instância de DatabaseConnection com schema configurado
    """
    db_connection = ConnectionFactory.create_connection(connection)
    
    # Se um schema foi especificado, usa ele; senão usa o da configuração
    target_schema = schema or connection.params.schema
    
    if target_schema:
        db_connection.set_schema(target_schema)
    
    return db_connection
