# Configuração do Data-Runner

Este diretório contém os arquivos de configuração do Data-Runner. Para proteger informações sensíveis, os arquivos de configuração reais não são versionados no Git.

## 📁 Arquivos de Configuração

### Arquivos de Exemplo

- `connections.json.example` - Exemplo de configuração de conexões
- `jobs.json.example` - Exemplo de configuração de jobs

### Arquivos Reais (não versionados)

- `connections.json` - Suas configurações reais de conexão
- `jobs.json` - Suas configurações reais de jobs

## 🚀 Como Configurar

### 1. Copiar Arquivos de Exemplo

```bash
cp config/connections.json.example config/connections.json
cp config/jobs.json.example config/jobs.json
```

### 2. Editar Configurações

**connections.json:**

- Substitua os valores de exemplo pelos seus dados reais
- Configure hosts, usuários, senhas e schemas
- Ajuste caminhos de arquivos CSV conforme necessário

**jobs.json:**

- Configure suas queries SQL
- Ajuste variáveis conforme necessário
- Configure dependências entre jobs
- Ajuste tabelas de destino

## 🔒 Segurança

- ✅ Arquivos de exemplo são versionados (sem dados sensíveis)
- ❌ Arquivos reais são ignorados pelo Git
- 🔐 Senhas e credenciais não são expostas no repositório

## 📋 Tipos de Conexão Suportados

### PostgreSQL

```json
{
  "name": "postgres_connection",
  "type": "postgres",
  "params": {
    "host": "localhost",
    "port": 5432,
    "database": "database_name",
    "user": "username",
    "password": "password",
    "schema": "schema_name"
  }
}
```

### MySQL

```json
{
  "name": "mysql_connection",
  "type": "mysql",
  "params": {
    "host": "localhost",
    "port": 3306,
    "database": "database_name",
    "user": "username",
    "password": "password",
    "schema": "schema_name"
  }
}
```

### MSSQL

```json
{
  "name": "mssql_connection",
  "type": "mssql",
  "params": {
    "host": "localhost",
    "port": 1433,
    "database": "database_name",
    "user": "username",
    "password": "password",
    "schema": "schema_name"
  }
}
```

### Oracle

#### Conexão Direta

```json
{
  "name": "oracle_connection",
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

#### Conexão via TNS Names

```json
{
  "name": "oracle_tns_connection",
  "type": "oracle",
  "params": {
    "database": "ERP_PROD",
    "user": "oracle_user",
    "password": "oracle_password",
    "schema": "HR"
  }
}
```

**Dependências Oracle:**

```bash
pip install cx_Oracle
```

**Configuração TNS Names:**

- Configure o arquivo `tnsnames.ora` no cliente Oracle
- Use apenas o campo `database` com o nome do TNS
- Os campos `host` e `port` são opcionais para TNS Names

### SQLite

```json
{
  "name": "sqlite_connection",
  "type": "sqlite",
  "params": {
    "filepath": "./data/database.sqlite"
  }
}
```

### CSV

```json
{
  "name": "csv_connection",
  "type": "csv",
  "params": {
    "csv_file": "./data/file.csv",
    "csv_separator": ",",
    "csv_encoding": "utf-8",
    "csv_has_header": true
  }
}
```

## 🔗 Sistema de Dependências

Configure dependências entre jobs usando o campo `dependencies`:

```json
{
  "queryId": "job_with_dependencies",
  "type": "carga",
  "connection": "connection_name",
  "sql": "SELECT * FROM table;",
  "targetTable": "target_table",
  "dependencies": ["job1", "job2"]
}
```

## 📊 Sistema de Variáveis

Configure variáveis reutilizáveis:

```json
{
  "variables": {
    "start_date": {
      "value": "2024-01-01",
      "type": "string",
      "description": "Data de início"
    },
    "min_amount": {
      "value": 100.0,
      "type": "number",
      "description": "Valor mínimo"
    }
  }
}
```

Use variáveis nas queries:

```sql
SELECT * FROM table WHERE date >= '${var:start_date}' AND amount >= ${var:min_amount};
```

## 🛠️ Validação

Após configurar, valide suas configurações:

```bash
# Validar dependências
python -m app validate

# Listar jobs
python -m app list

# Testar conexões
python -m app test-connections
```

## 📝 Exemplos

Veja os arquivos de exemplo para referência completa:

- `connections.json.example`
- `jobs.json.example`

Execute os exemplos incluídos:

```bash
python schema_example.py
python variables_example.py
python csv_example.py
python dependencies_example.py
```
