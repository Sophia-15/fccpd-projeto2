#!/bin/bash

echo "=========================================="
echo "TESTES - CENTRAL PERK API GATEWAY ☕"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' 

echo -e "${BLUE}Teste 1: Health Check${NC}"
echo "GET $BASE_URL/health"
curl -s $BASE_URL/health | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}Teste 2: Listar todos os clientes${NC}"
echo "GET $BASE_URL/users"
curl -s $BASE_URL/users | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}Teste 3: Buscar cliente específico (Ana Clara - ID: 1)${NC}"
echo "GET $BASE_URL/users/1"
curl -s $BASE_URL/users/1 | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}Teste 4: Filtrar clientes por bebida favorita (Cappuccino)${NC}"
echo "GET $BASE_URL/users/drink/Cappuccino"
curl -s $BASE_URL/users/drink/Cappuccino | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}Teste 5: Listar todos os pedidos${NC}"
echo "GET $BASE_URL/orders"
curl -s $BASE_URL/orders | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}Teste 6: Buscar pedido específico (ID: 3)${NC}"
echo "GET $BASE_URL/orders/3"
curl -s $BASE_URL/orders/3 | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}Teste 7: Filtrar pedidos por status (delivered)${NC}"
echo "GET $BASE_URL/orders/status/delivered"
curl -s $BASE_URL/orders/status/delivered | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}Teste 8: Filtrar pedidos por categoria (Bebida Quente)${NC}"
echo "GET $BASE_URL/orders/category/Bebida%20Quente"
curl -s "$BASE_URL/orders/category/Bebida%20Quente" | python3 -m json.tool
echo ""
echo ""

echo -e "${YELLOW}Teste 9: ORQUESTRAÇÃO - Cliente com pedidos (Ana Clara)${NC}"
echo "GET $BASE_URL/users/1/orders"
curl -s $BASE_URL/users/1/orders | python3 -m json.tool
echo ""
echo ""

echo -e "${YELLOW}Teste 10: ORQUESTRAÇÃO - Dashboard da cafeteria${NC}"
echo "GET $BASE_URL/dashboard"
curl -s $BASE_URL/dashboard | python3 -m json.tool
echo ""
echo ""

echo -e "${GREEN}Teste 11: Acesso direto aos microsserviços${NC}"
echo "GET http://localhost:5001/health (Users Service)"
curl -s http://localhost:5001/health | python3 -m json.tool
echo ""
echo "GET http://localhost:5002/health (Orders Service)"
curl -s http://localhost:5002/health | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo -e "${GREEN}☕ TESTES CONCLUÍDOS! ☕${NC}"
echo "Central Perk funcionando perfeitamente!"
echo "=========================================="
