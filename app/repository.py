"""
Repositório para persistência no DuckDB
"""

import os
from datetime import datetime
from typing import Optional
import pandas as pd
import duckdb
from .types import JobRun, JobStatus, JobType


class DuckDBRepository:
    """Repositório para operações no DuckDB"""
    
    def __init__(self, db_path: str):
        """
        Inicializa repositório DuckDB
        
        Args:
            db_path: Caminho para o arquivo DuckDB
        """
        self.db_path = db_path
        self._ensure_data_directory()
        self._create_audit_table()
    
    def _ensure_data_directory(self):
        """Garante que o diretório data existe"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
    
    def _create_audit_table(self):
        """Cria tabela de auditoria se não existir"""
        create_audit_sql = """
        CREATE TABLE IF NOT EXISTS audit_job_runs (
            run_id VARCHAR PRIMARY KEY,
            query_id VARCHAR NOT NULL,
            type VARCHAR NOT NULL,
            started_at VARCHAR NOT NULL,
            finished_at VARCHAR,
            status VARCHAR,
            rowcount INTEGER,
            error VARCHAR,
            target_table VARCHAR,
            connection VARCHAR
        )
        """
        
        with duckdb.connect(self.db_path) as conn:
            conn.execute(create_audit_sql)
    
    def save_dataframe(self, df: pd.DataFrame, table_name: str, replace: bool = True):
        """
        Salva DataFrame no DuckDB
        
        Args:
            df: DataFrame para salvar
            table_name: Nome da tabela
            replace: Se True, substitui tabela existente
        """
        with duckdb.connect(self.db_path) as conn:
            if replace:
                # Remove tabela se existir
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # Cria tabela a partir do DataFrame
            conn.register('temp_df', df)
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_df")
    
    def save_job_run(self, job_run: JobRun):
        """
        Salva registro de execução de job
        
        Args:
            job_run: Dados do job run
        """
        with duckdb.connect(self.db_path) as conn:
            insert_sql = """
            INSERT OR REPLACE INTO audit_job_runs 
            (run_id, query_id, type, started_at, finished_at, status, 
             rowcount, error, target_table, connection)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            conn.execute(insert_sql, (
                job_run.run_id,
                job_run.query_id,
                job_run.type.value,
                job_run.started_at,
                job_run.finished_at,
                job_run.status.value if job_run.status else None,
                job_run.rowcount,
                job_run.error,
                job_run.target_table,
                job_run.connection
            ))
    
    def get_job_runs(self, query_id: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """
        Recupera histórico de execuções
        
        Args:
            query_id: Filtro por query_id (opcional)
            limit: Limite de registros
            
        Returns:
            DataFrame com histórico
        """
        with duckdb.connect(self.db_path) as conn:
            if query_id:
                sql = """
                SELECT * FROM audit_job_runs 
                WHERE query_id = ? 
                ORDER BY started_at DESC 
                LIMIT ?
                """
                return conn.execute(sql, (query_id, limit)).df()
            else:
                sql = """
                SELECT * FROM audit_job_runs 
                ORDER BY started_at DESC 
                LIMIT ?
                """
                return conn.execute(sql, (limit,)).df()
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Obtém informações sobre uma tabela
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            DataFrame com informações da tabela
        """
        with duckdb.connect(self.db_path) as conn:
            try:
                # Verifica se tabela existe
                check_sql = """
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name = ?
                """
                result = conn.execute(check_sql, (table_name,)).fetchone()
                
                if result[0] == 0:
                    return pd.DataFrame({'error': ['Tabela não encontrada']})
                
                # Obtém informações da tabela
                info_sql = f"DESCRIBE {table_name}"
                return conn.execute(info_sql).df()
                
            except Exception as e:
                return pd.DataFrame({'error': [str(e)]})
    
    def get_table_row_count(self, table_name: str) -> int:
        """
        Obtém número de linhas de uma tabela
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Número de linhas
        """
        with duckdb.connect(self.db_path) as conn:
            try:
                result = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchone()
                return result[0] if result else 0
            except Exception:
                return 0
    
    def list_tables(self) -> list:
        """
        Lista todas as tabelas no DuckDB
        
        Returns:
            Lista de nomes de tabelas
        """
        with duckdb.connect(self.db_path) as conn:
            sql = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'main'
            ORDER BY table_name
            """
            result = conn.execute(sql).fetchall()
            return [row[0] for row in result]
    
    def drop_table(self, table_name: str) -> bool:
        """
        Remove uma tabela do DuckDB
        
        Args:
            table_name: Nome da tabela para remover
            
        Returns:
            True se tabela foi removida com sucesso
        """
        with duckdb.connect(self.db_path) as conn:
            try:
                # Verifica se tabela existe
                check_sql = """
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name = ?
                """
                result = conn.execute(check_sql, (table_name,)).fetchone()
                
                if result[0] == 0:
                    return False
                
                # Remove a tabela
                conn.execute(f"DROP TABLE {table_name}")
                return True
                
            except Exception:
                return False

    def test_connection(self) -> bool:
        """
        Testa conexão com DuckDB
        
        Returns:
            True se conexão OK
        """
        try:
            with duckdb.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
                return True
        except Exception:
            return False
