#!/bin/bash

# Data-Runner - Script de Setup Rápido
# Configuração rápida para desenvolvimento

set -e

echo "⚡ Data-Runner - Setup Rápido"
echo "============================="

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Execute este script no diretório raiz do Data-Runner"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    log_info "Ativando ambiente virtual..."
    source venv/bin/activate
    log_success "Ambiente virtual ativado"
else
    log_warning "Ambiente virtual não encontrado. Execute ./install.sh primeiro"
    exit 1
fi

# Configurar arquivos de configuração
setup_config() {
    log_info "Configurando arquivos de configuração..."
    
    # Backup dos arquivos existentes
    if [ -f "config/connections.json" ]; then
        cp config/connections.json config/connections.json.backup
        log_info "Backup criado: config/connections.json.backup"
    fi
    
    if [ -f "config/jobs.json" ]; then
        cp config/jobs.json config/jobs.json.backup
        log_info "Backup criado: config/jobs.json.backup"
    fi
    
    # Copiar arquivos de exemplo
    cp config/connections.json.example config/connections.json
    cp config/jobs.json.example config/jobs.json
    
    log_success "Arquivos de configuração atualizados"
}

# Testar configuração
test_config() {
    log_info "Testando configuração..."
    
    # Verificar se os arquivos JSON são válidos
    if python3 -c "import json; json.load(open('config/connections.json')); json.load(open('config/jobs.json'))" 2>/dev/null; then
        log_success "Arquivos JSON válidos"
    else
        echo "❌ Erro na validação dos arquivos JSON"
        exit 1
    fi
    
    # Testar CLI
    if data-runner --help &> /dev/null; then
        log_success "CLI funcionando"
    else
        echo "❌ Erro no CLI"
        exit 1
    fi
}

# Mostrar status
show_status() {
    log_info "Status do Data-Runner:"
    echo ""
    
    # Listar jobs disponíveis
    echo "📋 Jobs disponíveis:"
    data-runner list-jobs 2>/dev/null || echo "  (Nenhum job configurado)"
    echo ""
    
    # Mostrar informações do ambiente
    echo "🔧 Informações do ambiente:"
    echo "  Python: $(python3 --version)"
    echo "  Diretório: $(pwd)"
    echo "  Ambiente virtual: $(which python3)"
    echo ""
}

# Menu interativo
show_menu() {
    echo "📋 Menu de Opções:"
    echo "1) Configurar arquivos de exemplo"
    echo "2) Testar configuração"
    echo "3) Mostrar status"
    echo "4) Executar job de teste"
    echo "5) Sair"
    echo ""
    
    read -p "Escolha uma opção (1-5): " choice
    
    case $choice in
        1)
            setup_config
            ;;
        2)
            test_config
            ;;
        3)
            show_status
            ;;
        4)
            log_info "Executando job de teste..."
            data-runner run --id "test_job" 2>/dev/null || echo "Job de teste não encontrado"
            ;;
        5)
            log_success "Setup concluído!"
            exit 0
            ;;
        *)
            log_warning "Opção inválida"
            ;;
    esac
}

# Função principal
main() {
    echo ""
    
    # Verificar se os arquivos de exemplo existem
    if [ ! -f "config/connections.json.example" ] || [ ! -f "config/jobs.json.example" ]; then
        echo "❌ Arquivos de exemplo não encontrados"
        exit 1
    fi
    
    # Loop do menu
    while true; do
        show_menu
        echo ""
        read -p "Pressione Enter para continuar..."
        echo ""
    done
}

# Executar
main "$@"
