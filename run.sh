#!/bin/bash

# Data-Runner - Script de Execução
# Executa jobs do Data-Runner com facilidade

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Funções de log
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

log_run() {
    echo -e "${PURPLE}[RUN]${NC} $1"
}

# Banner
show_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Data-Runner Executor                     ║"
    echo "║              Executor de Jobs Parametrizados                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verificar ambiente
check_environment() {
    log_info "Verificando ambiente..."
    
    # Verificar se estamos no diretório correto
    if [ ! -f "pyproject.toml" ]; then
        log_error "Execute este script no diretório raiz do Data-Runner"
        exit 1
    fi
    
    # Verificar ambiente virtual
    if [ -d "venv" ]; then
        source venv/bin/activate
        log_success "Ambiente virtual ativado"
    else
        log_warning "Ambiente virtual não encontrado. Usando Python global"
    fi
    
    # Verificar CLI
    if ! command -v data-runner &> /dev/null; then
        log_error "data-runner não encontrado. Execute ./install.sh primeiro"
        exit 1
    fi
    
    log_success "Ambiente verificado"
}

# Listar jobs disponíveis
list_jobs() {
    log_info "Jobs disponíveis:"
    echo ""
    
    if data-runner list-jobs 2>/dev/null; then
        echo ""
    else
        log_warning "Nenhum job configurado ou erro ao listar jobs"
    fi
}

# Executar job único
run_single_job() {
    echo ""
    list_jobs
    
    read -p "Digite o ID do job para executar: " job_id
    
    if [ -z "$job_id" ]; then
        log_error "ID do job não pode estar vazio"
        return 1
    fi
    
    log_run "Executando job: $job_id"
    echo ""
    
    if data-runner run --id "$job_id"; then
        log_success "Job '$job_id' executado com sucesso!"
    else
        log_error "Erro ao executar job '$job_id'"
        return 1
    fi
}

# Executar múltiplos jobs
run_multiple_jobs() {
    echo ""
    list_jobs
    
    read -p "Digite os IDs dos jobs separados por vírgula: " jobs_input
    
    if [ -z "$jobs_input" ]; then
        log_error "IDs dos jobs não podem estar vazios"
        return 1
    fi
    
    # Converter vírgulas em espaços para o comando
    jobs=$(echo "$jobs_input" | tr ',' ' ')
    
    log_run "Executando jobs: $jobs"
    echo ""
    
    if data-runner run-batch $jobs; then
        log_success "Jobs executados com sucesso!"
    else
        log_error "Erro ao executar jobs"
        return 1
    fi
}

# Executar com opções
run_with_options() {
    echo ""
    list_jobs
    
    read -p "Digite o ID do job: " job_id
    read -p "Limite de linhas (opcional): " limit
    read -p "Dry-run (s/n): " dry_run
    
    if [ -z "$job_id" ]; then
        log_error "ID do job não pode estar vazio"
        return 1
    fi
    
    # Construir comando
    cmd="data-runner run --id $job_id"
    
    if [ ! -z "$limit" ]; then
        cmd="$cmd --limit $limit"
    fi
    
    if [ "$dry_run" = "s" ] || [ "$dry_run" = "S" ]; then
        cmd="$cmd --dry-run"
    fi
    
    log_run "Comando: $cmd"
    echo ""
    
    if eval $cmd; then
        log_success "Job '$job_id' executado com sucesso!"
    else
        log_error "Erro ao executar job '$job_id'"
        return 1
    fi
}

# Ver histórico
show_history() {
    log_info "Histórico de execuções:"
    echo ""
    
    if data-runner history 2>/dev/null; then
        echo ""
    else
        log_warning "Nenhum histórico encontrado ou erro ao carregar"
    fi
}

# Inspecionar DuckDB
inspect_database() {
    log_info "Inspecionando banco DuckDB:"
    echo ""
    
    if data-runner inspect 2>/dev/null; then
        echo ""
    else
        log_warning "Erro ao inspecionar banco de dados"
    fi
}

# Remover tabela
drop_table() {
    echo ""
    inspect_database
    echo ""
    
    read -p "Digite o nome da tabela para remover: " table_name
    
    if [ -z "$table_name" ]; then
        log_error "Nome da tabela não pode estar vazio"
        return 1
    fi
    
    log_warning "⚠️  ATENÇÃO: Esta operação irá remover permanentemente a tabela '$table_name'"
    read -p "Tem certeza? Digite 'SIM' para confirmar: " confirmation
    
    if [ "$confirmation" != "SIM" ]; then
        log_info "Operação cancelada"
        return 0
    fi
    
    log_run "Removendo tabela: $table_name"
    echo ""
    
    if data-runner drop-table --table "$table_name" --confirm 2>&1; then
        log_success "Tabela '$table_name' removida com sucesso!"
    else
        # Verificar se é erro de tabela protegida
        if data-runner drop-table --table "$table_name" --confirm 2>&1 | grep -q "tabela protegida"; then
            log_error "Não é possível remover tabelas do sistema (audit_job_runs)"
        else
            log_error "Erro ao remover tabela '$table_name'"
        fi
        return 1
    fi
}

# Menu principal
show_menu() {
    echo ""
    echo "📋 Menu Principal:"
    echo "1) Listar jobs disponíveis"
    echo "2) Executar job único"
    echo "3) Executar múltiplos jobs"
    echo "4) Executar com opções (limite, dry-run)"
    echo "5) Ver histórico de execuções"
    echo "6) Inspecionar banco DuckDB"
    echo "7) Remover tabela"
    echo "8) Sair"
    echo ""
    
    read -p "Escolha uma opção (1-8): " choice
    
    case $choice in
        1)
            list_jobs
            ;;
        2)
            run_single_job
            ;;
        3)
            run_multiple_jobs
            ;;
        4)
            run_with_options
            ;;
        5)
            show_history
            ;;
        6)
            inspect_database
            ;;
        7)
            drop_table
            ;;
        8)
            log_success "Data-Runner finalizado!"
            exit 0
            ;;
        *)
            log_warning "Opção inválida"
            ;;
    esac
}

# Execução direta por argumentos
run_direct() {
    if [ $# -eq 0 ]; then
        # Modo interativo
        show_banner
        check_environment
        echo ""
        log_success "Data-Runner pronto para uso!"
        
        while true; do
            show_menu
            echo ""
            read -p "Pressione Enter para continuar..."
        done
    else
        # Modo direto
        check_environment
        
        case "$1" in
            "list"|"ls")
                list_jobs
                ;;
            "run")
                if [ -z "$2" ]; then
                    log_error "ID do job necessário. Use: ./run.sh run <job_id>"
                    exit 1
                fi
                log_run "Executando job: $2"
                data-runner run --id "$2"
                ;;
            "batch")
                if [ -z "$2" ]; then
                    log_error "IDs dos jobs necessários. Use: ./run.sh batch <job1,job2,job3>"
                    exit 1
                fi
                jobs=$(echo "$2" | tr ',' ' ')
                log_run "Executando jobs: $jobs"
                data-runner run-batch $jobs
                ;;
            "history"|"hist")
                show_history
                ;;
            "inspect"|"db")
                inspect_database
                ;;
            "drop"|"drop-table")
                if [ -z "$2" ]; then
                    log_error "Nome da tabela necessário. Use: ./run.sh drop <table_name>"
                    exit 1
                fi
                log_warning "⚠️  ATENÇÃO: Esta operação irá remover permanentemente a tabela '$2'"
                read -p "Tem certeza? Digite 'SIM' para confirmar: " confirmation
                if [ "$confirmation" = "SIM" ]; then
                    if data-runner drop-table --table "$2" --confirm 2>&1; then
                        log_success "Tabela '$2' removida com sucesso!"
                    else
                        if data-runner drop-table --table "$2" --confirm 2>&1 | grep -q "tabela protegida"; then
                            log_error "Não é possível remover tabelas do sistema (audit_job_runs)"
                        else
                            log_error "Erro ao remover tabela '$2'"
                        fi
                    fi
                else
                    log_info "Operação cancelada"
                fi
                ;;
            "help"|"-h"|"--help")
                echo "Data-Runner Executor - Uso:"
                echo "  ./run.sh                    # Modo interativo"
                echo "  ./run.sh list               # Listar jobs"
                echo "  ./run.sh run <job_id>       # Executar job"
                echo "  ./run.sh batch <job1,job2>  # Executar múltiplos jobs"
                echo "  ./run.sh history            # Ver histórico"
                echo "  ./run.sh inspect            # Inspecionar banco"
                echo "  ./run.sh drop <table_name>  # Remover tabela"
                echo "  ./run.sh help               # Mostrar ajuda"
                ;;
            *)
                log_error "Comando desconhecido: $1"
                echo "Use './run.sh help' para ver os comandos disponíveis"
                exit 1
                ;;
        esac
    fi
}

# Executar função principal
run_direct "$@"
