#!/bin/bash

echo "Testando Endpoints - Forza Garage API"
echo "=================================================="

BASE_URL="http://localhost:5000"

echo ""
echo "1. Testando endpoint raiz (/)..."
echo "=================================================="
curl -s $BASE_URL | python3 -m json.tool
echo ""

sleep 1

echo ""
echo "2. Testando health check (/health)..."
echo "=================================================="
curl -s $BASE_URL/health | python3 -m json.tool
echo ""

sleep 1

echo ""
echo "3. Listando todos os carros (/cars)..."
echo "=================================================="
curl -s $BASE_URL/cars | python3 -m json.tool | head -50
echo "..."
echo ""

sleep 1

echo ""
echo "4. Buscando carro especifico (/cars/1)..."
echo "=================================================="
curl -s $BASE_URL/cars/1 | python3 -m json.tool
echo ""

sleep 1

echo ""
echo "5. Carros por classe S2 (/cars/class/S2)..."
echo "=================================================="
curl -s $BASE_URL/cars/class/S2 | python3 -m json.tool | head -30
echo "..."
echo ""

sleep 1

echo ""
echo "6. Carros Legendary (/cars/rarity/Legendary)..."
echo "=================================================="
curl -s $BASE_URL/cars/rarity/Legendary | python3 -m json.tool | head -30
echo "..."
echo ""

sleep 1

echo ""
echo "7. Estatisticas da garagem (/stats)..."
echo "=================================================="
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""

echo ""
echo "8. Testando cache (segunda requisicao de /stats)..."
echo "=================================================="
echo "Observe o campo 'source' - deve ser 'cache':"
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""

echo ""
echo "=================================================="
echo "Testes concluidos!"
echo "=================================================="
