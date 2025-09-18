"""
Tipos e contratos para o sistema Data-Runner
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid


class JobType(Enum):
    """Tipos de job suportados"""
    CARGA = "carga"
    BATIMENTO = "batimento"


class JobStatus(Enum):
    """Status de execução de jobs"""
    SUCCESS = "success"
    ERROR = "error"


class ConnectionType(Enum):
    """Tipos de conexão suportados"""
    POSTGRES = "postgres"
    SQLITE = "sqlite"
    MYSQL = "mysql"
    MSSQL = "mssql"
    ORACLE = "oracle"
    CSV = "csv"


class VariableType(Enum):
    """Tipos de variáveis suportados"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


@dataclass
class ConnectionParams:
    """Parâmetros de conexão genéricos"""
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    filepath: Optional[str] = None
    schema: Optional[str] = None  # Schema padrão para queries
    # Parâmetros específicos para CSV
    csv_file: Optional[str] = None  # Caminho do arquivo CSV
    csv_separator: Optional[str] = None  # Separador do CSV (padrão: ',')
    csv_encoding: Optional[str] = None  # Encoding do arquivo (padrão: 'utf-8')
    csv_has_header: Optional[bool] = None  # Se tem cabeçalho (padrão: True)
    # Parâmetros adicionais para outros tipos de banco
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class Variable:
    """Definição de uma variável"""
    name: str
    value: Any
    type: VariableType
    description: Optional[str] = None


@dataclass
class Connection:
    """Definição de uma conexão"""
    name: str
    type: ConnectionType
    params: ConnectionParams


@dataclass
class Job:
    """Definição de um job"""
    query_id: str
    type: JobType
    connection: str
    sql: Optional[str] = None  # Opcional para conexões CSV
    target_table: Optional[str] = None
    dependencies: Optional[List[str]] = None  # Lista de query_ids dos jobs dependentes


@dataclass
class JobRun:
    """Registro de execução de um job"""
    run_id: str
    query_id: str
    type: JobType
    started_at: str
    finished_at: Optional[str] = None
    status: Optional[JobStatus] = None
    rowcount: Optional[int] = None
    error: Optional[str] = None
    target_table: Optional[str] = None
    connection: Optional[str] = None

    @classmethod
    def create_new(cls, query_id: str, job_type: JobType) -> "JobRun":
        """Cria um novo JobRun com ID único"""
        return cls(
            run_id=str(uuid.uuid4()),
            query_id=query_id,
            type=job_type,
            started_at="",  # Será preenchido pelo runner
        )


@dataclass
class ConnectionsConfig:
    """Configuração de conexões"""
    default_duckdb_path: str
    connections: List[Connection]


@dataclass
class JobsConfig:
    """Configuração de jobs"""
    jobs: List[Job]
    variables: Optional[Dict[str, Variable]] = None


@dataclass
class ExecutionOptions:
    """Opções de execução"""
    dry_run: bool = False
    limit: Optional[int] = None
    save_as: Optional[str] = None
    duckdb_path: Optional[str] = None
