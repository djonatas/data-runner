# Data-Runner

🎯 **Executor de consultas/processos parametrizado por JSON**

Data-Runner é uma ferramenta Python avançada que permite executar consultas SQL em diferentes bancos de dados de forma parametrizada através de arquivos JSON de configuração. Com suporte a variáveis configuráveis, sistema de dependências entre jobs, conexões Oracle via TNS Names, leitura de arquivos CSV e muito mais. Os resultados são persistidos em um banco DuckDB local para análise posterior.

## ✨ Características

- **Configuração via JSON**: Defina conexões e jobs através de arquivos JSON simples
- **Múltiplos bancos suportados**: PostgreSQL, SQLite, MySQL, MSSQL, Oracle, CSV
- **Persistência DuckDB**: Todos os resultados salvos localmente para análise
- **Tipos de job**: Carga (dados) e Batimento (validação)
- **Auditoria completa**: Rastreamento de todas as execuções
- **CLI intuitiva**: Interface de linha de comando fácil de usar
- **SQL parametrizado**: Suporte a variáveis de ambiente no SQL
- **Sistema de Variáveis**: Variáveis configuráveis com tipos (string, number, boolean)
- **Sistema de Dependências**: Jobs com dependências e execução ordenada
- **Conexões CSV**: Leitura direta de arquivos CSV
- **Oracle TNS Names**: Suporte a conexões Oracle via TNS Names
- **Suporte a Schema**: Configuração de schema padrão por conexão
- **Validação de Ciclos**: Detecção automática de dependências circulares
- **Execução Paralela**: Jobs independentes executados em paralelo
- **Testável e idempotente**: Execuções seguras e repetíveis

## 🚀 Funcionalidades Principais

### 🔗 Sistema de Conexões

- **6 tipos de conexão**: PostgreSQL, SQLite, MySQL, MSSQL, Oracle, CSV
- **Oracle TNS Names**: Suporte completo a conexões Oracle via TNS Names
- **Schema configurável**: Defina schema padrão por conexão
- **Teste de conexão**: Validação automática de conexões

### 📊 Sistema de Variáveis

- **Tipos suportados**: String, Number, Boolean
- **Substituição automática**: Variáveis processadas em tempo de execução
- **Validação de tipos**: Verificação automática de tipos de dados
- **Sintaxe simples**: Use `${var:nome_da_variavel}` em suas queries

### 🔄 Sistema de Dependências

- **Dependências entre jobs**: Configure jobs que dependem de outros
- **Ordenação automática**: Execução na ordem correta baseada em dependências
- **Detecção de ciclos**: Validação automática de dependências circulares
- **Execução paralela**: Jobs independentes executados simultaneamente

### 📁 Conexões CSV

- **Leitura direta**: Carregue dados de arquivos CSV sem SQL
- **Configuração flexível**: Separador, encoding, header configuráveis
- **Integração completa**: Funciona com sistema de dependências e variáveis

### 🛡️ Segurança e Configuração

- **Arquivos de exemplo**: Templates seguros para configuração
- **Gitignore automático**: Proteção de dados sensíveis
- **Validação robusta**: Verificação de configurações antes da execução

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Instalação básica

```bash
# Clone o repositório
git clone <repository-url>
cd data-runner

# Instale as dependências
pip install -e .

# Ou instale com dependências opcionais
pip install -e ".[all]"

# Configure os arquivos de configuração
cp config/connections.json.example config/connections.json
cp config/jobs.json.example config/jobs.json

# Edite os arquivos com suas configurações reais
# config/connections.json - conexões de banco de dados
# config/jobs.json - jobs e queries
```

### Dependências opcionais

Para conectar com bancos específicos, instale as dependências correspondentes:

```bash
# Para MySQL
pip install -e ".[mysql]"

# Para MSSQL
pip install -e ".[mssql]"

# Para Oracle
pip install -e ".[oracle]"

# Para desenvolvimento (inclui testes)
pip install -e ".[dev]"
```

## ⚡ Quick Start

### 1. Configuração Básica

```bash
# Copie os arquivos de exemplo
cp config/connections.json.example config/connections.json
cp config/jobs.json.example config/jobs.json

# Edite com suas configurações reais
```

### 2. Configuração de Exemplos

Os exemplos de uso estão documentados na seção "Funcionalidades Avançadas" abaixo.

### 3. Execução de Jobs

```bash
# Executar job único
migradata run-job "load_people"

# Executar múltiplos jobs com dependências
migradata run-jobs "load_products_csv,transform_products,create_sales_fact"

# Executar todos os jobs
migradata run-all
```

## 📁 Estrutura do Projeto

```
migradata/
├── app/
│   ├── __init__.py
│   ├── cli.py                    # Interface de linha de comando
│   ├── connections.py            # Gerenciamento de conexões
│   ├── dependency_manager.py     # Gerenciamento de dependências
│   ├── repository.py             # Persistência DuckDB
│   ├── runner.py                # Orquestrador principal
│   ├── sql_utils.py             # Utilitários SQL
│   ├── types.py                 # Tipos e contratos
│   └── variable_processor.py    # Processamento de variáveis
├── config/
│   ├── connections.json.example  # Exemplo de conexões
│   ├── jobs.json.example        # Exemplo de jobs
│   └── README.md                # Documentação de configuração
├── data/
│   ├── products.csv             # Dados de exemplo
│   ├── customers.csv            # Dados de exemplo
│   ├── sales_data.csv           # Dados de exemplo
│   └── warehouse.duckdb         # Banco DuckDB (criado automaticamente)
├── tests/
│   ├── test_config_parsing.py
│   └── test_runner_sqlite.py
├── pyproject.toml
└── README.md
```

## ⚙️ Configuração

### Configuração Inicial

1. **Copie os arquivos de exemplo:**

```bash
cp config/connections.json.example config/connections.json
cp config/jobs.json.example config/jobs.json
```

2. **Edite as configurações:**

   - `config/connections.json` - Configure suas conexões de banco
   - `config/jobs.json` - Configure seus jobs e queries

3. **Segurança:**
   - Os arquivos reais são ignorados pelo Git
   - Use os arquivos `.example` como referência
   - Nunca commite senhas ou dados sensíveis

### 1. Configuração de Conexões (`config/connections.json`)

```json
{
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
        "password": "pass",
        "schema": "public"
      }
    },
    {
      "name": "mysql_analytics",
      "type": "mysql",
      "params": {
        "host": "localhost",
        "port": 3306,
        "database": "analytics",
        "user": "analytics_user",
        "password": "analytics_pass",
        "schema": "analytics"
      }
    },
    {
      "name": "mssql_warehouse",
      "type": "mssql",
      "params": {
        "host": "localhost",
        "port": 1433,
        "database": "warehouse",
        "user": "warehouse_user",
        "password": "warehouse_pass",
        "schema": "dbo"
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
```

#### Suporte a Schema

O Data-Runner agora suporta configuração de schema padrão para cada conexão:

- **PostgreSQL**: Use `"schema": "nome_do_schema"` para definir o search_path
- **MySQL**: Use `"schema": "nome_do_database"` para definir o database padrão
- **MSSQL**: Use `"schema": "nome_do_schema"` para definir o schema padrão
- **SQLite**: Não requer configuração de schema (usa o arquivo diretamente)

O schema configurado será aplicado automaticamente a todas as queries executadas na conexão.

### 2. Configuração de Jobs (`config/jobs.json`)

```json
{
  "variables": {
    "start_date": {
      "value": "2024-01-01",
      "type": "string",
      "description": "Data de início para filtros"
    },
    "min_amount": {
      "value": 100.0,
      "type": "number",
      "description": "Valor mínimo"
    },
    "active_only": {
      "value": true,
      "type": "boolean",
      "description": "Filtrar apenas ativos"
    }
  },
  "jobs": [
    {
      "queryId": "orders_full_load",
      "type": "carga",
      "connection": "pg_main",
      "sql": "SELECT * FROM public.orders WHERE order_date >= '${var:start_date}' AND amount >= ${var:min_amount};",
      "targetTable": "stg_orders"
    },
    {
      "queryId": "customers_mismatch",
      "type": "batimento",
      "connection": "sqlite_dev",
      "sql": "SELECT c.id, c.email FROM customers c LEFT JOIN crm_customers crm ON crm.id = c.id WHERE crm.id IS NULL AND ${var:active_only} = true;"
    }
  ]
}
```

#### Sistema de Variáveis

O Data-Runner suporta variáveis configuráveis que podem ser usadas em qualquer query:

**Tipos de Variáveis:**

- **`string`**: Texto (será automaticamente envolvido em aspas simples)
- **`number`**: Números (inteiros ou decimais)
- **`boolean`**: Valores booleanos (true/false)

**Sintaxe de Uso:**

- Use `${var:nome_variavel}` nas suas queries SQL
- As variáveis são substituídas automaticamente durante a execução

**Exemplos:**

```sql
-- Variável string
SELECT * FROM users WHERE name = '${var:user_name}';

-- Variável numérica
SELECT * FROM orders WHERE amount >= ${var:min_amount};

-- Variável booleana
SELECT * FROM products WHERE active = ${var:active_only};
```

### Tipos de Conexão Suportados

- **PostgreSQL**: `"type": "postgres"`
- **SQLite**: `"type": "sqlite"`
- **MySQL**: `"type": "mysql"`
- **MSSQL**: `"type": "mssql"`
- **Oracle**: `"type": "oracle"`
- **CSV**: `"type": "csv"`

#### Conexões Oracle

O Data-Runner suporta conexões Oracle usando cx_Oracle com dois métodos:

##### 1. Conexão Direta (Host/Porta)

```json
{
  "name": "oracle_erp",
  "type": "oracle",
  "params": {
    "host": "oracle-server.example.com",
    "port": 1521,
    "database": "XE",
    "user": "oracle_user",
    "password": "oracle_password",
    "schema": "HR"
  }
}
```

##### 2. Conexão via TNS Names

```json
{
  "name": "oracle_tns_erp",
  "type": "oracle",
  "params": {
    "database": "ERP_PROD",
    "user": "oracle_user",
    "password": "oracle_password",
    "schema": "HR"
  }
}
```

**Parâmetros Oracle:**

- `host`: Servidor Oracle (opcional para TNS Names)
- `port`: Porta do Oracle (opcional para TNS Names)
- `database`: Service Name, SID ou TNS Name do Oracle
- `user`: Usuário Oracle
- `password`: Senha Oracle
- `schema`: Schema padrão (opcional)

**Conexão via TNS Names:**

- Configure o arquivo `tnsnames.ora` no cliente Oracle
- Use apenas `database` com o nome do TNS
- O `host` e `port` são opcionais quando usando TNS Names

**Dependências:**

```bash
pip install cx_Oracle
```

#### Conexões CSV

O Data-Runner suporta leitura direta de arquivos CSV:

```json
{
  "name": "csv_products",
  "type": "csv",
  "params": {
    "csv_file": "./data/products.csv",
    "csv_separator": ",",
    "csv_encoding": "utf-8",
    "csv_has_header": true
  }
}
```

**Parâmetros CSV:**

- `csv_file`: Caminho para o arquivo CSV (obrigatório)
- `csv_separator`: Separador usado no CSV (padrão: `,`)
- `csv_encoding`: Encoding do arquivo (padrão: `utf-8`)
- `csv_has_header`: Se o arquivo tem cabeçalho (padrão: `true`)

**Jobs CSV:**
Para conexões CSV, o campo `sql` é opcional, pois o sistema lê o arquivo inteiro:

```json
{
  "queryId": "load_products_csv",
  "type": "carga",
  "connection": "csv_products",
  "targetTable": "stg_products"
}
```

#### Sistema de Dependências

O Data-Runner suporta dependências entre jobs para criar pipelines de dados:

```json
{
  "queryId": "transform_products",
  "type": "carga",
  "connection": "sqlite_dev",
  "sql": "SELECT * FROM stg_products WHERE active = 1;",
  "targetTable": "dim_products",
  "dependencies": ["load_products_csv"]
},
{
  "queryId": "create_sales_fact",
  "type": "carga",
  "connection": "sqlite_dev",
  "sql": "SELECT s.*, p.name FROM stg_sales s JOIN stg_products p ON s.product_id = p.id;",
  "targetTable": "fact_sales",
  "dependencies": ["load_sales_csv", "load_products_csv"]
}
```

**Funcionalidades:**

- **Ordenação Automática**: Jobs são executados na ordem correta das dependências
- **Validação de Ciclos**: Detecta dependências circulares
- **Execução Paralela**: Jobs sem dependências podem executar em paralelo
- **Resolução Inteligente**: Inclui automaticamente dependências necessárias

### Tipos de Job

- **Carga** (`"type": "carga"`): Carrega dados para tabela de staging
- **Batimento** (`"type": "batimento"`): Valida dados e salva divergências

## 🖥️ Uso

### Comandos Principais

```bash
# Listar jobs disponíveis
python -m app list

# Executar um job específico
python -m app run --id orders_full_load

# Executar múltiplos jobs
python -m app run --ids orders_full_load,customers_mismatch

# Executar com opções
python -m app run --id orders_full_load --limit 1000 --dry-run

# Ver histórico de execuções
python -m app history

# Inspecionar tabelas no DuckDB
python -m app inspect
```

### Opções de Execução

- `--duckdb <path>`: Caminho personalizado para o DuckDB
- `--dry-run`: Mostra o que faria sem executar
- `--limit <N>`: Limita o número de linhas retornadas
- `--save-as <table>`: Nome personalizado para a tabela alvo

### Exemplos de Uso

```bash
# Execução simples
python -m app run --id orders_full_load

# Execução com limite e dry-run
python -m app run --id customers_mismatch --limit 100 --dry-run

# Execução em lote
python -m app run --ids orders_full_load,customers_mismatch,products_daily_sync

# Ver histórico de um job específico
python -m app history --query-id orders_full_load

# Inspecionar tabela específica
python -m app inspect --table stg_orders
```

### Uso Programático com Schema

```python
from app.connections import create_connection_with_schema
from app.repository import ConfigRepository

# Carregar configurações
repo = ConfigRepository("./config")
connections_config = repo.load_connections()

# Criar conexão com schema específico
connection = next(c for c in connections_config.connections if c.name == "pg_main")
db_conn = create_connection_with_schema(connection)

# Executar query (schema será aplicado automaticamente)
result = db_conn.execute_query("SELECT * FROM my_table")

# Mudar schema dinamicamente
db_conn.set_schema("other_schema")
result = db_conn.execute_query("SELECT * FROM other_table")

# Verificar schema atual
current_schema = db_conn.get_schema()
print(f"Schema atual: {current_schema}")

# Fechar conexão
db_conn.close()
```

### Uso Programático com Variáveis

```python
from app.runner import JobRunner
from app.types import Variable, VariableType

# Inicializar runner
runner = JobRunner("./config")
runner.load_configs()

# Listar variáveis disponíveis
variables = runner.list_variables()
print("Variáveis:", variables)

# Validar variáveis
errors = runner.validate_variables()
if errors:
    print("Erros:", errors)

# Adicionar nova variável dinamicamente
new_var = Variable(
    name="dynamic_param",
    value="Valor Dinâmico",
    type=VariableType.STRING,
    description="Parâmetro adicionado em runtime"
)
runner.add_variable(new_var)

# Executar job (variáveis serão processadas automaticamente)
result = runner.run_job("my_job")
```

### Uso Programático com Dependências

```python
from app.runner import JobRunner

# Inicializar runner
runner = JobRunner("./config")
runner.load_configs()

# Validar dependências
errors = runner.validate_dependencies()
if errors:
    print("Erros:", errors)

# Detectar ciclos
cycles = runner.detect_cycles()
if cycles:
    print("Ciclos:", cycles)

# Obter ordem de execução
execution_order = runner.get_execution_order()
print("Ordem:", execution_order)

# Obter grupos de execução paralela
execution_groups = runner.get_execution_groups()
print("Grupos:", execution_groups)

# Executar jobs respeitando dependências
results = runner.run_jobs(["job1", "job2", "job3"])

# Analisar dependências específicas
deps = runner.get_job_dependencies("job2")
dependents = runner.get_dependent_jobs("job2")
print(f"Dependências de job2: {deps}")
print(f"Jobs que dependem de job2: {dependents}")
```

## 🗄️ Estrutura do DuckDB

### Tabela de Auditoria (`audit_job_runs`)

| Coluna         | Tipo    | Descrição                     |
| -------------- | ------- | ----------------------------- |
| `run_id`       | VARCHAR | ID único da execução (UUID)   |
| `query_id`     | VARCHAR | ID da query executada         |
| `type`         | VARCHAR | Tipo do job (carga/batimento) |
| `started_at`   | VARCHAR | Timestamp de início           |
| `finished_at`  | VARCHAR | Timestamp de fim              |
| `status`       | VARCHAR | Status (success/error)        |
| `rowcount`     | INTEGER | Número de linhas processadas  |
| `error`        | VARCHAR | Mensagem de erro (se houver)  |
| `target_table` | VARCHAR | Tabela alvo                   |
| `connection`   | VARCHAR | Conexão utilizada             |

### Convenções de Nomenclatura

- **Jobs de Carga**: `stg_<queryId>` (ex: `stg_orders`)
- **Jobs de Batimento**: `val_<queryId>` (ex: `val_customers_mismatch`)

## 🔧 SQL Parametrizado

### Variáveis de Ambiente

Use `${env:VAR_NAME}` no SQL para referenciar variáveis de ambiente:

```sql
SELECT '${env:USER}' as current_user,
       '${env:HOME}' as home_dir,
       datetime('now') as current_time;
```

### Aplicação de LIMIT

O parâmetro `--limit` é aplicado automaticamente ao SQL:

```bash
python -m app run --id orders_full_load --limit 1000
# Adiciona "LIMIT 1000" ao final da query
```

## 🧪 Testes

Execute os testes com pytest:

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app

# Executar testes específicos
pytest tests/test_config_parsing.py
pytest tests/test_runner_sqlite.py
```

## 📝 Boas Práticas

### Para Jobs de Carga

1. **Use filtros de data**: Sempre inclua filtros de data para evitar carregar dados desnecessários
2. **Defina target_table**: Especifique explicitamente o nome da tabela alvo
3. **Teste com --dry-run**: Use `--dry-run` antes de executar jobs grandes
4. **Use LIMIT para testes**: Use `--limit` para testar com poucos dados

```json
{
  "queryId": "orders_daily_load",
  "type": "carga",
  "connection": "pg_main",
  "sql": "SELECT * FROM orders WHERE order_date = CURRENT_DATE;",
  "targetTable": "stg_orders_daily"
}
```

### Para Jobs de Batimento

1. **Identifique divergências claramente**: Use LEFT JOIN para encontrar registros órfãos
2. **Inclua campos identificadores**: Sempre inclua IDs para facilitar correção
3. **Documente a regra**: Use comentários no SQL para explicar a validação

```json
{
  "queryId": "customers_orphan_validation",
  "type": "batimento",
  "connection": "sqlite_dev",
  "sql": "-- Validação: Clientes sem pedidos nos últimos 30 dias\nSELECT c.id, c.name, c.email, c.created_at\nFROM customers c\nLEFT JOIN orders o ON o.customer_id = c.id AND o.order_date >= date('now', '-30 days')\nWHERE o.id IS NULL;"
}
```

### Para Configuração de Conexões

1. **Use variáveis de ambiente**: Para senhas e dados sensíveis
2. **Teste conexões**: Use `python -m app list` para validar configurações
3. **Organize por ambiente**: Diferentes conexões para dev/prod

```json
{
  "name": "pg_prod",
  "type": "postgres",
  "params": {
    "host": "${env:PG_HOST}",
    "port": 5432,
    "database": "${env:PG_DATABASE}",
    "user": "${env:PG_USER}",
    "password": "${env:PG_PASSWORD}"
  }
}
```

## 🚀 Funcionalidades Avançadas

### 📊 Sistema de Variáveis Configuráveis

O Data-Runner permite definir variáveis personalizadas que podem ser usadas em qualquer query SQL:

```json
{
  "variables": {
    "start_date": {
      "value": "2024-01-01",
      "type": "string",
      "description": "Data de início para filtros"
    },
    "min_amount": {
      "value": 1000,
      "type": "number",
      "description": "Valor mínimo para vendas"
    },
    "active_only": {
      "value": true,
      "type": "boolean",
      "description": "Filtrar apenas registros ativos"
    }
  }
}
```

**Uso nas queries:**

```sql
SELECT * FROM sales
WHERE date >= ${var:start_date}
  AND amount >= ${var:min_amount}
  AND active = ${var:active_only};
```

### 🔄 Sistema de Dependências Entre Jobs

Configure jobs que dependem de outros para criar pipelines de dados:

```json
{
  "jobs": [
    {
      "queryId": "load_products_csv",
      "type": "carga",
      "connection": "csv_products",
      "targetTable": "staging_products"
    },
    {
      "queryId": "transform_products",
      "type": "carga",
      "connection": "warehouse",
      "sql": "SELECT * FROM staging_products WHERE price > 0",
      "targetTable": "dim_products",
      "dependencies": ["load_products_csv"]
    },
    {
      "queryId": "create_sales_fact",
      "type": "carga",
      "connection": "warehouse",
      "sql": "SELECT p.*, s.* FROM dim_products p JOIN sales s ON p.id = s.product_id",
      "targetTable": "fact_sales",
      "dependencies": ["load_products_csv", "load_customers_csv"]
    }
  ]
}
```

**Funcionalidades:**

- ✅ **Ordenação automática**: Jobs executados na ordem correta
- ✅ **Detecção de ciclos**: Validação de dependências circulares
- ✅ **Execução paralela**: Jobs independentes executados simultaneamente
- ✅ **Validação robusta**: Verificação de dependências inexistentes

### 📁 Conexões CSV Avançadas

Leia arquivos CSV diretamente sem necessidade de SQL:

```json
{
  "name": "csv_products",
  "type": "csv",
  "params": {
    "csv_file": "./data/products.csv",
    "csv_separator": ",",
    "csv_encoding": "utf-8",
    "csv_has_header": true
  }
}
```

**Jobs CSV:**

```json
{
  "queryId": "load_products_csv",
  "type": "carga",
  "connection": "csv_products",
  "targetTable": "staging_products"
}
```

### 🔗 Oracle TNS Names

Suporte completo a conexões Oracle via TNS Names:

```json
{
  "name": "oracle_erp",
  "type": "oracle",
  "params": {
    "database": "ERP_PROD",
    "user": "oracle_user",
    "password": "oracle_password",
    "schema": "HR"
  }
}
```

**Configuração TNS Names:**

```bash
# Arquivo tnsnames.ora
ERP_PROD =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = oracle-server.company.com)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = ERP_PROD)
    )
  )
```

### 🏗️ Suporte a Schema

Configure schema padrão para diferentes bancos:

```json
{
  "name": "postgres_analytics",
  "type": "postgres",
  "params": {
    "host": "localhost",
    "port": 5432,
    "database": "analytics",
    "user": "analytics_user",
    "password": "analytics_pass",
    "schema": "analytics"
  }
}
```

**Bancos suportados:**

- **PostgreSQL**: `search_path` configurado automaticamente
- **MySQL**: `USE schema` executado automaticamente
- **MSSQL**: `USE schema` executado automaticamente
- **Oracle**: `ALTER SESSION SET CURRENT_SCHEMA` executado automaticamente

## 🐛 Solução de Problemas

### Erro de Conexão

```bash
# Verificar se a conexão está configurada corretamente
python -m app list

# Testar conexão específica
python -c "from app.connections import ConnectionFactory; from app.types import Connection, ConnectionType, ConnectionParams; conn = Connection('test', ConnectionType.SQLITE, ConnectionParams(filepath='./test.db')); db_conn = ConnectionFactory.create_connection(conn); print(db_conn.test_connection())"
```

### Erro de SQL

```bash
# Executar com dry-run para ver o SQL processado
python -m app run --id problematic_job --dry-run

# Verificar logs detalhados
python -m app run --id problematic_job --verbose
```

### Problemas com DuckDB

```bash
# Verificar se o diretório data existe
ls -la data/

# Inspecionar tabelas criadas
python -m app inspect

# Verificar histórico de execuções
python -m app history
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/migradata/migradata/issues)
- **Discussões**: [GitHub Discussions](https://github.com/migradata/migradata/discussions)

---

## 🎯 Resumo das Funcionalidades

O **Data-Runner** é uma ferramenta completa para processamento de dados que oferece:

### 🔧 **Funcionalidades Core**

- ✅ **6 tipos de conexão**: PostgreSQL, SQLite, MySQL, MSSQL, Oracle, CSV
- ✅ **Sistema de variáveis**: Configuração flexível com tipos (string, number, boolean)
- ✅ **Sistema de dependências**: Jobs com dependências e execução ordenada
- ✅ **Suporte a Schema**: Configuração de schema padrão por conexão
- ✅ **Oracle TNS Names**: Conexões Oracle via TNS Names (padrão corporativo)
- ✅ **Conexões CSV**: Leitura direta de arquivos CSV sem SQL
- ✅ **Validação robusta**: Detecção de ciclos e dependências inválidas
- ✅ **Execução paralela**: Jobs independentes executados simultaneamente
- ✅ **Auditoria completa**: Rastreamento de todas as execuções
- ✅ **CLI intuitiva**: Interface de linha de comando fácil de usar

### 🚀 **Casos de Uso**

- **ETL/ELT**: Pipelines de dados com dependências
- **Data Warehousing**: Carregamento de dados de múltiplas fontes
- **Integração de Sistemas**: Conexão com sistemas legados
- **Análise de Dados**: Processamento e transformação de dados
- **Automação**: Jobs agendados e parametrizados

**MigraData** - A ferramenta definitiva para migração e processamento de dados! 🚀
