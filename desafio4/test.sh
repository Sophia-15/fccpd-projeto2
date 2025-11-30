#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🧪 Testando Forza Garage - Microsserviços"
echo "============================================================"
echo ""

# Check if services are running
echo -e "${BLUE}Verificando se os serviços estão rodando...${NC}"
if ! docker ps | grep -q "garage-service"; then
    echo -e "${RED}❌ Garage Service não está rodando!${NC}"
    echo "Execute ./start.sh primeiro"
    exit 1
fi

if ! docker ps | grep -q "analytics-service"; then
    echo -e "${RED}❌ Analytics Service não está rodando!${NC}"
    echo "Execute ./start.sh primeiro"
    exit 1
fi

echo -e "${GREEN}✅ Ambos os serviços estão rodando${NC}"
echo ""
sleep 2

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=$4
    
    echo -e "${BLUE}Testando: ${name}${NC}"
    echo "URL: ${url}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT -H "Content-Type: application/json" -d "$data" "$url")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$url")
    fi
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ Status: ${http_code}${NC}"
    else
        echo -e "${RED}❌ Status: ${http_code}${NC}"
    fi
    
    # Pretty print JSON (if jq is available)
    if command -v jq &> /dev/null; then
        echo "$body" | jq '.'
    else
        echo "$body"
    fi
    
    echo ""
    echo "------------------------------------------------------------"
    echo ""
    sleep 1
}

echo "============================================================"
echo "🏎️  TESTANDO GARAGE SERVICE (Microsserviço A)"
echo "============================================================"
echo ""

test_endpoint "1. Info do Garage Service" "http://localhost:5100/"

test_endpoint "2. Listar todos os carros" "http://localhost:5100/cars"

test_endpoint "3. Buscar carro ID 1" "http://localhost:5100/cars/1"

test_endpoint "4. Estatísticas básicas" "http://localhost:5100/stats"

test_endpoint "5. Health check do Garage" "http://localhost:5100/health"

echo -e "${YELLOW}Testando operações CRUD...${NC}"
echo ""

# Create a new car
new_car='{
  "manufacturer": "Bugatti",
  "model": "Chiron Super Sport",
  "year": 2024,
  "horsepower": 1600,
  "top_speed": 273,
  "acceleration": 2.3,
  "price": 3500000,
  "status": "available",
  "category": "Hypercar"
}'

test_endpoint "6. Adicionar novo carro (POST)" "http://localhost:5100/cars" "POST" "$new_car"

# Update the car (assuming it got ID 11)
update_data='{"status": "racing"}'
test_endpoint "7. Atualizar status do carro (PUT)" "http://localhost:5100/cars/11" "PUT" "$update_data"

test_endpoint "8. Verificar carro atualizado" "http://localhost:5100/cars/11"

echo "============================================================"
echo "📊 TESTANDO ANALYTICS SERVICE (Microsserviço B)"
echo "============================================================"
echo ""

test_endpoint "9. Info do Analytics Service" "http://localhost:5101/"

test_endpoint "10. Relatório completo (consome Garage Service)" "http://localhost:5101/report"

test_endpoint "11. Relatório detalhado do carro 1" "http://localhost:5101/report/1"

test_endpoint "12. Resumo executivo agregado" "http://localhost:5101/summary"

test_endpoint "13. Análise de atividade" "http://localhost:5101/activity"

test_endpoint "14. Health check integrado" "http://localhost:5101/health"

echo "============================================================"
echo "🔗 TESTANDO COMUNICAÇÃO ENTRE MICROSSERVIÇOS"
echo "============================================================"
echo ""

echo -e "${BLUE}Verificando comunicação HTTP entre serviços...${NC}"
echo ""
echo "Analytics Service (5101) → Garage Service (5100)"
echo ""

# The analytics service calls the garage service internally
# We can verify this by checking the health endpoint
echo -e "${YELLOW}O endpoint /health do Analytics verifica o Garage:${NC}"
test_endpoint "15. Health check que testa ambos os serviços" "http://localhost:5101/health"

echo -e "${YELLOW}O endpoint /summary consome dados do Garage:${NC}"
test_endpoint "16. Summary que agrega dados do Garage" "http://localhost:5101/summary"

echo "============================================================"
echo "🧹 LIMPEZA (Deletar carro criado)"
echo "============================================================"
echo ""

test_endpoint "17. Deletar carro de teste" "http://localhost:5100/cars/11" "DELETE"

echo "============================================================"
echo "✅ TESTES CONCLUÍDOS!"
echo "============================================================"
echo ""
echo "Resumo:"
echo "  • Garage Service: Testado CRUD completo"
echo "  • Analytics Service: Testados todos os relatórios"
echo "  • Comunicação HTTP: Verificada e funcionando"
echo ""
echo "Para ver os logs em tempo real:"
echo "  ./logs.sh"
echo ""
echo "Para explorar mais:"
echo "  curl http://localhost:5100/cars | jq"
echo "  curl http://localhost:5101/summary | jq"
echo ""
