#!/bin/bash

echo "🛑 Parando Forza Garage - Microsserviços"
echo "============================================================"
echo ""

docker compose down

echo ""
echo "✅ Microsserviços parados e removidos com sucesso!"
echo ""
echo "Containers removidos:"
echo "  • garage-service"
echo "  • analytics-service"
echo ""
echo "Rede removida:"
echo "  • garage-network"
echo ""
echo "============================================================"
