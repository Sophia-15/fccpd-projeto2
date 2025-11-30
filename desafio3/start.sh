#!/bin/bash

echo "Iniciando Desafio 3 - Forza Garage"
echo "=================================================="

echo "Construindo imagens Docker..."
docker compose build

echo "Iniciando servicos..."
docker compose up -d

sleep 3

echo ""
echo "Servicos iniciados!"
echo ""
echo "Status dos containers:"
docker compose ps

echo ""
echo "Verificando saude dos servicos..."
sleep 2
curl -s http://localhost:5000/health | python3 -m json.tool

echo ""
echo ""
echo "=================================================="
echo "Forza Garage rodando!"
echo "=================================================="
echo ""
echo "API disponivel em: http://localhost:5000"
echo ""
echo "Endpoints disponiveis:"
echo "  GET  /              - Informacoes da API"
echo "  GET  /cars          - Listar todos os carros"
echo "  GET  /cars/<id>     - Buscar carro por ID"
echo "  GET  /cars/class/<class>   - Carros por classe"
echo "  GET  /cars/rarity/<rarity> - Carros por raridade"
echo "  GET  /stats         - Estatisticas da garagem"
echo "  GET  /health        - Status dos servicos"
echo ""
echo "Exemplos:"
echo "  curl http://localhost:5000/cars"
echo "  curl http://localhost:5000/cars/1"
echo "  curl http://localhost:5000/cars/class/S2"
echo "  curl http://localhost:5000/cars/rarity/Legendary"
echo "  curl http://localhost:5000/stats"
echo ""
echo "=================================================="
