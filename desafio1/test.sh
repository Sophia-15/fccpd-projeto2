#!/bin/bash

echo "Testando Cafeteria Central Perk"
echo "============================================================"
echo ""

echo "1. Fazendo um pedido (/):"
echo "------------------------------------------------------------"
curl -s http://localhost:8080 | python3 -m json.tool
echo ""
echo ""

echo "2. Verificando status (/health):"
echo "------------------------------------------------------------"
curl -s http://localhost:8080/health | python3 -m json.tool
echo ""
echo ""

echo "3. Consultando estatísticas (/stats):"
echo "------------------------------------------------------------"
curl -s http://localhost:8080/stats | python3 -m json.tool
echo ""
echo ""

echo "4. Visualizando cardápio (/menu):"
echo "------------------------------------------------------------"
curl -s http://localhost:8080/menu | python3 -m json.tool
echo ""
echo ""

echo "5. Logs dos clientes (últimas 25 linhas):"
echo "------------------------------------------------------------"
docker compose logs --tail=25 web-client
echo ""
echo ""

echo "6. Informações da rede Docker:"
echo "------------------------------------------------------------"
docker network inspect desafio1-network --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}'
echo ""

echo "TESTES CONCLUÍDOS!"
echo "============================================================"
