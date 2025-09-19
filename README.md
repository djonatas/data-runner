# Data-Runner

🎯 **Executor de consultas/processos parametrizado por JSON**

Data-Runner é uma ferramenta CLI robusta para **orquestração de pipelines de dados** que automatiza a execução de consultas SQL, transformações e carregamentos de dados entre diferentes fontes. 

**O que o Data-Runner faz:**
- 🔄 **Automatiza pipelines de dados** através de arquivos JSON de configuração
- 🗄️ **Conecta múltiplas fontes** (PostgreSQL, MySQL, SQL Server, Oracle, CSV, SQLite)
- 📊 **Executa consultas SQL** parametrizadas com variáveis dinâmicas
- 🏗️ **Constrói data warehouses** locais usando DuckDB como repositório central
- 🔗 **Gerencia dependências** entre jobs para execução ordenada e paralela
- 📈 **Monitora execuções** com auditoria completa e histórico detalhado
- 🎯 **Exporta resultados** para CSV com configurações personalizáveis
- ⚡ **Executa em lote** jobs individuais, por tipo ou grupos configurados

**Casos de uso típicos:**
- Migração de dados entre sistemas
- ETL/ELT automatizado para data warehouses
- Consolidação de dados de múltiplas fontes
- Relatórios automatizados com exportação
- Validação e batimento de dados
- Pipelines de dados para análise e BI

## 🚀 Quick Start

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/djonatas/data-runner.git
cd data-runner

# Instalação automática
./install.sh

# Ou instalação manual
python -m pip install -e .
```

### Configuração Inicial

```bash
# Setup automático
./setup.sh

# Ou configuração manual
cp config/connections.json.example config/connections.json
cp config/jobs.json.example config/jobs.json
```

### Uso Básico

```bash
# Listar jobs disponíveis
data-runner list-jobs

# Executar um job
data-runner run --id meu_job

# Executar múltiplos jobs
data-runner run-batch --ids job1,job2,job3

# Ver histórico
data-runner history

# Ajuda
data-runner --help
```

## 📋 Comandos CLI

### Listar Jobs

```bash
# Listar todos os jobs
data-runner list-jobs

# Listar grupos configurados
data-runner list-groups
```

### Executar Jobs

```bash
# Executar job único
data-runner run --id meu_job

# Executar job com limite
data-runner run --id meu_job --limit 1000

# Executar job em modo dry-run
data-runner run --id meu_job --dry-run

# Executar múltiplos jobs
data-runner run-batch --ids job1,job2,job3

# Executar jobs por tipo
data-runner run-group --type carga

# Executar grupo configurado
data-runner run-group-config --group meu_grupo
```

### Histórico e Inspeção

```bash
# Ver histórico de execuções
data-runner history

# Ver histórico de job específico
data-runner history --query-id meu_job

# Inspecionar banco DuckDB
data-runner inspect

# Inspecionar tabela específica
data-runner inspect --table minha_tabela
```

### Gerenciamento

```bash
# Remover tabela
data-runner drop-table --table tabela_antiga

# Remover tabela com confirmação
data-runner drop-table --table tabela_antiga --confirm
```

## ⚙️ Configuração

### Arquivo connections.json

```json
{
  "defaultDuckDbPath": "./data/warehouse.duckdb",
  "connections": [
    {
      "name": "meu_postgres",
      "type": "postgres",
      "params": {
        "host": "${env:POSTGRES_HOST}",
        "port": 5432,
        "database": "${env:POSTGRES_DATABASE}",
        "user": "${env:POSTGRES_USER}",
        "password": "${env:POSTGRES_PASSWORD}",
        "schema": "public"
      }
    }
  ]
}
```

### Arquivo jobs.json

```json
{
  "variables": {
    "tenant_id": {
      "value": "12345",
      "type": "string",
      "description": "ID do tenant"
    }
  },
  "jobs": [
    {
      "queryId": "meu_job",
      "type": "carga",
      "connection": "meu_postgres",
      "sql": "SELECT * FROM usuarios WHERE tenant_id = '${var:tenant_id}'",
      "targetTable": "usuarios_importados",
      "dependencies": ["job_anterior"]
    }
  ],
  "job_groups": {
    "cargas_diarias": {
      "description": "Cargas diárias de dados",
      "job_ids": ["job1", "job2", "job3"]
    }
  }
}
```

### Arquivo .env

```bash
# Variáveis de ambiente
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=meu_banco
POSTGRES_USER=meu_usuario
POSTGRES_PASSWORD=minha_senha
```

## 🔧 Tipos de Conexão

### PostgreSQL

```json
{
  "name": "postgres_db",
  "type": "postgres",
  "params": {
    "host": "localhost",
    "port": 5432,
    "database": "meu_banco",
    "user": "usuario",
    "password": "senha",
    "schema": "public"
  }
}
```

### MySQL

```json
{
  "name": "mysql_db",
  "type": "mysql",
  "params": {
    "host": "localhost",
    "port": 3306,
    "database": "meu_banco",
    "user": "usuario",
    "password": "senha",
    "schema": "meu_schema"
  }
}
```

### SQL Server

```json
{
  "name": "mssql_db",
  "type": "mssql",
  "params": {
    "host": "localhost",
    "port": 1433,
    "database": "meu_banco",
    "user": "usuario",
    "password": "senha",
    "schema": "dbo"
  }
}
```

### Oracle

```json
{
  "name": "oracle_db",
  "type": "oracle",
  "params": {
    "host": "localhost",
    "port": 1521,
    "database": "XE",
    "user": "usuario",
    "password": "senha",
    "schema": "HR"
  }
}
```

### Oracle TNS Names

```json
{
  "name": "oracle_tns",
  "type": "oracle",
  "params": {
    "database": "ERP_PROD",
    "user": "usuario",
    "password": "senha",
    "schema": "HR"
  }
}
```

### CSV

```json
{
  "name": "csv_data",
  "type": "csv",
  "params": {
    "csv_file": "./data/arquivo.csv",
    "csv_separator": ",",
    "csv_encoding": "utf-8",
    "csv_has_header": true
  }
}
```

## 📊 Tipos de Job

### Carga (carga)

```json
{
  "queryId": "importar_usuarios",
  "type": "carga",
  "connection": "postgres_db",
  "sql": "SELECT * FROM usuarios WHERE ativo = true",
  "targetTable": "usuarios_ativos"
}
```

### Batimento (batimento)

```json
{
  "queryId": "validar_dados",
  "type": "batimento",
  "connection": "postgres_db",
  "sql": "SELECT COUNT(*) as total FROM usuarios_ativos",
  "targetTable": "contagem_usuarios"
}
```

### Export CSV (export-csv)

```json
{
  "queryId": "exportar_relatorio",
  "type": "export-csv",
  "connection": "postgres_db",
  "sql": "SELECT * FROM usuarios_ativos ORDER BY nome",
  "csv_file": "relatorio_usuarios.csv",
  "csv_separator": ",",
  "csv_encoding": "utf-8",
  "csv_include_header": true
}
```

## 🔄 Sistema de Dependências

```json
{
  "jobs": [
    {
      "queryId": "carregar_dados",
      "type": "carga",
      "connection": "postgres_db",
      "sql": "SELECT * FROM dados",
      "targetTable": "dados_carregados"
    },
    {
      "queryId": "processar_dados",
      "type": "carga",
      "connection": "postgres_db",
      "sql": "SELECT * FROM dados_carregados WHERE status = 'ativo'",
      "targetTable": "dados_processados",
      "dependencies": ["carregar_dados"]
    }
  ]
}
```

## 📁 Grupos de Jobs

```json
{
  "job_groups": {
    "pipeline_completo": {
      "description": "Pipeline completo de dados",
      "job_ids": ["carregar_dados", "processar_dados", "exportar_relatorio"]
    },
    "cargas_diarias": {
      "description": "Cargas diárias",
      "job_ids": ["carregar_dados", "processar_dados"]
    }
  }
}
```

## 🔐 Variáveis de Ambiente

### Uso em Conexões

```json
{
  "params": {
    "host": "${env:POSTGRES_HOST}",
    "password": "${env:POSTGRES_PASSWORD}"
  }
}
```

### Uso em Jobs

```json
{
  "variables": {
    "tenant_id": {
      "value": "${env:TENANT_ID}",
      "type": "string"
    }
  }
}
```

## 🛠️ Scripts de Ajuda

### install.sh

```bash
# Instalação completa
./install.sh
```

### setup.sh

```bash
# Setup e configuração
./setup.sh
```

### run.sh

```bash
# Execução interativa
./run.sh

# Execução direta
./run.sh run meu_job
./run.sh batch job1,job2
./run.sh group carga
./run.sh group-config meu_grupo
```

### test.sh

```bash
# Testes e validação
./test.sh
```

## 📚 Exemplos de Uso

### Execução Básica

```bash
# Listar jobs
data-runner list-jobs

# Executar job
data-runner run --id importar_usuarios

# Ver resultado
data-runner inspect --table usuarios_importados
```

### Execução com Limites

```bash
# Executar com limite de linhas
data-runner run --id importar_usuarios --limit 1000

# Executar em modo dry-run
data-runner run --id importar_usuarios --dry-run
```

### Execução em Lote

```bash
# Executar múltiplos jobs
data-runner run-batch --ids importar_usuarios,processar_dados,exportar_relatorio

# Executar por tipo
data-runner run-group --type carga

# Executar grupo configurado
data-runner run-group-config --group pipeline_completo
```

### Monitoramento

```bash
# Ver histórico
data-runner history

# Ver histórico de job específico
data-runner history --query-id importar_usuarios

# Ver detalhes de tabela
data-runner inspect --table usuarios_importados
```

## 🔍 Troubleshooting

### Erro de Conexão

```bash
# Verificar configurações
data-runner list-jobs

# Testar conexão
./test.sh config
```

### Erro de SQL

```bash
# Executar em modo dry-run
data-runner run --id problema_job --dry-run

# Verificar logs
python -m app run --id problema_job --verbose
```

### Problemas com DuckDB

```bash
# Inspecionar banco
data-runner inspect

# Ver tabelas
data-runner inspect --table audit_job_runs
```

---

## 👨‍💻 Para Desenvolvedores

### Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **DuckDB**: Banco de dados local para persistência
- **pandas**: Manipulação de dados
- **Click**: Interface CLI
- **psycopg2**: Conexão PostgreSQL
- **PyMySQL**: Conexão MySQL
- **pyodbc**: Conexão SQL Server
- **cx_Oracle**: Conexão Oracle
- **python-dotenv**: Carregamento de variáveis de ambiente

### Estrutura do Projeto

```
data-runner/
├── app/
│   ├── cli.py              # Interface CLI
│   ├── runner.py           # Orquestrador principal
│   ├── connections.py      # Gerenciamento de conexões
│   ├── repository.py       # Persistência DuckDB
│   ├── types.py           # Tipos e contratos
│   ├── env_processor.py   # Processamento de variáveis de ambiente
│   ├── variable_processor.py # Processamento de variáveis
│   ├── dependency_manager.py # Gerenciamento de dependências
│   └── sql_utils.py       # Utilitários SQL
├── config/
│   ├── connections.json.example
│   └── jobs.json.example
├── data/
│   └── warehouse.duckdb
├── tests/
└── scripts/
    ├── install.sh
    ├── setup.sh
    ├── run.sh
    └── test.sh
```

### Fluxo Principal

1. **CLI** (`cli.py`) recebe comandos do usuário
2. **Runner** (`runner.py`) orquestra a execução
3. **ConnectionFactory** (`connections.py`) cria conexões com bancos
4. **Repository** (`repository.py`) persiste resultados no DuckDB
5. **Processadores** lidam com variáveis e dependências

### Classes Principais

- **`JobRunner`**: Orquestrador principal, gerencia execução de jobs
- **`ConnectionFactory`**: Factory para criar conexões com diferentes bancos
- **`DuckDBRepository`**: Gerencia persistência e auditoria no DuckDB
- **`EnvironmentVariableProcessor`**: Processa variáveis de ambiente
- **`VariableProcessor`**: Processa variáveis definidas em jobs.json
- **`DependencyManager`**: Gerencia dependências e ordenação de jobs

### Setup Local

```bash
# Clone e setup
git clone https://github.com/djonatas/data-runner.git
cd data-runner

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Dependências
pip install -e .

# Dependências opcionais
pip install -e ".[mysql,mssql,oracle]"

# Configuração
cp config/connections.json.example config/connections.json
cp config/jobs.json.example config/jobs.json

# Teste
python -m app.cli --help
```

### Desenvolvimento

```bash
# Executar testes
python -m pytest tests/

# Executar CLI
python -m app.cli list-jobs

# Debug
python -m app.cli run --id teste --verbose
```

---

## 📄 Licença

MIT License - veja arquivo LICENSE para detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/djonatas/data-runner/issues)
