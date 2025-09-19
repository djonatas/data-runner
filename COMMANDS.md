# Data-Runner - Comandos CLI

📚 **Documentação completa de todos os comandos disponíveis**

## 📖 Índice

- [🔄 Importação de Dados](#-importação-de-dados)
- [📤 Exportação de Dados](#-exportação-de-dados)
- [🔍 Validação de Dados](#-validação-de-dados)
- [📊 Monitoramento e Inspeção](#-monitoramento-e-inspeção)
- [⚙️ Gerenciamento](#️-gerenciamento)
- [🔧 Utilitários](#-utilitários)

---

## 🔄 Importação de Dados

### 📋 Listar Jobs de Importação

```bash
# Listar todos os jobs disponíveis
data-runner list-jobs

# Listar grupos de jobs
data-runner list-groups
```

**Descrição**: Exibe todos os jobs configurados no `jobs.json`, incluindo jobs de carga (importação), batimento (validação) e export-csv.

**Exemplo de saída**:

```
📋 Jobs Disponíveis:
================================================================================
ID: importar_usuarios
Tipo: carga
Conexão: postgres_db
Destino: stg_usuarios
SQL: SELECT * FROM usuarios WHERE ativo = true
--------------------------------------------------------------------------------
```

---

### 🎯 Executar Job de Importação Individual

```bash
# Executar um job específico
data-runner run --id importar_usuarios

# Executar com limite de linhas
data-runner run --id importar_usuarios --limit 1000

# Executar em modo dry-run (apenas simular)
data-runner run --id importar_usuarios --dry-run

# Executar com DuckDB personalizado
data-runner run --id importar_usuarios --duckdb ./meu_banco.duckdb

# Executar com nome de tabela personalizado
data-runner run --id importar_usuarios --save-as usuarios_custom
```

**Parâmetros**:

- `--id`: ID do job a ser executado (obrigatório)
- `--duckdb`: Caminho personalizado para o arquivo DuckDB
- `--dry-run`: Simula a execução sem executar realmente
- `--limit`: Limita o número de linhas a serem processadas
- `--save-as`: Nome personalizado para a tabela de destino

**Exemplo de saída**:

```
🎯 Execução Concluída:
Run ID: 12345
Status: success
Linhas processadas: 1500
Tabela alvo: stg_usuarios
✅ Execução bem-sucedida!
```

---

### 📦 Executar Múltiplos Jobs de Importação

```bash
# Executar múltiplos jobs em sequência
data-runner run-batch --ids job1,job2,job3

# Executar com limite global
data-runner run-batch --ids job1,job2 --limit 500

# Executar em modo dry-run
data-runner run-batch --ids job1,job2 --dry-run
```

**Parâmetros**:

- `--ids`: Lista de IDs separados por vírgula (obrigatório)
- `--duckdb`: Caminho personalizado para o DuckDB
- `--dry-run`: Simula a execução
- `--limit`: Limita linhas processadas
- `--save-as`: Nome personalizado para tabela

**Exemplo de saída**:

```
📊 Resumo da Execução em Lote:
================================================================================
✅ job1: success (1500 linhas)
✅ job2: success (2300 linhas)
❌ job3: error (0 linhas)
--------------------------------------------------------------------------------
Total: 3 jobs
Sucessos: 2
Erros: 1
```

---

### 🏷️ Executar Jobs por Tipo

```bash
# Executar todos os jobs de carga (importação)
data-runner run-group --type carga

# Executar todos os jobs de batimento (validação)
data-runner run-group --type batimento

# Executar com limite
data-runner run-group --type carga --limit 1000

# Executar em modo dry-run
data-runner run-group --type carga --dry-run
```

**Parâmetros**:

- `--type`: Tipo de job (carga, batimento, export-csv)
- `--duckdb`: Caminho personalizado para o DuckDB
- `--dry-run`: Simula a execução
- `--limit`: Limita linhas processadas

**Exemplo de saída**:

```
🎯 Executando Jobs do Tipo: carga
============================================================
📋 Jobs encontrados: 3
  - importar_usuarios
  - importar_produtos
  - importar_vendas

📊 Resumo da Execução em Grupo:
================================================================================
✅ importar_usuarios: success (1500 linhas)
✅ importar_produtos: success (800 linhas)
✅ importar_vendas: success (3200 linhas)
--------------------------------------------------------------------------------
Total: 3 jobs
Sucessos: 3
Erros: 0
```

---

### 🎭 Executar Grupos Configurados

```bash
# Executar grupo configurado no jobs.json
data-runner run-group-config --group cargas_diarias

# Executar com limite
data-runner run-group-config --group cargas_diarias --limit 5000

# Executar em modo dry-run
data-runner run-group-config --group cargas_diarias --dry-run
```

**Parâmetros**:

- `--group`: Nome do grupo configurado no jobs.json (obrigatório)
- `--duckdb`: Caminho personalizado para o DuckDB
- `--dry-run`: Simula a execução
- `--limit`: Limita linhas processadas

**Exemplo de saída**:

```
🎯 Executando Grupo de Jobs: cargas_diarias
============================================================
📝 Descrição: Carregamento diário de dados de produção
📋 Jobs: importar_usuarios, importar_produtos, importar_vendas
📊 Total: 3 jobs

📊 Resumo da Execução do Grupo:
================================================================================
✅ importar_usuarios: success (1500 linhas)
✅ importar_produtos: success (800 linhas)
✅ importar_vendas: success (3200 linhas)
--------------------------------------------------------------------------------
Total: 3 jobs
Sucessos: 3
Erros: 0
```

---

## 📤 Exportação de Dados

### 🎯 Executar Job de Export CSV

```bash
# Executar job de exportação para CSV
data-runner run --id exportar_relatorio

# Executar com limite de linhas
data-runner run --id exportar_relatorio --limit 5000

# Executar em modo dry-run
data-runner run --id exportar_relatorio --dry-run
```

**Parâmetros**: Mesmos parâmetros do comando `run` para jobs de importação.

**Exemplo de saída**:

```
🎯 Execução Concluída:
Run ID: 12346
Status: success
Linhas processadas: 2500
Tabela alvo: N/A
Arquivo CSV: relatorio_vendas_2024.csv
✅ Execução bem-sucedida!
```

---

### 📦 Executar Múltiplos Jobs de Export

```bash
# Executar múltiplos jobs de exportação
data-runner run-batch --ids export_rel1,export_rel2,export_rel3

# Executar com limite
data-runner run-batch --ids export_rel1,export_rel2 --limit 1000
```

**Parâmetros**: Mesmos parâmetros do comando `run-batch`.

**Exemplo de saída**:

```
📊 Resumo da Execução em Lote:
================================================================================
✅ export_rel1: success (2500 linhas)
✅ export_rel2: success (1800 linhas)
✅ export_rel3: success (3200 linhas)
--------------------------------------------------------------------------------
Total: 3 jobs
Sucessos: 3
Erros: 0
```

---

### 🏷️ Executar Todos os Jobs de Export

```bash
# Executar todos os jobs de export-csv
data-runner run-group --type export-csv

# Executar com limite
data-runner run-group --type export-csv --limit 2000
```

**Parâmetros**: Mesmos parâmetros do comando `run-group`.

**Exemplo de saída**:

```
🎯 Executando Jobs do Tipo: export-csv
============================================================
📋 Jobs encontrados: 2
  - exportar_relatorio_vendas
  - exportar_relatorio_usuarios

📊 Resumo da Execução em Grupo:
================================================================================
✅ exportar_relatorio_vendas: success (2500 linhas)
✅ exportar_relatorio_usuarios: success (1800 linhas)
--------------------------------------------------------------------------------
Total: 2 jobs
Sucessos: 2
Erros: 0
```

---

### 🎭 Executar Grupos de Export Configurados

```bash
# Executar grupo de relatórios configurado
data-runner run-group-config --group relatorios_semanais

# Executar com limite
data-runner run-group-config --group relatorios_semanais --limit 5000
```

**Parâmetros**: Mesmos parâmetros do comando `run-group-config`.

**Exemplo de saída**:

```
🎯 Executando Grupo de Jobs: relatorios_semanais
============================================================
📝 Descrição: Geração semanal de relatórios em CSV
📋 Jobs: export_vendas, export_usuarios, export_produtos
📊 Total: 3 jobs

📊 Resumo da Execução do Grupo:
================================================================================
✅ export_vendas: success (2500 linhas)
✅ export_usuarios: success (1800 linhas)
✅ export_produtos: success (800 linhas)
--------------------------------------------------------------------------------
Total: 3 jobs
Sucessos: 3
Erros: 0
```

---

## 🔍 Validação de Dados

### 🎯 Executar Job de Validação

```bash
# Executar validação individual
data-runner run --id validate_user_data

# Executar com limite de linhas
data-runner run --id validate_user_data --limit 1000

# Executar em modo dry-run
data-runner run --id validate_user_data --dry-run
```

**Parâmetros**: Mesmos parâmetros do comando `run` para outros tipos de job.

**Exemplo de saída**:

```
🎯 Execução Concluída:
Run ID: 12347
Status: success
Linhas processadas: 1500
Tabela alvo: N/A
Arquivo de Validação: user_data_validation.py
Resultado da Validação: Validação de usuários passou: 6 verificação(ões) executadas com sucesso
✅ Execução bem-sucedida!
```

---

### 🏷️ Executar Todas as Validações

```bash
# Executar todos os jobs de validation
data-runner run-group --type validation

# Executar com limite
data-runner run-group --type validation --limit 1000
```

**Parâmetros**: Mesmos parâmetros do comando `run-group`.

**Exemplo de saída**:

```
🎯 Executando Jobs do Tipo: validation
============================================================
📋 Jobs encontrados: 2
  - validate_user_data
  - validate_sales_data

📊 Resumo da Execução em Grupo:
================================================================================
✅ validate_user_data: success (1500 linhas)
⚠️  validate_sales_data: success (800 linhas) - Algumas verificações falharam
--------------------------------------------------------------------------------
Total: 2 jobs
Sucessos: 2
Erros: 0
```

---

### 🎭 Executar Grupos de Validação Configurados

```bash
# Executar grupo de validações configurado
data-runner run-group-config --group validations

# Executar com limite
data-runner run-group-config --group validations --limit 2000
```

**Parâmetros**: Mesmos parâmetros do comando `run-group-config`.

**Exemplo de saída**:

```
🎯 Executando Grupo de Jobs: validations
============================================================
📝 Descrição: Executa todas as validações de qualidade
📋 Jobs: validate_user_data, validate_sales_data
📊 Total: 2 jobs

📊 Resumo da Execução do Grupo:
================================================================================
✅ validate_user_data: success (1500 linhas)
⚠️  validate_sales_data: success (800 linhas)
--------------------------------------------------------------------------------
Total: 2 jobs
Sucessos: 2
Erros: 0
```

---

## 📊 Monitoramento e Inspeção

### 📈 Histórico de Execuções

```bash
# Ver histórico completo
data-runner history

# Ver histórico com limite personalizado
data-runner history --limit 20

# Ver histórico de job específico
data-runner history --query-id importar_usuarios

# Ver histórico de job com limite
data-runner history --query-id importar_usuarios --limit 10
```

**Parâmetros**:

- `--query-id`: Filtrar por ID específico de job
- `--limit`: Número máximo de registros (padrão: 50)

**Exemplo de saída**:

```
📈 Histórico de Execuções:
========================================================================================================================
✅ importar_usuarios | carga | 2024-01-15 14:30:25 | success | 1500 linhas | stg_usuarios
✅ exportar_relatorio | export-csv | 2024-01-15 14:25:10 | success | 2500 linhas | CSV: relatorio_vendas.csv
❌ importar_produtos | carga | 2024-01-15 14:20:15 | error | 0 linhas | stg_produtos
    Erro: Connection timeout
```

---

### 🔍 Inspeção de Dados

```bash
# Listar todas as tabelas
data-runner inspect

# Inspecionar tabela específica
data-runner inspect --table stg_usuarios

# Inspecionar tabela de auditoria
data-runner inspect --table audit_job_runs
```

**Parâmetros**:

- `--table`: Nome da tabela para inspecionar (opcional)

**Exemplo de saída (listar todas)**:

```
📋 Tabelas no DuckDB:
============================================================
stg_usuarios: 1500 linhas
stg_produtos: 800 linhas
stg_vendas: 3200 linhas
audit_job_runs: 45 linhas
```

**Exemplo de saída (tabela específica)**:

```
🔍 Inspeção da Tabela: stg_usuarios
============================================================
Estrutura:
  id: INTEGER
  nome: VARCHAR
  email: VARCHAR
  ativo: BOOLEAN
  created_at: TIMESTAMP

Linhas: 1500
```

---

## ⚙️ Gerenciamento

### 🗑️ Remoção de Tabelas

```bash
# Remover tabela com confirmação interativa
data-runner drop-table --table tabela_antiga

# Remover tabela sem confirmação
data-runner drop-table --table tabela_antiga --confirm
```

**Parâmetros**:

- `--table`: Nome da tabela a ser removida (obrigatório)
- `--confirm`: Confirma remoção sem pedir confirmação interativa

**Exemplo de saída**:

```
🗑️  Remoção de Tabela
==================================================
Tabela: tabela_antiga
Linhas: 1500

⚠️  Tem certeza que deseja remover a tabela 'tabela_antiga'? [y/N]: y
✅ Tabela 'tabela_antiga' removida com sucesso!
```

**Tabelas Protegidas**: As seguintes tabelas não podem ser removidas:

- `audit_job_runs`
- `audit_jobs_runs`
- `audit_job_run`
- `audit_jobs_run`

---

## 🔧 Utilitários

### 📋 Listar Grupos de Jobs

```bash
# Listar todos os grupos configurados
data-runner list-groups
```

**Exemplo de saída**:

```
📋 Grupos de Jobs Disponíveis:
================================================================================
Nome: cargas_diarias
Descrição: Carregamento diário de dados de produção
Jobs: importar_usuarios, importar_produtos, importar_vendas
Total: 3 jobs
--------------------------------------------------------------------------------
Nome: relatorios_semanais
Descrição: Geração semanal de relatórios em CSV
Jobs: export_vendas, export_usuarios, export_produtos
Total: 3 jobs
--------------------------------------------------------------------------------
```

---

### ❓ Ajuda e Versão

```bash
# Ajuda geral
data-runner --help

# Ajuda de comando específico
data-runner run --help
data-runner run-batch --help

# Versão do Data-Runner
data-runner --version
```

**Exemplo de saída (ajuda geral)**:

```
Usage: data-runner [OPTIONS] COMMAND [ARGS]...

  Data-Runner - Executor de consultas/processos parametrizado por JSON

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  drop-table        Remove uma tabela específica do DuckDB
  history           Exibe histórico de execuções
  inspect           Inspeciona tabelas no DuckDB
  list-groups       Lista todos os grupos de jobs disponíveis
  list-jobs         Lista todos os jobs disponíveis
  run               Executa um job específico
  run-batch         Executa múltiplos jobs em sequência
  run-group         Executa todos os jobs de um tipo específico
  run-group-config  Executa um grupo de jobs configurado no JSON
```

---

## 🎯 Casos de Uso Comuns

### 📊 Pipeline Completo de Dados

```bash
# 1. Executar todas as cargas
data-runner run-group --type carga

# 2. Executar validações
data-runner run-group --type batimento

# 3. Gerar relatórios
data-runner run-group --type export-csv

# 4. Verificar histórico
data-runner history --limit 20
```

### 🔄 Execução Diária Automatizada

```bash
# Executar grupo configurado para execução diária
data-runner run-group-config --group cargas_diarias

# Verificar resultados
data-runner inspect --table stg_usuarios
data-runner history --query-id importar_usuarios --limit 5
```

### 🧪 Teste e Desenvolvimento

```bash
# Testar configuração em modo dry-run
data-runner run --id meu_job --dry-run

# Executar com limite para testes
data-runner run --id meu_job --limit 100

# Verificar estrutura dos dados
data-runner inspect --table stg_teste
```

### 🧹 Limpeza e Manutenção

```bash
# Listar tabelas
data-runner inspect

# Remover tabela de teste
data-runner drop-table --table tabela_teste --confirm

# Verificar histórico de execuções
data-runner history --limit 10
```

---

## ⚠️ Observações Importantes

### 🔒 Tabelas Protegidas

- As tabelas de auditoria (`audit_job_runs` e variações) não podem ser removidas
- Tentativa de remoção resultará em erro com mensagem explicativa

### 📁 Arquivos CSV

- Jobs do tipo `export-csv` geram arquivos na raiz do projeto
- Nome do arquivo é configurado no parâmetro `csv_file` do job
- Arquivos são sobrescritos a cada execução

### 🔄 Modo Dry-Run

- Disponível em todos os comandos de execução
- Simula a execução sem modificar dados
- Útil para testar configurações e validar SQL

### 📊 Limites

- O parâmetro `--limit` controla quantas linhas são processadas
- Útil para testes e execuções parciais
- Não afeta a estrutura da tabela, apenas a quantidade de dados

### 🎯 Dependências

- Jobs com dependências são executados na ordem correta automaticamente
- Dependências circulares são detectadas e reportadas como erro
- Jobs independentes podem ser executados em paralelo

---

## 📞 Suporte

Para dúvidas sobre comandos específicos:

- Use `data-runner <comando> --help` para ajuda detalhada
- Consulte o `README.md` para exemplos de configuração
- Verifique o histórico com `data-runner history` para debug de execuções
