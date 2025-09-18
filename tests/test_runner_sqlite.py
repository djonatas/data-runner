"""
Testes para execução de jobs usando SQLite
"""

import tempfile
import os
import sqlite3
import pandas as pd
import pytest
from app.runner import JobRunner
from app.types import ExecutionOptions, JobType, JobStatus


class TestRunnerSQLite:
    """Testes para execução de jobs com SQLite"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test.sqlite")
        self.duckdb_path = os.path.join(self.temp_dir, "test.duckdb")
        
        # Criar banco SQLite de teste
        self._create_test_sqlite_db()
        
        # Criar configurações de teste
        self._create_test_configs()
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_sqlite_db(self):
        """Cria banco SQLite de teste com dados"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Criar tabela de teste
        cursor.execute("""
            CREATE TABLE test_orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                amount REAL,
                order_date TEXT
            )
        """)
        
        # Inserir dados de teste
        test_data = [
            (1, 101, 100.50, '2024-01-01'),
            (2, 102, 200.75, '2024-01-02'),
            (3, 103, 150.25, '2024-01-03'),
            (4, 104, 300.00, '2024-01-04'),
        ]
        
        cursor.executemany(
            "INSERT INTO test_orders (id, customer_id, amount, order_date) VALUES (?, ?, ?, ?)",
            test_data
        )
        
        # Criar tabela para batimento
        cursor.execute("""
            CREATE TABLE test_customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        
        cursor.executemany(
            "INSERT INTO test_customers (id, name, email) VALUES (?, ?, ?)",
            [
                (101, 'João Silva', 'joao@email.com'),
                (102, 'Maria Santos', 'maria@email.com'),
                (103, 'Pedro Costa', 'pedro@email.com'),
                # ID 104 não existe para testar batimento
            ]
        )
        
        conn.commit()
        conn.close()
    
    def _create_test_configs(self):
        """Cria arquivos de configuração de teste"""
        # Configuração de conexões
        connections_config = {
            "defaultDuckDbPath": self.duckdb_path,
            "connections": [
                {
                    "name": "test_sqlite",
                    "type": "sqlite",
                    "params": {
                        "filepath": self.test_db_path
                    }
                }
            ]
        }
        
        connections_path = os.path.join(self.temp_dir, "connections.json")
        with open(connections_path, 'w') as f:
            import json
            json.dump(connections_config, f)
        
        # Configuração de jobs
        jobs_config = {
            "jobs": [
                {
                    "queryId": "test_carga_orders",
                    "type": "carga",
                    "connection": "test_sqlite",
                    "sql": "SELECT * FROM test_orders WHERE amount > 150;",
                    "targetTable": "stg_orders"
                },
                {
                    "queryId": "test_batimento_customers",
                    "type": "batimento",
                    "connection": "test_sqlite",
                    "sql": "SELECT c.id, c.name FROM test_customers c LEFT JOIN test_orders o ON o.customer_id = c.id WHERE o.customer_id IS NULL;"
                }
            ]
        }
        
        jobs_path = os.path.join(self.temp_dir, "jobs.json")
        with open(jobs_path, 'w') as f:
            import json
            json.dump(jobs_config, f)
    
    def test_run_carga_job(self):
        """Testa execução de job de carga"""
        runner = JobRunner(self.temp_dir)
        runner.load_configs()
        
        # Executar job de carga
        result = runner.run_job("test_carga_orders")
        
        # Verificar resultado
        assert result.status == JobStatus.SUCCESS
        assert result.rowcount == 2  # Apenas orders com amount > 150
        assert result.target_table == "stg_orders"
        assert result.error is None
        
        # Verificar se dados foram salvos no DuckDB
        assert runner.repository is not None
        tables = runner.repository.list_tables()
        assert "stg_orders" in tables
        
        # Verificar conteúdo da tabela
        row_count = runner.repository.get_table_row_count("stg_orders")
        assert row_count == 2
        
        # Verificar auditoria
        history = runner.repository.get_job_runs("test_carga_orders", 1)
        assert len(history) == 1
        assert history.iloc[0]['status'] == 'success'
        assert history.iloc[0]['rowcount'] == 2
    
    def test_run_batimento_job(self):
        """Testa execução de job de batimento"""
        runner = JobRunner(self.temp_dir)
        runner.load_configs()
        
        # Executar job de batimento
        result = runner.run_job("test_batimento_customers")
        
        # Verificar resultado
        assert result.status == JobStatus.SUCCESS
        assert result.rowcount == 1  # Apenas customer 104 não tem orders
        assert result.target_table == "val_test_batimento_customers"
        assert result.error is None
        
        # Verificar se dados foram salvos no DuckDB
        assert runner.repository is not None
        tables = runner.repository.list_tables()
        assert "val_test_batimento_customers" in tables
        
        # Verificar auditoria
        history = runner.repository.get_job_runs("test_batimento_customers", 1)
        assert len(history) == 1
        assert history.iloc[0]['status'] == 'success'
        assert history.iloc[0]['rowcount'] == 1
    
    def test_run_job_with_options(self):
        """Testa execução de job com opções"""
        runner = JobRunner(self.temp_dir)
        runner.load_configs()
        
        # Executar com limite
        options = ExecutionOptions(limit=1)
        result = runner.run_job("test_carga_orders", options)
        
        assert result.status == JobStatus.SUCCESS
        assert result.rowcount == 1  # Limitado a 1 linha
        
        # Executar dry run
        options = ExecutionOptions(dry_run=True)
        result = runner.run_job("test_carga_orders", options)
        
        assert result.status == JobStatus.SUCCESS
        assert result.rowcount == 0  # Dry run não executa
        assert result.error is None
    
    def test_run_nonexistent_job(self):
        """Testa execução de job inexistente"""
        runner = JobRunner(self.temp_dir)
        runner.load_configs()
        
        with pytest.raises(ValueError, match="Job não encontrado: nonexistent"):
            runner.run_job("nonexistent")
    
    def test_run_job_with_invalid_connection(self):
        """Testa execução com conexão inválida"""
        # Criar job com conexão inexistente
        jobs_config = {
            "jobs": [
                {
                    "queryId": "test_invalid_conn",
                    "type": "carga",
                    "connection": "nonexistent_connection",
                    "sql": "SELECT 1;"
                }
            ]
        }
        
        jobs_path = os.path.join(self.temp_dir, "jobs.json")
        with open(jobs_path, 'w') as f:
            import json
            json.dump(jobs_config, f)
        
        runner = JobRunner(self.temp_dir)
        runner.load_configs()
        
        with pytest.raises(ValueError, match="Conexão não encontrada: nonexistent_connection"):
            runner.run_job("test_invalid_conn")
    
    def test_run_multiple_jobs(self):
        """Testa execução de múltiplos jobs"""
        runner = JobRunner(self.temp_dir)
        runner.load_configs()
        
        # Executar múltiplos jobs
        results = runner.run_jobs(["test_carga_orders", "test_batimento_customers"])
        
        assert len(results) == 2
        
        # Verificar primeiro job
        assert results[0].query_id == "test_carga_orders"
        assert results[0].status == JobStatus.SUCCESS
        
        # Verificar segundo job
        assert results[1].query_id == "test_batimento_customers"
        assert results[1].status == JobStatus.SUCCESS
    
    def test_sql_with_env_vars(self):
        """Testa SQL com variáveis de ambiente"""
        import os
        
        # Definir variável de ambiente
        os.environ['TEST_VAR'] = 'test_value'
        
        # Criar job com variável de ambiente
        jobs_config = {
            "jobs": [
                {
                    "queryId": "test_env_var",
                    "type": "carga",
                    "connection": "test_sqlite",
                    "sql": "SELECT '${env:TEST_VAR}' as env_value, 1 as test_col;",
                    "targetTable": "stg_env_test"
                }
            ]
        }
        
        jobs_path = os.path.join(self.temp_dir, "jobs.json")
        with open(jobs_path, 'w') as f:
            import json
            json.dump(jobs_config, f)
        
        runner = JobRunner(self.temp_dir)
        runner.load_configs()
        
        # Executar job
        result = runner.run_job("test_env_var")
        
        assert result.status == JobStatus.SUCCESS
        assert result.rowcount == 1
        
        # Limpar variável de ambiente
        del os.environ['TEST_VAR']
