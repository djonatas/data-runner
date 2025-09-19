# Data-Runner - Guia do Desenvolvedor

🚀 **Guia completo para desenvolvedores que querem contribuir ou fazer fork do projeto**

## 📖 Índice

- [🎯 Visão Geral](#-visão-geral)
- [🏗️ Arquitetura](#️-arquitetura)
- [⚙️ Setup de Desenvolvimento](#️-setup-de-desenvolvimento)
- [🧪 Testes](#-testes)
- [📝 Padrões de Código](#-padrões-de-código)
- [🔧 Estrutura do Projeto](#-estrutura-do-projeto)
- [🔄 Fluxo de Desenvolvimento](#-fluxo-de-desenvolvimento)
- [📦 Contribuindo](#-contribuindo)
- [🚀 Fazendo Fork](#-fazendo-fork)
- [📚 Documentação](#-documentação)

---

## 🎯 Visão Geral

O **Data-Runner** é uma ferramenta de orquestração de pipelines de dados construída em Python que permite executar consultas SQL parametrizadas em múltiplas fontes de dados através de configurações JSON.

### 🎯 Objetivos do Projeto

- **Simplicidade**: Configuração via JSON, não código
- **Flexibilidade**: Suporte a múltiplas fontes de dados
- **Confiabilidade**: Sistema de dependências e auditoria
- **Performance**: Execução paralela e otimizada
- **Extensibilidade**: Arquitetura modular e plugável

### 🏆 Princípios de Design

- **Single Responsibility**: Cada classe tem uma responsabilidade específica
- **Dependency Injection**: Dependências injetadas via construtor
- **Factory Pattern**: Criação de conexões via factory
- **Strategy Pattern**: Diferentes estratégias de processamento
- **Observer Pattern**: Sistema de auditoria e logging

---

## 🏗️ Arquitetura

### 📊 Diagrama de Componentes

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Runner Layer   │    │  Repository     │
│                 │    │                 │    │                 │
│  app/cli.py     │───▶│ app/runner.py   │───▶│ app/repository.py│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Connections    │    │   Processors    │    │   DuckDB        │
│                 │    │                 │    │                 │
│ app/connections │    │ app/*_processor │    │ data/*.duckdb   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🧩 Componentes Principais

#### **CLI Layer** (`app/cli.py`)

- **Responsabilidade**: Interface de linha de comando
- **Tecnologia**: Click framework
- **Padrão**: Command Pattern

#### **Runner Layer** (`app/runner.py`)

- **Responsabilidade**: Orquestração e coordenação
- **Funcionalidades**:
  - Carregamento de configurações
  - Execução de jobs
  - Gerenciamento de dependências
  - Processamento de variáveis

#### **Repository Layer** (`app/repository.py`)

- **Responsabilidade**: Persistência e auditoria
- **Tecnologia**: DuckDB + pandas
- **Funcionalidades**:
  - Armazenamento de resultados
  - Auditoria de execuções
  - Inspeção de dados

#### **Connection Layer** (`app/connections.py`)

- **Responsabilidade**: Gerenciamento de conexões
- **Padrão**: Factory Pattern
- **Suporte**: PostgreSQL, MySQL, SQL Server, Oracle, CSV, SQLite

#### **Processing Layer** (`app/*_processor.py`)

- **EnvironmentVariableProcessor**: Processamento de variáveis de ambiente
- **VariableProcessor**: Processamento de variáveis configuráveis
- **DependencyManager**: Gerenciamento de dependências entre jobs

#### **Types Layer** (`app/types.py`)

- **Responsabilidade**: Definição de contratos e tipos
- **Tecnologia**: Python dataclasses + enums
- **Funcionalidades**: Tipagem estática e validação

---

## ⚙️ Setup de Desenvolvimento

### 📋 Pré-requisitos

- **Python**: 3.11 ou superior
- **Git**: Para controle de versão
- **Make**: Para automação (opcional)

### 🚀 Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/djonatas/data-runner.git
cd data-runner

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instale dependências de desenvolvimento
pip install -e ".[dev,all]"

# Configure arquivos de exemplo
cp config/connections.json.example config/connections.json
cp config/jobs.json.example config/jobs.json
```

### 🔧 Instalação Detalhada

#### 1. Dependências Básicas

```bash
pip install -e .
```

#### 2. Dependências de Desenvolvimento

```bash
pip install -e ".[dev]"
```

#### 3. Dependências Opcionais

```bash
# Para MySQL
pip install -e ".[mysql]"

# Para SQL Server
pip install -e ".[mssql]"

# Para Oracle
pip install -e ".[oracle]"

# Todas as dependências
pip install -e ".[all]"
```

### 🧪 Verificação da Instalação

```bash
# Teste básico
python -m app.cli --help

# Teste de importações
python -c "from app import runner, connections, repository"

# Executar testes
pytest tests/ -v
```

---

## 🧪 Testes

### 🏃 Execução de Testes

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_runner_sqlite.py -v

# Com cobertura
pytest tests/ --cov=app --cov-report=html

# Testes de integração
pytest tests/ -m integration

# Testes rápidos (excluir slow)
pytest tests/ -m "not slow"
```

### 📊 Estrutura de Testes

```
tests/
├── __init__.py              # Configuração de testes
├── test_config_parsing.py   # Testes de parsing de configuração
└── test_runner_sqlite.py    # Testes de integração com SQLite
```

### 🎯 Tipos de Testes

#### **Testes Unitários**

- Testam componentes isolados
- Mock de dependências externas
- Rápidos e determinísticos

#### **Testes de Integração**

- Testam interação entre componentes
- Usam banco de dados real (SQLite)
- Marcados com `@pytest.mark.integration`

#### **Testes de Performance**

- Testam performance e escalabilidade
- Marcados com `@pytest.mark.slow`
- Executados separadamente

### 📝 Escrevendo Testes

```python
import pytest
from app.runner import JobRunner
from app.types import Job, JobType

class TestJobRunner:
    def test_run_job_success(self):
        """Testa execução bem-sucedida de job"""
        runner = JobRunner()
        # Setup do teste
        # Execução
        # Assertions

    @pytest.mark.integration
    def test_run_job_with_sqlite(self):
        """Testa integração com SQLite"""
        # Teste de integração

    @pytest.mark.slow
    def test_performance_large_dataset(self):
        """Teste de performance com dataset grande"""
        # Teste de performance
```

---

## 📝 Padrões de Código

### 🎨 Formatação

O projeto usa **Black** para formatação automática:

```bash
# Formatar código
black app/ tests/

# Verificar formatação
black --check app/ tests/
```

### 📦 Importações

O projeto usa **isort** para organização de importações:

```bash
# Organizar importações
isort app/ tests/

# Verificar organização
isort --check-only app/ tests/
```

### 🔍 Linting

O projeto usa **flake8** para verificação de código:

```bash
# Verificar código
flake8 app/ tests/

# Com configuração específica
flake8 app/ tests/ --max-line-length=88
```

### 🔬 Type Checking

O projeto usa **mypy** para verificação de tipos:

```bash
# Verificar tipos
mypy app/

# Com configuração específica
mypy app/ --strict
```

### 📋 Configurações

As configurações estão no `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
strict_equality = true
```

---

## 🔧 Estrutura do Projeto

### 📁 Organização de Arquivos

```
data-runner/
├── app/                          # Código principal
│   ├── __init__.py              # Inicialização do pacote
│   ├── cli.py                   # Interface CLI
│   ├── runner.py                # Orquestrador principal
│   ├── connections.py           # Gerenciamento de conexões
│   ├── repository.py            # Persistência DuckDB
│   ├── types.py                 # Tipos e contratos
│   ├── env_processor.py         # Processamento de env vars
│   ├── variable_processor.py    # Processamento de variáveis
│   ├── dependency_manager.py    # Gerenciamento de dependências
│   └── sql_utils.py             # Utilitários SQL
├── config/                      # Configurações
│   ├── connections.json.example # Exemplo de conexões
│   └── jobs.json.example        # Exemplo de jobs
├── tests/                       # Testes
│   ├── __init__.py
│   ├── test_config_parsing.py
│   └── test_runner_sqlite.py
├── data/                        # Dados locais
│   └── warehouse.duckdb         # Banco DuckDB
├── scripts/                     # Scripts de automação
│   ├── install.sh
│   ├── setup.sh
│   ├── run.sh
│   └── test.sh
├── docs/                        # Documentação
│   ├── README.md
│   ├── COMMANDS.md
│   ├── SCRIPTS.md
│   └── DEVELOPER.md
├── pyproject.toml               # Configuração do projeto
├── requirements.txt             # Dependências
└── .gitignore                   # Arquivos ignorados
```

### 🏗️ Padrões de Arquitetura

#### **Separation of Concerns**

- **CLI**: Apenas interface de usuário
- **Runner**: Apenas orquestração
- **Repository**: Apenas persistência
- **Connections**: Apenas conexões

#### **Dependency Injection**

```python
class JobRunner:
    def __init__(self, repository: Optional[DuckDBRepository] = None):
        self.repository = repository or DuckDBRepository()
```

#### **Factory Pattern**

```python
class ConnectionFactory:
    @classmethod
    def create_connection(cls, connection: Connection) -> DatabaseConnection:
        connection_class = cls._connection_classes[connection.type]
        return connection_class(connection.params)
```

#### **Strategy Pattern**

```python
class DatabaseConnection(ABC):
    @abstractmethod
    def execute_query(self, sql: str) -> pd.DataFrame:
        pass
```

---

## 🔄 Fluxo de Desenvolvimento

### 🌿 Git Workflow

#### **Branches**

- **`master`**: Branch principal, sempre estável
- **`develop`**: Branch de desenvolvimento
- **`feature/*`**: Branches para novas funcionalidades
- **`bugfix/*`**: Branches para correções
- **`hotfix/*`**: Branches para correções urgentes

#### **Commits**

```bash
# Formato de commit
<type>: <descrição>

# Tipos aceitos
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: manutenção

# Exemplos
feat: adiciona suporte a Oracle TNS Names
fix: corrige processamento de variáveis de ambiente
docs: atualiza README com novos comandos
```

### 🔄 Processo de Desenvolvimento

#### **1. Nova Funcionalidade**

```bash
# Criar branch
git checkout -b feature/nova-funcionalidade

# Desenvolver
# ... código ...

# Testar
pytest tests/ -v

# Formatar
black app/ tests/
isort app/ tests/

# Commit
git add .
git commit -m "feat: adiciona nova funcionalidade"

# Push
git push origin feature/nova-funcionalidade
```

#### **2. Pull Request**

- Criar PR para `develop`
- Incluir descrição detalhada
- Referenciar issues relacionadas
- Aguardar revisão e aprovação

#### **3. Merge**

- Merge para `develop`
- Testes de integração
- Merge para `master` (releases)

### 🚀 Release Process

#### **1. Preparação**

```bash
# Atualizar versão no pyproject.toml
# Atualizar CHANGELOG.md
# Criar tag
git tag -a v1.1.0 -m "Release v1.1.0"
```

#### **2. Deploy**

```bash
# Build do pacote
python -m build

# Upload para PyPI (se aplicável)
python -m twine upload dist/*
```

---

## 📦 Contribuindo

### 🤝 Como Contribuir

#### **1. Fork do Repositório**

- Fork no GitHub
- Clone seu fork
- Configure remote upstream

```bash
git remote add upstream https://github.com/djonatas/data-runner.git
```

#### **2. Desenvolvimento**

- Siga os padrões de código
- Escreva testes para novas funcionalidades
- Mantenha cobertura de testes > 80%
- Documente mudanças importantes

#### **3. Pull Request**

- Descreva claramente as mudanças
- Inclua testes se aplicável
- Referencie issues relacionadas
- Aguarde revisão

### 📋 Checklist para Contribuições

#### **Código**

- [ ] Segue padrões de formatação (Black)
- [ ] Importações organizadas (isort)
- [ ] Passa em linting (flake8)
- [ ] Passa em type checking (mypy)
- [ ] Testes unitários incluídos
- [ ] Testes de integração se aplicável

#### **Documentação**

- [ ] README atualizado se necessário
- [ ] COMMANDS.md atualizado se novos comandos
- [ ] Docstrings em funções públicas
- [ ] Comentários em código complexo

#### **Testes**

- [ ] Novos testes para nova funcionalidade
- [ ] Testes existentes ainda passam
- [ ] Cobertura de testes mantida
- [ ] Testes de performance se aplicável

---

## 🚀 Fazendo Fork

### 🎯 Estratégias de Fork

#### **1. Fork para Uso Próprio**

- Mantenha sincronizado com upstream
- Adicione funcionalidades específicas
- Considere contribuir de volta

#### **2. Fork para Distribuição**

- Mantenha compatibilidade com upstream
- Documente diferenças claramente
- Considere mudar nome do projeto

#### **3. Fork para Experimentação**

- Liberdade total para mudanças
- Não precisa manter compatibilidade
- Ideal para POCs e experimentos

### 🔄 Sincronização com Upstream

```bash
# Buscar mudanças do upstream
git fetch upstream

# Merge das mudanças
git checkout master
git merge upstream/master

# Push para seu fork
git push origin master
```

### 📝 Personalizações Comuns

#### **1. Adicionar Novos Tipos de Conexão**

```python
# app/connections.py
class MongoDBConnection(DatabaseConnection):
    def execute_query(self, sql: str) -> pd.DataFrame:
        # Implementação específica do MongoDB
        pass

# Registrar no factory
ConnectionFactory._connection_classes[ConnectionType.MONGODB] = MongoDBConnection
```

#### **2. Adicionar Novos Tipos de Job**

```python
# app/types.py
class JobType(Enum):
    CARGA = "carga"
    BATIMENTO = "batimento"
    EXPORT_CSV = "export-csv"
    EXPORT_JSON = "export-json"  # Novo tipo
```

#### **3. Adicionar Novos Processadores**

```python
# app/custom_processor.py
class CustomProcessor:
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Lógica personalizada
        pass
```

---

## 📚 Documentação

### 📖 Documentação Disponível

- **README.md**: Guia principal para usuários
- **COMMANDS.md**: Documentação completa de comandos CLI
- **SCRIPTS.md**: Documentação dos scripts de automação
- **DEVELOPER.md**: Este guia para desenvolvedores

### 📝 Padrões de Documentação

#### **Docstrings**

```python
def execute_query(self, sql: str) -> pd.DataFrame:
    """
    Executa uma consulta SQL no banco de dados.

    Args:
        sql: Consulta SQL a ser executada

    Returns:
        DataFrame com os resultados da consulta

    Raises:
        DatabaseError: Se a consulta falhar
        ConnectionError: Se a conexão falhar
    """
```

#### **Comentários**

```python
# Processar variáveis de ambiente antes de criar conexão
# Isso garante que ${env:VAR} seja resolvido corretamente
env_processor = EnvironmentVariableProcessor()
processed_params = env_processor.process_dict(params_dict)
```

### 🔧 Ferramentas de Documentação

#### **Geração Automática**

```bash
# Instalar sphinx (opcional)
pip install sphinx sphinx-rtd-theme

# Gerar documentação
sphinx-build -b html docs/ docs/_build/html
```

#### **Validação de Links**

```bash
# Instalar linkchecker
pip install linkchecker

# Verificar links na documentação
linkchecker docs/
```

---

## 🎯 Roadmap e Ideias

### 🚀 Funcionalidades Futuras

#### **Curto Prazo**

- [ ] Suporte a MongoDB
- [ ] Suporte a Redis
- [ ] Interface web básica
- [ ] Métricas e dashboards

#### **Médio Prazo**

- [ ] Suporte a streaming de dados
- [ ] Integração com Apache Airflow
- [ ] Suporte a Kubernetes
- [ ] API REST

#### **Longo Prazo**

- [ ] Interface gráfica
- [ ] Suporte a machine learning
- [ ] Integração com cloud providers
- [ ] Sistema de plugins

### 💡 Ideias para Contribuição

#### **Para Iniciantes**

- Melhorar documentação
- Adicionar exemplos
- Corrigir typos
- Melhorar testes

#### **Para Intermediários**

- Adicionar novos tipos de conexão
- Implementar novos processadores
- Melhorar performance
- Adicionar métricas

#### **Para Avançados**

- Refatorar arquitetura
- Implementar cache distribuído
- Adicionar suporte a streaming
- Criar interface web

---

## 📞 Suporte e Comunidade

### 🤝 Como Obter Ajuda

- **Issues**: [GitHub Issues](https://github.com/djonatas/data-runner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/djonatas/data-runner/discussions)
- **Documentação**: Consulte os arquivos .md do projeto

### 🎯 Guidelines da Comunidade

- Seja respeitoso e construtivo
- Pesquise antes de perguntar
- Forneça contexto detalhado
- Ajude outros desenvolvedores

### 📋 Template para Issues

```markdown
## Descrição

Descrição clara do problema ou funcionalidade.

## Ambiente

- OS: [ex: Linux, macOS, Windows]
- Python: [ex: 3.11.0]
- Data-Runner: [ex: 1.0.0]

## Passos para Reproduzir

1. ...
2. ...
3. ...

## Comportamento Esperado

O que deveria acontecer.

## Comportamento Atual

O que está acontecendo.

## Logs/Erros
```

Traceback (most recent call last):
...

```

## Contexto Adicional
Qualquer informação adicional relevante.
```

---

## 🎉 Conclusão

O Data-Runner é um projeto open-source que valoriza contribuições da comunidade. Seja para correções, melhorias ou novas funcionalidades, toda contribuição é bem-vinda!

### 🚀 Próximos Passos

1. **Fork o repositório**
2. **Configure o ambiente de desenvolvimento**
3. **Escolha uma issue ou crie uma nova funcionalidade**
4. **Siga os padrões e guidelines**
5. **Faça um pull request**
6. **Participe da comunidade**

**Bem-vindo ao Data-Runner! 🎯🚀**
