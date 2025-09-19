"""
Tipos e contratos para o sistema Data-Runner
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid
import json


class JobType(Enum):
    """Tipos de job suportados"""
    CARGA = "carga"
    BATIMENTO = "batimento"
    EXPORT_CSV = "export-csv"
    VALIDATION = "validation"


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
    # Parâmetros específicos para export-csv
    csv_file: Optional[str] = None  # Nome do arquivo CSV de saída
    csv_separator: Optional[str] = None  # Separador do CSV (padrão: ',')
    csv_encoding: Optional[str] = None  # Encoding do arquivo (padrão: 'utf-8')
    csv_include_header: Optional[bool] = None  # Se inclui cabeçalho (padrão: True)
    # Parâmetros específicos para validation
    validation_file: Optional[str] = None  # Caminho do arquivo Python de validação
    main_query: Optional[str] = None  # queryId da query principal para validação
    # Parâmetros para tabela de output de validação
    output_table: Optional[str] = None  # Nome da tabela de output para resultados
    pkey_field: Optional[str] = None  # Campo chave primária para indexação


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
    csv_file: Optional[str] = None  # Arquivo CSV exportado (para jobs export-csv)
    validation_file: Optional[str] = None  # Arquivo de validação executado
    validation_result: Optional[str] = None  # Resultado da validação (JSON string)

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
class JobGroup:
    """Grupo de jobs para execução em sequência"""
    name: str
    description: Optional[str] = None
    job_ids: List[str] = field(default_factory=list)


@dataclass
class JobsConfig:
    """Configuração de jobs"""
    jobs: List[Job]
    variables: Optional[Dict[str, Variable]] = None
    job_groups: Optional[Dict[str, JobGroup]] = None


@dataclass
class ValidationRecord:
    """Registro de validação individual para tabela de output"""
    execution_count: int
    pkey: str
    result: str  # "success" ou "error"
    message: str
    details: str  # JSON string com detalhes
    input_data: str  # JSON string com dados do registro
    executed_at: str  # ISO timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "execution_count": self.execution_count,
            "pkey": self.pkey,
            "result": self.result,
            "message": self.message,
            "details": self.details,
            "input_data": self.input_data,
            "executed_at": self.executed_at
        }


@dataclass
class ExecutionOptions:
    """Opções de execução"""
    dry_run: bool = False
    limit: Optional[int] = None
    save_as: Optional[str] = None
    duckdb_path: Optional[str] = None
