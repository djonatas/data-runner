"""
Repositório para persistência no DuckDB
"""

import os
from datetime import datetime
from typing import Optional
import pandas as pd
import duckdb
from .types import JobRun, JobStatus, JobType, ValidationRecord


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
            connection VARCHAR,
            csv_file VARCHAR,
            validation_file VARCHAR,
            validation_result VARCHAR
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
    
    def export_dataframe_to_csv(self, df: pd.DataFrame, csv_file: str, 
                               separator: str = ",", encoding: str = "utf-8", 
                               include_header: bool = True) -> str:
        """
        Exporta DataFrame para arquivo CSV
        
        Args:
            df: DataFrame para exportar
            csv_file: Nome do arquivo CSV
            separator: Separador do CSV (padrão: ',')
            encoding: Encoding do arquivo (padrão: 'utf-8')
            include_header: Se inclui cabeçalho (padrão: True)
            
        Returns:
            Caminho completo do arquivo CSV criado
        """
        import os
        
        # Garante que o diretório data existe
        data_dir = os.path.dirname(self.db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        
        # Caminho completo do arquivo CSV
        csv_path = os.path.join(data_dir, csv_file)
        
        # Exporta para CSV
        df.to_csv(
            csv_path,
            sep=separator,
            encoding=encoding,
            index=False,
            header=include_header
        )
        
        return csv_path
    
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
             rowcount, error, target_table, connection, csv_file, 
             validation_file, validation_result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                job_run.connection,
                job_run.csv_file,
                job_run.validation_file,
                job_run.validation_result
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
        # Bloqueio para tabelas críticas do sistema
        protected_tables = {
            'audit_job_runs',
            'audit_jobs_runs',  # variação do nome
            'audit_job_run',
            'audit_jobs_run'    # variação do nome
        }
        
        if table_name.lower() in protected_tables:
            raise ValueError(f"Não é possível remover a tabela '{table_name}' - é uma tabela protegida do sistema")
        
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
    
    def create_validation_output_table(self, table_name: str):
        """
        Cria tabela de output para resultados de validação
        
        Args:
            table_name: Nome da tabela de output
        """
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            execution_count INTEGER NOT NULL,
            pkey VARCHAR NOT NULL,
            result VARCHAR NOT NULL,
            message TEXT,
            details TEXT,
            input_data TEXT,
            executed_at VARCHAR NOT NULL,
            PRIMARY KEY (execution_count, pkey)
        )
        """
        
        with duckdb.connect(self.db_path) as conn:
            conn.execute(create_table_sql)
    
    def get_next_execution_count(self, table_name: str) -> int:
        """
        Obtém o próximo número de execução para uma tabela de validação
        
        Args:
            table_name: Nome da tabela de output
            
        Returns:
            Próximo número de execução
        """
        with duckdb.connect(self.db_path) as conn:
            try:
                # Verificar se a tabela existe
                result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
                if result and result[0] > 0:
                    # Obter o maior execution_count
                    max_result = conn.execute(f"SELECT MAX(execution_count) FROM {table_name}").fetchone()
                    if max_result and max_result[0] is not None:
                        return int(max_result[0]) + 1
                return 1
            except Exception:
                # Se a tabela não existe ou há erro, retornar 1
                return 1
    
    def save_validation_record(self, table_name: str, validation_record: ValidationRecord):
        """
        Salva um registro de validação na tabela de output
        
        Args:
            table_name: Nome da tabela de output
            validation_record: Registro de validação para salvar
        """
        # Criar tabela se não existir
        self.create_validation_output_table(table_name)
        
        insert_sql = f"""
        INSERT OR REPLACE INTO {table_name} 
        (execution_count, pkey, result, message, details, input_data, executed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        with duckdb.connect(self.db_path) as conn:
            conn.execute(insert_sql, (
                validation_record.execution_count,
                validation_record.pkey,
                validation_record.result,
                validation_record.message,
                validation_record.details,
                validation_record.input_data,
                validation_record.executed_at
            ))
    
    def save_validation_records_batch(self, table_name: str, validation_records: list):
        """
        Salva múltiplos registros de validação em lote
        
        Args:
            table_name: Nome da tabela de output
            validation_records: Lista de ValidationRecord
        """
        if not validation_records:
            return
        
        # Criar tabela se não existir
        self.create_validation_output_table(table_name)
        
        insert_sql = f"""
        INSERT OR REPLACE INTO {table_name} 
        (execution_count, pkey, result, message, details, input_data, executed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        # Preparar dados para inserção em lote
        data_to_insert = []
        for record in validation_records:
            data_to_insert.append((
                record.execution_count,
                record.pkey,
                record.result,
                record.message,
                record.details,
                record.input_data,
                record.executed_at
            ))
        
        with duckdb.connect(self.db_path) as conn:
            conn.executemany(insert_sql, data_to_insert)
    
    def get_validation_results(self, table_name: str, execution_count: Optional[int] = None, 
                              pkey: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """
        Recupera resultados de validação da tabela de output
        
        Args:
            table_name: Nome da tabela de output
            execution_count: Filtrar por número de execução específico
            pkey: Filtrar por chave primária específica
            limit: Limite de registros
            
        Returns:
            DataFrame com os resultados
        """
        where_conditions = []
        params = []
        
        if execution_count is not None:
            where_conditions.append("execution_count = ?")
            params.append(execution_count)
        
        if pkey is not None:
            where_conditions.append("pkey = ?")
            params.append(pkey)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        query = f"""
        SELECT execution_count, pkey, result, message, details, input_data, executed_at
        FROM {table_name}
        {where_clause}
        ORDER BY execution_count DESC, executed_at DESC
        LIMIT ?
        """
        params.append(limit)
        
        with duckdb.connect(self.db_path) as conn:
            return conn.execute(query, params).df()
    
    def get_validation_summary(self, table_name: str, execution_count: Optional[int] = None) -> dict:
        """
        Obtém resumo dos resultados de validação
        
        Args:
            table_name: Nome da tabela de output
            execution_count: Filtrar por número de execução específico
            
        Returns:
            Dicionário com estatísticas de validação
        """
        where_clause = ""
        params = []
        
        if execution_count is not None:
            where_clause = "WHERE execution_count = ?"
            params.append(execution_count)
        
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN result = 'success' THEN 1 END) as successful_records,
            COUNT(CASE WHEN result = 'error' THEN 1 END) as failed_records,
            MAX(execution_count) as latest_execution_count
        FROM {table_name}
        {where_clause}
        """
        
        with duckdb.connect(self.db_path) as conn:
            result = conn.execute(query, params).fetchone()
            
            if result:
                total = result[0] or 0
                successful = result[1] or 0
                failed = result[2] or 0
                latest_execution = result[3] or 0
                
                return {
                    "total_records": total,
                    "successful_records": successful,
                    "failed_records": failed,
                    "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
                    "latest_execution_count": latest_execution
                }
            
            return {
                "total_records": 0,
                "successful_records": 0,
                "failed_records": 0,
                "success_rate": 0,
                "latest_execution_count": 0
            }
