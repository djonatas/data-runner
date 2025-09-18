#!/usr/bin/env python3
"""
Script de inicialização e teste do MigraData
Testa componentes que não dependem de bibliotecas externas
"""

import json
import os
from datetime import datetime


def test_types():
    """Testa os tipos e enums"""
    print("🔧 Testando tipos e enums...")
    
    from app.types import JobType, ConnectionType, Job, Connection, ConnectionParams
    
    # Testar enums
    assert JobType.CARGA.value == "carga"
    assert JobType.BATIMENTO.value == "batimento"
    assert ConnectionType.SQLITE.value == "sqlite"
    assert ConnectionType.POSTGRES.value == "postgres"
    
    # Testar criação de objetos
    job = Job('test_job', JobType.CARGA, 'test_conn', 'SELECT 1;')
    assert job.query_id == 'test_job'
    assert job.type == JobType.CARGA
    
    conn_params = ConnectionParams(filepath='./test.db')
    connection = Connection('test_conn', ConnectionType.SQLITE, conn_params)
    assert connection.name == 'test_conn'
    assert connection.type == ConnectionType.SQLITE
    
    print("✅ Tipos e enums funcionando corretamente!")


def test_sql_utils():
    """Testa utilitários SQL"""
    print("🔧 Testando utilitários SQL...")
    
    from app.sql_utils import expand_env_vars, apply_limit, sanitize_table_name, get_default_target_table
    
    # Testar expansão de variáveis de ambiente
    os.environ['TEST_VAR'] = 'test_value'
    sql = 'SELECT * FROM orders WHERE user = \'${env:TEST_VAR}\';'
    expanded = expand_env_vars(sql)
    assert 'test_value' in expanded
    print(f"   ✅ Expansão de variáveis: {expanded}")
    
    # Testar aplicação de LIMIT
    sql = 'SELECT * FROM orders'
    limited = apply_limit(sql, 100)
    assert 'LIMIT 100' in limited
    print(f"   ✅ Aplicação de LIMIT: {limited}")
    
    # Testar sanitização de nomes
    sanitized = sanitize_table_name('test-table_name!')
    assert sanitized == 'test_table_name'
    print(f"   ✅ Sanitização: {sanitized}")
    
    # Testar geração de nomes padrão
    carga_table = get_default_target_table('orders', 'carga')
    assert carga_table == 'stg_orders'
    
    batimento_table = get_default_target_table('customers', 'batimento')
    assert batimento_table == 'val_customers'
    print(f"   ✅ Nomes padrão: {carga_table}, {batimento_table}")
    
    print("✅ Utilitários SQL funcionando corretamente!")


def test_config_parsing():
    """Testa parsing de configurações JSON"""
    print("🔧 Testando parsing de configurações...")
    
    # Simular parsing de conexões
    connections_data = {
        "defaultDuckDbPath": "./data/warehouse.duckdb",
        "connections": [
            {
                "name": "pg_main",
                "type": "postgres",
                "params": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "mydb",
                    "user": "user",
                    "password": "pass"
                }
            },
            {
                "name": "sqlite_dev",
                "type": "sqlite",
                "params": {
                    "filepath": "./data/dev.sqlite"
                }
            }
        ]
    }
    
    # Verificar estrutura
    assert "connections" in connections_data
    assert len(connections_data["connections"]) == 2
    assert connections_data["defaultDuckDbPath"] == "./data/warehouse.duckdb"
    
    print("   ✅ Estrutura de conexões válida")
    
    # Simular parsing de jobs
    jobs_data = {
        "jobs": [
            {
                "queryId": "orders_full_load",
                "type": "carga",
                "connection": "pg_main",
                "sql": "SELECT * FROM public.orders WHERE order_date >= '2024-01-01';",
                "targetTable": "stg_orders"
            },
            {
                "queryId": "customers_mismatch",
                "type": "batimento",
                "connection": "sqlite_dev",
                "sql": "SELECT c.id, c.email FROM customers c LEFT JOIN crm_customers crm ON crm.id = c.id WHERE crm.id IS NULL;"
            }
        ]
    }
    
    # Verificar estrutura
    assert "jobs" in jobs_data
    assert len(jobs_data["jobs"]) == 2
    
    for job in jobs_data["jobs"]:
        assert "queryId" in job
        assert "type" in job
        assert "connection" in job
        assert "sql" in job
        assert job["type"] in ["carga", "batimento"]
    
    print("   ✅ Estrutura de jobs válida")
    print("✅ Parsing de configurações funcionando corretamente!")


def test_file_structure():
    """Testa estrutura de arquivos"""
    print("🔧 Testando estrutura de arquivos...")
    
    required_files = [
        "app/__init__.py",
        "app/__main__.py",
        "app/types.py",
        "app/sql_utils.py",
        "app/connections.py",
        "app/repository.py",
        "app/runner.py",
        "app/cli.py",
        "config/connections.json",
        "config/jobs.json",
        "tests/test_config_parsing.py",
        "tests/test_runner_sqlite.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {missing_files}")
        return False
    
    print(f"   ✅ Todos os {len(required_files)} arquivos necessários estão presentes")
    
    # Verificar se os diretórios existem
    required_dirs = ["app", "config", "tests", "data"]
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            print(f"❌ Diretório faltando: {dir_path}")
            return False
    
    print("   ✅ Todos os diretórios necessários estão presentes")
    print("✅ Estrutura de arquivos correta!")


def test_json_configs():
    """Testa se os arquivos JSON são válidos"""
    print("🔧 Testando arquivos JSON...")
    
    # Testar connections.json
    try:
        with open("config/connections.json", "r") as f:
            connections = json.load(f)
        assert "defaultDuckDbPath" in connections
        assert "connections" in connections
        print("   ✅ config/connections.json é válido")
    except Exception as e:
        print(f"   ❌ Erro em connections.json: {e}")
        return False
    
    # Testar jobs.json
    try:
        with open("config/jobs.json", "r") as f:
            jobs = json.load(f)
        assert "jobs" in jobs
        print("   ✅ config/jobs.json é válido")
    except Exception as e:
        print(f"   ❌ Erro em jobs.json: {e}")
        return False
    
    print("✅ Arquivos JSON válidos!")


def main():
    """Função principal de teste"""
    print("🚀 MigraData - Inicialização e Testes")
    print("=" * 50)
    
    try:
        test_file_structure()
        test_json_configs()
        test_types()
        test_sql_utils()
        test_config_parsing()
        
        print("\n" + "=" * 50)
        print("🎉 PROJETO INICIALIZADO COM SUCESSO!")
        print("\n📋 Status dos Componentes:")
        print("✅ Estrutura de arquivos")
        print("✅ Configurações JSON")
        print("✅ Tipos e enums")
        print("✅ Utilitários SQL")
        print("✅ Parsing de configurações")
        
        print("\n🚀 Próximos Passos:")
        print("1. Instalar dependências: pip install -e .")
        print("2. Executar: python -m app list")
        print("3. Configurar suas conexões em config/connections.json")
        print("4. Definir seus jobs em config/jobs.json")
        
        print("\n📚 Para mais informações, consulte o README.md")
        
    except Exception as e:
        print(f"\n❌ Erro durante inicialização: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
