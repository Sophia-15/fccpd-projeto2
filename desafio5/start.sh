#!/bin/bash

echo "Iniciando Desafio 5 - Central Perk API Gateway ☕"
echo "=================================================="

echo "Construindo imagens Docker..."
docker compose build

echo "Iniciando serviços..."
docker compose up -d

sleep 5

echo ""
echo "Serviços iniciados!"
echo ""
echo "Status dos containers:"
docker compose ps

echo ""
echo "Verificando saúde dos serviços..."
sleep 2
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo ""
echo "=================================================="
echo "Central Perk API Gateway ☕ - Online!"
echo "=================================================="
echo ""
echo "Gateway disponível em: http://localhost:8000"
echo "Barista: Gunther"
echo ""
echo "Endpoints disponíveis:"
echo ""
echo "  USERS:"
echo "    GET  /users                  - Listar todos os clientes"
echo "    GET  /users/<id>             - Buscar cliente por ID"
echo "    GET  /users/drink/<drink>    - Filtrar por bebida favorita"
echo ""
echo "  ORDERS:"
echo "    GET  /orders                    - Listar todos os pedidos"
echo "    GET  /orders/<id>               - Buscar pedido por ID"
echo "    GET  /orders/user/<user_id>     - Pedidos de um cliente"
echo "    GET  /orders/status/<status>    - Filtrar por status"
echo "    GET  /orders/category/<category> - Filtrar por categoria"
echo ""
echo "  COMBINED (Orquestração):"
echo "    GET  /users/<id>/orders      - Cliente com seus pedidos"
echo "    GET  /dashboard              - Dashboard completo"
echo ""
echo "  HEALTH:"
echo "    GET  /health                 - Status de todos os serviços"
echo ""
echo "Exemplos de uso:"
echo "  curl http://localhost:8000/users"
echo "  curl http://localhost:8000/users/1"
echo "  curl http://localhost:8000/orders"
echo "  curl http://localhost:8000/orders/category/Bebida%20Quente"
echo "  curl http://localhost:8000/users/1/orders"
echo "  curl http://localhost:8000/dashboard"
echo ""
echo "Acesso direto aos microsserviços (opcional):"
echo "  Users Service:  http://localhost:5001"
echo "  Orders Service:     http://localhost:5002"
echo ""
echo "=================================================="
