#!/bin/bash

SERVER_URL="http://web-server:8080"
INTERVAL=5

CUSTOMERS=("Ross" "Rachel" "Monica" "Chandler" "Joey" "Phoebe")

echo "Central Perk - Sistema de Pedidos Automático"
echo "============================================================"
echo "Intervalo entre pedidos: $INTERVAL segundos"
echo "============================================================"

count=0

while true; do
    count=$((count + 1))
    
    echo ""
    echo "Pedido #$count - $(date '+%H:%M:%S')"
    
    response=$(curl -s $SERVER_URL)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" $SERVER_URL)
    
    if [ $? -eq 0 ] && [ "$http_code" = "200" ]; then
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        echo ""
        echo "Status: Pedido processado com sucesso (HTTP $http_code)"
    else
        echo "Erro ao conectar à cafeteria"
        echo "Status Code: $http_code"
    fi
    
    echo "Aguardando $INTERVAL segundos..."
    
    sleep $INTERVAL
done
