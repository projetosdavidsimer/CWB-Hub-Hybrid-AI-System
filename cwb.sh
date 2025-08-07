#!/bin/bash
# CWB Hub Hybrid AI System - Unix/Linux Shell Script
# Criado por: David Simer

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para exibir mensagens coloridas
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}💡 $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python não encontrado. Instale Python 3.8+ primeiro."
    print_info "Ubuntu/Debian: sudo apt install python3"
    print_info "CentOS/RHEL: sudo yum install python3"
    print_info "macOS: brew install python3"
    exit 1
fi

# Usar python3 se disponível, senão python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Verificar versão do Python
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $PYTHON_VERSION encontrado, mas é necessário Python $REQUIRED_VERSION ou superior."
    exit 1
fi

# Verificar se o arquivo CLI existe
if [ ! -f "cwb_cli.py" ]; then
    print_error "Arquivo cwb_cli.py não encontrado."
    print_info "Execute este script no diretório do CWB Hub."
    exit 1
fi

# Verificar se as dependências estão instaladas
if [ ! -d "src" ]; then
    print_warning "Diretório 'src' não encontrado."
    print_info "Execute primeiro: python install_dependencies.py"
fi

# Tornar o script executável se necessário
if [ ! -x "$0" ]; then
    chmod +x "$0"
fi

# Executar CLI com todos os argumentos passados
$PYTHON_CMD cwb_cli.py "$@"

# Capturar código de saída
EXIT_CODE=$?

# Mostrar ajuda se nenhum argumento foi passado
if [ $# -eq 0 ] && [ $EXIT_CODE -eq 0 ]; then
    echo ""
    print_info "Para usar: ./cwb.sh [comando] [argumentos]"
    print_info "Para ajuda: ./cwb.sh --help"
    echo ""
    echo "Exemplos rápidos:"
    echo "  ./cwb.sh query \"Como criar um app mobile?\""
    echo "  ./cwb.sh agents"
    echo "  ./cwb.sh status"
fi

exit $EXIT_CODE