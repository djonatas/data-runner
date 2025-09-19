# Variáveis de Ambiente no Data-Runner

O Data-Runner suporta o uso de variáveis de ambiente em arquivos de configuração, permitindo maior flexibilidade e segurança para diferentes ambientes.

## ⚡ Carregamento Automático

O Data-Runner carrega automaticamente o arquivo `.env` quando iniciado, não sendo necessário configurar manualmente as variáveis de ambiente.

**Log de carregamento:**

```
INFO - Carregando variáveis de ambiente de: /path/to/.env
```

## Padrão de Uso

Use o padrão `${env:VARIABLE_NAME}` em qualquer campo de string nos arquivos de configuração:

```json
{
  "connections": [
    {
      "name": "my_postgres",
      "type": "postgres",
      "params": {
        "host": "${env:POSTGRES_HOST}",
        "port": "${env:POSTGRES_PORT}",
        "database": "${env:POSTGRES_DATABASE}",
        "user": "${env:POSTGRES_USER}",
        "password": "${env:POSTGRES_PASSWORD}",
        "schema": "${env:POSTGRES_SCHEMA}"
      }
    }
  ]
}
```

## Variáveis Recomendadas

### PostgreSQL

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=my_database
POSTGRES_USER=my_user
POSTGRES_PASSWORD=my_password
POSTGRES_SCHEMA=public
```

### MySQL

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=my_database
MYSQL_USER=my_user
MYSQL_PASSWORD=my_password
MYSQL_SCHEMA=my_schema
```

### SQL Server

```bash
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=my_database
MSSQL_USER=my_user
MSSQL_PASSWORD=my_password
```

### Oracle

```bash
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_DATABASE=XE
ORACLE_USER=my_user
ORACLE_PASSWORD=my_password
ORACLE_SCHEMA=HR
```

### Configurações Gerais

```bash
DEFAULT_DUCKDB_PATH=./data/warehouse.duckdb
TENANT_UID=f9fc6810-691b-4102-8296-7bd19687ed5b
ENVIRONMENT=development
```

## Como Configurar

### 1. Criar arquivo .env

```bash
# Crie o arquivo .env na raiz do projeto
touch .env

# Edite com suas configurações
nano .env
```

### 2. Carregamento Automático

O Data-Runner carrega automaticamente o arquivo `.env` quando iniciado. Não é necessário carregar manualmente as variáveis.

**Locais onde o Data-Runner procura o arquivo .env:**

1. `./.env` (diretório atual)
2. `../.env` (diretório pai)
3. `./data-runner/.env` (raiz do projeto)
4. `~/.env` (home do usuário)

### 3. Usar no Data-Runner

```bash
# As variáveis serão automaticamente carregadas e substituídas
data-runner list-jobs
data-runner run --id meu_job
```

### 4. Carregamento Manual (Opcional)

Se preferir carregar manualmente:

```bash
# Linux/Mac
export $(cat .env | xargs)

# Windows (PowerShell)
Get-Content .env | ForEach-Object { $name, $value = $_.split('=', 2); Set-Item -Path "env:$name" -Value $value }
```

## Exemplos de Uso

### Conexão PostgreSQL com Variáveis

```json
{
  "name": "prod_postgres",
  "type": "postgres",
  "params": {
    "host": "${env:POSTGRES_HOST}",
    "port": "${env:POSTGRES_PORT}",
    "database": "${env:POSTGRES_DATABASE}",
    "user": "${env:POSTGRES_USER}",
    "password": "${env:POSTGRES_PASSWORD}",
    "schema": "${env:POSTGRES_SCHEMA}"
  }
}
```

### Caminho do DuckDB

```json
{
  "defaultDuckDbPath": "${env:DEFAULT_DUCKDB_PATH}"
}
```

### Variáveis em Jobs

```json
{
  "variables": {
    "tenant_uid": {
      "value": "${env:TENANT_UID}",
      "type": "string",
      "description": "UID do tenant"
    }
  }
}
```

## Segurança

- ✅ **Nunca commite** arquivos `.env` com senhas reais
- ✅ **Use diferentes arquivos** `.env` para cada ambiente
- ✅ **Mantenha senhas** em variáveis de ambiente do sistema
- ✅ **Use ferramentas** como Docker secrets ou Kubernetes secrets em produção

## Troubleshooting

### Variável não encontrada

Se uma variável não for encontrada, o Data-Runner manterá o padrão original `${env:VARIABLE_NAME}` e exibirá um warning no log.

### Verificar variáveis carregadas

```bash
# Linux/Mac
env | grep POSTGRES

# Windows
Get-ChildItem Env: | Where-Object {$_.Name -like "*POSTGRES*"}
```

### Testar substituição

```bash
# Teste com echo
echo "Host: ${env:POSTGRES_HOST}"
```
