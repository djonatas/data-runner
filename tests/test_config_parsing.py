"""
Testes para parsing de configurações JSON
"""

import json
import tempfile
import os
import pytest
from app.runner import JobRunner
from app.types import JobType, ConnectionType


class TestConfigParsing:
    """Testes para parsing de configurações"""
    
    def test_parse_connections_config(self):
        """Testa parsing de configuração de conexões"""
        connections_data = {
            "defaultDuckDbPath": "./test.duckdb",
            "connections": [
                {
                    "name": "test_sqlite",
                    "type": "sqlite",
                    "params": {
                        "filepath": "./test.sqlite"
                    }
                },
                {
                    "name": "test_postgres",
                    "type": "postgres",
                    "params": {
                        "host": "localhost",
                        "port": 5432,
                        "database": "testdb",
                        "user": "testuser",
                        "password": "testpass"
                    }
                }
            ]
        }
        
        runner = JobRunner()
        config = runner._parse_connections_config(connections_data)
        
        assert config.default_duckdb_path == "./test.duckdb"
        assert len(config.connections) == 2
        
        # Verificar primeira conexão
        sqlite_conn = config.connections[0]
        assert sqlite_conn.name == "test_sqlite"
        assert sqlite_conn.type == ConnectionType.SQLITE
        assert sqlite_conn.params.filepath == "./test.sqlite"
        
        # Verificar segunda conexão
        pg_conn = config.connections[1]
        assert pg_conn.name == "test_postgres"
        assert pg_conn.type == ConnectionType.POSTGRES
        assert pg_conn.params.host == "localhost"
        assert pg_conn.params.port == 5432
        assert pg_conn.params.database == "testdb"
        assert pg_conn.params.user == "testuser"
        assert pg_conn.params.password == "testpass"
    
    def test_parse_jobs_config(self):
        """Testa parsing de configuração de jobs"""
        jobs_data = {
            "jobs": [
                {
                    "queryId": "test_carga",
                    "type": "carga",
                    "connection": "test_sqlite",
                    "sql": "SELECT * FROM test_table;",
                    "targetTable": "stg_test"
                },
                {
                    "queryId": "test_batimento",
                    "type": "batimento",
                    "connection": "test_postgres",
                    "sql": "SELECT * FROM validation_table WHERE id IS NULL;"
                }
            ]
        }
        
        runner = JobRunner()
        config = runner._parse_jobs_config(jobs_data)
        
        assert len(config.jobs) == 2
        
        # Verificar primeiro job
        carga_job = config.jobs[0]
        assert carga_job.query_id == "test_carga"
        assert carga_job.type == JobType.CARGA
        assert carga_job.connection == "test_sqlite"
        assert carga_job.sql == "SELECT * FROM test_table;"
        assert carga_job.target_table == "stg_test"
        
        # Verificar segundo job
        batimento_job = config.jobs[1]
        assert batimento_job.query_id == "test_batimento"
        assert batimento_job.type == JobType.BATIMENTO
        assert batimento_job.connection == "test_postgres"
        assert batimento_job.sql == "SELECT * FROM validation_table WHERE id IS NULL;"
        assert batimento_job.target_table is None
    
    def test_load_configs_from_files(self):
        """Testa carregamento de configurações de arquivos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar arquivos de configuração temporários
            connections_path = os.path.join(temp_dir, "connections.json")
            jobs_path = os.path.join(temp_dir, "jobs.json")
            
            connections_data = {
                "defaultDuckDbPath": "./test.duckdb",
                "connections": [
                    {
                        "name": "test_sqlite",
                        "type": "sqlite",
                        "params": {
                            "filepath": "./test.sqlite"
                        }
                    }
                ]
            }
            
            jobs_data = {
                "jobs": [
                    {
                        "queryId": "test_job",
                        "type": "carga",
                        "connection": "test_sqlite",
                        "sql": "SELECT 1 as test_column;"
                    }
                ]
            }
            
            with open(connections_path, 'w') as f:
                json.dump(connections_data, f)
            
            with open(jobs_path, 'w') as f:
                json.dump(jobs_data, f)
            
            # Testar carregamento
            runner = JobRunner(temp_dir)
            runner.load_configs()
            
            assert runner.connections_config is not None
            assert runner.jobs_config is not None
            assert runner.repository is not None
            
            # Verificar se consegue buscar job
            job = runner.get_job("test_job")
            assert job is not None
            assert job.query_id == "test_job"
            
            # Verificar se consegue buscar conexão
            conn = runner.get_connection("test_sqlite")
            assert conn is not None
            assert conn.name == "test_sqlite"
    
    def test_invalid_connection_type(self):
        """Testa erro com tipo de conexão inválido"""
        connections_data = {
            "defaultDuckDbPath": "./test.duckdb",
            "connections": [
                {
                    "name": "invalid_conn",
                    "type": "invalid_type",
                    "params": {}
                }
            ]
        }
        
        runner = JobRunner()
        
        with pytest.raises(ValueError, match="'invalid_type' is not a valid ConnectionType"):
            runner._parse_connections_config(connections_data)
    
    def test_invalid_job_type(self):
        """Testa erro com tipo de job inválido"""
        jobs_data = {
            "jobs": [
                {
                    "queryId": "invalid_job",
                    "type": "invalid_type",
                    "connection": "test_conn",
                    "sql": "SELECT 1;"
                }
            ]
        }
        
        runner = JobRunner()
        
        with pytest.raises(ValueError, match="'invalid_type' is not a valid JobType"):
            runner._parse_jobs_config(jobs_data)
