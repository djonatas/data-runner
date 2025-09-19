# 📜 Scripts Shell do Data-Runner

Este documento descreve os scripts shell disponíveis para facilitar o uso do Data-Runner.

## 🚀 Scripts Disponíveis

### 1. `install.sh` - Instalação Completa

Script de instalação completa do Data-Runner com todas as dependências.

**Uso:**

```bash
./install.sh
```

**Funcionalidades:**

- ✅ Verifica Python 3.11+
- ✅ Cria ambiente virtual
- ✅ Instala dependências básicas
- ✅ Oferece instalação de dependências opcionais (MySQL, MSSQL, Oracle, Dev)
- ✅ Configura arquivos de exemplo
- ✅ Testa a instalação
- ✅ Interface colorida e interativa

**Dependências Opcionais:**

1. MySQL (mysql-connector-python)
2. MSSQL (pymssql)
3. Oracle (cx_Oracle)
4. Desenvolvimento (pytest, black, isort, etc.)
5. Todas as dependências
6. Pular (apenas básicas)

### 2. `setup.sh` - Setup Rápido

Script para configuração rápida e desenvolvimento.

**Uso:**

```bash
./setup.sh
```

**Funcionalidades:**

- ✅ Ativa ambiente virtual existente
- ✅ Configura arquivos de exemplo
- ✅ Cria backups dos arquivos existentes
- ✅ Menu interativo para configuração
- ✅ Testa configuração
- ✅ Mostra status do sistema

**Menu de Opções:**

1. Configurar arquivos de exemplo
2. Testar configuração
3. Mostrar status
4. Executar job de teste
5. Sair

### 3. `run.sh` - Executor de Jobs

Script principal para executar jobs do Data-Runner.

**Uso Interativo:**

```bash
./run.sh
```

**Uso Direto:**

```bash
./run.sh list                    # Listar jobs
./run.sh run <job_id>            # Executar job único
./run.sh batch <job1,job2>       # Executar múltiplos jobs
./run.sh history                 # Ver histórico
./run.sh inspect                 # Inspecionar banco
./run.sh help                    # Mostrar ajuda
```

**Funcionalidades:**

- ✅ Interface colorida e amigável
- ✅ Modo interativo e modo direto
- ✅ Lista jobs disponíveis
- ✅ Execução de jobs únicos e múltiplos
- ✅ Opções avançadas (limite, dry-run)
- ✅ Histórico de execuções
- ✅ Inspeção do banco DuckDB

### 4. `test.sh` - Testes e Validação

Script para executar testes e validações do sistema.

**Uso Interativo:**

```bash
./test.sh
```

**Uso Direto:**

```bash
./test.sh all                    # Executar todos os testes
./test.sh imports                # Testar importações
./test.sh cli                    # Testar CLI
./test.sh config                 # Testar configuração
./test.sh functionality          # Testar funcionalidades
./test.sh unit                   # Testes unitários
./test.sh help                   # Mostrar ajuda
```

**Funcionalidades:**

- ✅ Teste de importações dos módulos
- ✅ Validação da interface CLI
- ✅ Verificação de arquivos de configuração
- ✅ Teste de funcionalidades principais
- ✅ Execução de testes unitários
- ✅ Relatório de resumo dos testes

## 🎯 Fluxo de Uso Recomendado

### 1. Instalação Inicial

```bash
# Clone o repositório
git clone <repository-url>
cd data-runner

# Execute a instalação
./install.sh
```

### 2. Configuração

```bash
# Configure rapidamente
./setup.sh

# Ou configure manualmente
cp config/connections.json.example config/connections.json
cp config/jobs.json.example config/jobs.json
# Edite os arquivos conforme necessário
```

### 3. Testes

```bash
# Execute todos os testes
./test.sh all

# Ou teste individualmente
./test.sh imports
./test.sh config
```

### 4. Execução

```bash
# Modo interativo
./run.sh

# Ou execução direta
./run.sh list
./run.sh run "meu_job"
```

## 🔧 Características dos Scripts

### Interface Amigável

- 🎨 **Cores**: Diferentes cores para diferentes tipos de mensagem
- 📋 **Menus**: Interfaces interativas com opções numeradas
- ✅ **Status**: Indicadores claros de sucesso/erro
- 📊 **Progresso**: Feedback visual durante operações

### Robustez

- 🛡️ **Validações**: Verificações de ambiente e dependências
- 🔄 **Backups**: Criação automática de backups
- ❌ **Tratamento de Erros**: Saída em caso de erro crítico
- 🔍 **Verificações**: Validação de arquivos e configurações

### Flexibilidade

- 🎯 **Modo Interativo**: Para usuários iniciantes
- ⚡ **Modo Direto**: Para automação e scripts
- 🔧 **Opções**: Diferentes níveis de configuração
- 📝 **Logs**: Mensagens informativas e detalhadas

## 📋 Pré-requisitos

### Sistema

- **OS**: Linux, macOS, WSL (Windows)
- **Shell**: Bash 4.0+
- **Python**: 3.11 ou superior

### Dependências (instaladas automaticamente)

- **pip**: Gerenciador de pacotes Python
- **venv**: Módulo de ambiente virtual Python

## 🚨 Solução de Problemas

### Erro: "command not found"

```bash
# Verifique se o script é executável
chmod +x install.sh setup.sh run.sh test.sh
```

### Erro: "Python 3.11+ é necessário"

```bash
# Instale Python 3.11+ ou use pyenv
pyenv install 3.11.0
pyenv local 3.11.0
```

### Erro: "Ambiente virtual não encontrado"

```bash
# Execute a instalação primeiro
./install.sh
```

### Erro: "data-runner não encontrado"

```bash
# Ative o ambiente virtual
source venv/bin/activate
# Ou reinstale
./install.sh
```

## 📖 Exemplos de Uso

### Instalação Completa com Oracle

```bash
./install.sh
# Escolha opção 3 (Oracle) quando solicitado
```

### Setup e Teste Rápido

```bash
./setup.sh
# Escolha opção 2 (Testar configuração)
./test.sh all
```

### Execução de Pipeline

```bash
./run.sh batch "load_csv,transform_data,create_summary"
```

### Verificação de Sistema

```bash
./test.sh imports
./test.sh cli
./run.sh list
```

## 🎉 Conclusão

Os scripts shell do Data-Runner facilitam significativamente:

- **Instalação** e configuração inicial
- **Desenvolvimento** e testes
- **Execução** de jobs e pipelines
- **Manutenção** e validação do sistema

Use os scripts para uma experiência mais fluida e produtiva com o Data-Runner!
