#!/bin/bash

# Script para ativar ambiente virtual e executar data-runner
# Uso: ./activate_and_run.sh [comando] [argumentos]

# Ativar ambiente virtual
source venv/bin/activate

# Executar data-runner com argumentos passados
data-runner "$@"
