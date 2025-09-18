#!/bin/bash

# Data-Runner - Script de Instalação
# Instala o Data-Runner e suas dependências

set -e  # Sair em caso de erro

echo "🚀 Data-Runner - Instalação"
echo "=========================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Python está instalado
check_python() {
    log_info "Verificando Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python encontrado: $PYTHON_VERSION"
        
        # Verificar se é Python 3.11+
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
            log_success "Versão do Python compatível (3.11+)"
        else
            log_error "Python 3.11+ é necessário. Versão atual: $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 não encontrado. Instale Python 3.11+ primeiro."
        exit 1
    fi
}

# Verificar se pip está instalado
check_pip() {
    log_info "Verificando pip..."
    
    if command -v pip3 &> /dev/null; then
        log_success "pip encontrado"
    else
        log_error "pip não encontrado. Instale pip primeiro."
        exit 1
    fi
}

# Criar ambiente virtual
create_venv() {
    log_info "Criando ambiente virtual..."
    
    if [ -d "venv" ]; then
        log_warning "Ambiente virtual já existe. Removendo..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    log_success "Ambiente virtual criado"
}

# Ativar ambiente virtual e instalar dependências
install_dependencies() {
    log_info "Ativando ambiente virtual e instalando dependências..."
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar pip
    log_info "Atualizando pip..."
    pip install --upgrade pip
    
    # Instalar dependências básicas
    log_info "Instalando dependências básicas..."
    pip install -e .
    
    # Perguntar sobre dependências opcionais
    echo ""
    log_info "Dependências opcionais disponíveis:"
    echo "1) MySQL (mysql-connector-python)"
    echo "2) MSSQL (pymssql)"
    echo "3) Oracle (cx_Oracle)"
    echo "4) Desenvolvimento (pytest, black, isort, etc.)"
    echo "5) Todas as dependências"
    echo "6) Pular (instalar apenas dependências básicas)"
    
    read -p "Escolha uma opção (1-6): " choice
    
    case $choice in
        1)
            log_info "Instalando dependências MySQL..."
            pip install -e ".[mysql]"
            ;;
        2)
            log_info "Instalando dependências MSSQL..."
            pip install -e ".[mssql]"
            ;;
        3)
            log_info "Instalando dependências Oracle..."
            pip install -e ".[oracle]"
            ;;
        4)
            log_info "Instalando dependências de desenvolvimento..."
            pip install -e ".[dev]"
            ;;
        5)
            log_info "Instalando todas as dependências..."
            pip install -e ".[all]"
            ;;
        6)
            log_info "Pulando dependências opcionais"
            ;;
        *)
            log_warning "Opção inválida. Instalando apenas dependências básicas."
            ;;
    esac
    
    log_success "Dependências instaladas"
}

# Configurar arquivos de exemplo
setup_config() {
    log_info "Configurando arquivos de configuração..."
    
    # Copiar arquivos de exemplo se não existirem
    if [ ! -f "config/connections.json" ]; then
        cp config/connections.json.example config/connections.json
        log_success "Arquivo config/connections.json criado"
    else
        log_info "Arquivo config/connections.json já existe"
    fi
    
    if [ ! -f "config/jobs.json" ]; then
        cp config/jobs.json.example config/jobs.json
        log_success "Arquivo config/jobs.json criado"
    else
        log_info "Arquivo config/jobs.json já existe"
    fi
    
    log_success "Configuração inicial concluída"
}

# Testar instalação
test_installation() {
    log_info "Testando instalação..."
    
    source venv/bin/activate
    
    # Testar importação
    if python3 -c "from app.runner import JobRunner; print('✅ JobRunner importado com sucesso')" 2>/dev/null; then
        log_success "Importação do JobRunner funcionando"
    else
        log_error "Erro na importação do JobRunner"
        exit 1
    fi
    
    # Testar CLI
    if data-runner --help &> /dev/null; then
        log_success "CLI do Data-Runner funcionando"
    else
        log_error "Erro no CLI do Data-Runner"
        exit 1
    fi
    
    log_success "Teste de instalação concluído"
}

# Função principal
main() {
    echo ""
    log_info "Iniciando instalação do Data-Runner..."
    echo ""
    
    check_python
    check_pip
    create_venv
    install_dependencies
    setup_config
    test_installation
    
    echo ""
    log_success "🎉 Data-Runner instalado com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Ative o ambiente virtual: source venv/bin/activate"
    echo "2. Configure suas conexões: nano config/connections.json"
    echo "3. Configure seus jobs: nano config/jobs.json"
    echo "4. Execute um job: data-runner run --id 'seu_job'"
    echo ""
    echo "📖 Para mais informações, consulte o README.md"
}

# Executar função principal
main "$@"
