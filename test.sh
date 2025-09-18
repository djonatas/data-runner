#!/bin/bash

# Data-Runner - Script de Testes
# Executa testes e validações do Data-Runner

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

log_test() {
    echo -e "${PURPLE}[TEST]${NC} $1"
}

# Banner
show_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Data-Runner Testes                      ║"
    echo "║              Validação e Testes do Sistema                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verificar ambiente
check_environment() {
    log_info "Verificando ambiente de teste..."
    
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
    
    log_success "Ambiente verificado"
}

# Teste de importação
test_imports() {
    log_test "Testando importações dos módulos..."
    
    local failed=0
    
    # Testar importações principais
    if python3 -c "from app.runner import JobRunner; print('✅ JobRunner')" 2>/dev/null; then
        log_success "JobRunner importado"
    else
        log_error "Erro ao importar JobRunner"
        ((failed++))
    fi
    
    if python3 -c "from app.connections import ConnectionFactory; print('✅ ConnectionFactory')" 2>/dev/null; then
        log_success "ConnectionFactory importado"
    else
        log_error "Erro ao importar ConnectionFactory"
        ((failed++))
    fi
    
    if python3 -c "from app.dependency_manager import DependencyManager; print('✅ DependencyManager')" 2>/dev/null; then
        log_success "DependencyManager importado"
    else
        log_error "Erro ao importar DependencyManager"
        ((failed++))
    fi
    
    if python3 -c "from app.variable_processor import VariableProcessor; print('✅ VariableProcessor')" 2>/dev/null; then
        log_success "VariableProcessor importado"
    else
        log_error "Erro ao importar VariableProcessor"
        ((failed++))
    fi
    
    if [ $failed -eq 0 ]; then
        log_success "Todas as importações funcionando"
        return 0
    else
        log_error "$failed importações falharam"
        return 1
    fi
}

# Teste de CLI
test_cli() {
    log_test "Testando interface de linha de comando..."
    
    local failed=0
    
    # Testar comando de ajuda
    if data-runner --help &> /dev/null; then
        log_success "Comando --help funcionando"
    else
        log_error "Erro no comando --help"
        ((failed++))
    fi
    
    # Testar comando list-jobs
    if data-runner list-jobs &> /dev/null; then
        log_success "Comando list-jobs funcionando"
    else
        log_warning "Comando list-jobs falhou (pode ser normal se não há jobs configurados)"
    fi
    
    # Testar comando history
    if data-runner history &> /dev/null; then
        log_success "Comando history funcionando"
    else
        log_warning "Comando history falhou (pode ser normal se não há histórico)"
    fi
    
    # Testar comando inspect
    if data-runner inspect &> /dev/null; then
        log_success "Comando inspect funcionando"
    else
        log_warning "Comando inspect falhou"
    fi
    
    if [ $failed -eq 0 ]; then
        log_success "CLI funcionando corretamente"
        return 0
    else
        log_error "$failed comandos CLI falharam"
        return 1
    fi
}

# Teste de configuração
test_config() {
    log_test "Testando arquivos de configuração..."
    
    local failed=0
    
    # Verificar se arquivos de exemplo existem
    if [ -f "config/connections.json.example" ]; then
        log_success "Arquivo connections.json.example existe"
        
        # Validar JSON
        if python3 -c "import json; json.load(open('config/connections.json.example'))" 2>/dev/null; then
            log_success "connections.json.example é JSON válido"
        else
            log_error "connections.json.example contém JSON inválido"
            ((failed++))
        fi
    else
        log_error "Arquivo connections.json.example não encontrado"
        ((failed++))
    fi
    
    if [ -f "config/jobs.json.example" ]; then
        log_success "Arquivo jobs.json.example existe"
        
        # Validar JSON
        if python3 -c "import json; json.load(open('config/jobs.json.example'))" 2>/dev/null; then
            log_success "jobs.json.example é JSON válido"
        else
            log_error "jobs.json.example contém JSON inválido"
            ((failed++))
        fi
    else
        log_error "Arquivo jobs.json.example não encontrado"
        ((failed++))
    fi
    
    # Verificar se arquivos de configuração atuais existem
    if [ -f "config/connections.json" ]; then
        log_info "Arquivo connections.json encontrado"
        
        if python3 -c "import json; json.load(open('config/connections.json'))" 2>/dev/null; then
            log_success "connections.json é JSON válido"
        else
            log_error "connections.json contém JSON inválido"
            ((failed++))
        fi
    else
        log_warning "Arquivo connections.json não encontrado (copie do .example)"
    fi
    
    if [ -f "config/jobs.json" ]; then
        log_info "Arquivo jobs.json encontrado"
        
        if python3 -c "import json; json.load(open('config/jobs.json'))" 2>/dev/null; then
            log_success "jobs.json é JSON válido"
        else
            log_error "jobs.json contém JSON inválido"
            ((failed++))
        fi
    else
        log_warning "Arquivo jobs.json não encontrado (copie do .example)"
    fi
    
    if [ $failed -eq 0 ]; then
        log_success "Configurações válidas"
        return 0
    else
        log_error "$failed problemas de configuração encontrados"
        return 1
    fi
}

# Teste de funcionalidades
test_functionality() {
    log_test "Testando funcionalidades principais..."
    
    local failed=0
    
    # Testar inicialização do JobRunner
    if python3 -c "
from app.runner import JobRunner
runner = JobRunner('./config')
print('✅ JobRunner inicializado')
" 2>/dev/null; then
        log_success "JobRunner inicializa corretamente"
    else
        log_error "Erro ao inicializar JobRunner"
        ((failed++))
    fi
    
    # Testar processamento de variáveis
    if python3 -c "
from app.variable_processor import VariableProcessor
from app.types import Variable, VariableType
vp = VariableProcessor()
var = Variable('test', 'value', VariableType.STRING)
vp.add_variable(var)
result = vp.process_sql('SELECT * FROM table WHERE col = \${var:test}')
print('✅ Processamento de variáveis funcionando')
" 2>/dev/null; then
        log_success "Processamento de variáveis funcionando"
    else
        log_error "Erro no processamento de variáveis"
        ((failed++))
    fi
    
    # Testar gerenciamento de dependências
    if python3 -c "
from app.dependency_manager import DependencyManager
from app.types import Job, JobType
jobs = [Job('job1', JobType.CARGA, 'conn1', 'SELECT 1')]
dm = DependencyManager(jobs)
order = dm.get_execution_order()
print('✅ Gerenciamento de dependências funcionando')
" 2>/dev/null; then
        log_success "Gerenciamento de dependências funcionando"
    else
        log_error "Erro no gerenciamento de dependências"
        ((failed++))
    fi
    
    if [ $failed -eq 0 ]; then
        log_success "Funcionalidades principais funcionando"
        return 0
    else
        log_error "$failed funcionalidades falharam"
        return 1
    fi
}

# Executar testes unitários
run_unit_tests() {
    log_test "Executando testes unitários..."
    
    if [ -d "tests" ] && [ -f "tests/test_config_parsing.py" ]; then
        if python3 -m pytest tests/ -v 2>/dev/null; then
            log_success "Testes unitários passaram"
            return 0
        else
            log_warning "Alguns testes unitários falharam (pode ser normal sem dependências)"
            return 1
        fi
    else
        log_warning "Testes unitários não encontrados"
        return 1
    fi
}

# Resumo dos testes
show_summary() {
    local total_tests=5
    local passed_tests=0
    
    echo ""
    log_info "Resumo dos Testes:"
    echo "==================="
    
    # Contar testes que passaram
    test_imports && ((passed_tests++))
    test_cli && ((passed_tests++))
    test_config && ((passed_tests++))
    test_functionality && ((passed_tests++))
    run_unit_tests && ((passed_tests++))
    
    echo ""
    if [ $passed_tests -eq $total_tests ]; then
        log_success "🎉 Todos os testes passaram! ($passed_tests/$total_tests)"
        echo ""
        log_success "Data-Runner está funcionando perfeitamente!"
    else
        log_warning "⚠️  $passed_tests de $total_tests testes passaram"
        echo ""
        log_warning "Alguns testes falharam. Verifique os erros acima."
    fi
    
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Configure suas conexões em config/connections.json"
    echo "2. Configure seus jobs em config/jobs.json"
    echo "3. Execute: ./run.sh para usar o Data-Runner"
}

# Menu de testes
show_menu() {
    echo ""
    echo "📋 Menu de Testes:"
    echo "1) Testar importações"
    echo "2) Testar CLI"
    echo "3) Testar configuração"
    echo "4) Testar funcionalidades"
    echo "5) Executar testes unitários"
    echo "6) Executar todos os testes"
    echo "7) Sair"
    echo ""
    
    read -p "Escolha uma opção (1-7): " choice
    
    case $choice in
        1)
            test_imports
            ;;
        2)
            test_cli
            ;;
        3)
            test_config
            ;;
        4)
            test_functionality
            ;;
        5)
            run_unit_tests
            ;;
        6)
            show_summary
            ;;
        7)
            log_success "Testes finalizados!"
            exit 0
            ;;
        *)
            log_warning "Opção inválida"
            ;;
    esac
}

# Função principal
main() {
    show_banner
    check_environment
    
    if [ $# -eq 0 ]; then
        # Modo interativo
        while true; do
            show_menu
            echo ""
            read -p "Pressione Enter para continuar..."
        done
    else
        # Modo direto
        case "$1" in
            "all")
                show_summary
                ;;
            "imports")
                test_imports
                ;;
            "cli")
                test_cli
                ;;
            "config")
                test_config
                ;;
            "functionality")
                test_functionality
                ;;
            "unit")
                run_unit_tests
                ;;
            "help"|"-h"|"--help")
                echo "Data-Runner Testes - Uso:"
                echo "  ./test.sh                    # Modo interativo"
                echo "  ./test.sh all                # Executar todos os testes"
                echo "  ./test.sh imports            # Testar importações"
                echo "  ./test.sh cli                # Testar CLI"
                echo "  ./test.sh config             # Testar configuração"
                echo "  ./test.sh functionality      # Testar funcionalidades"
                echo "  ./test.sh unit               # Testes unitários"
                echo "  ./test.sh help               # Mostrar ajuda"
                ;;
            *)
                log_error "Comando desconhecido: $1"
                echo "Use './test.sh help' para ver os comandos disponíveis"
                exit 1
                ;;
        esac
    fi
}

# Executar função principal
main "$@"
