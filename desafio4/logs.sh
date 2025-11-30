#!/bin/bash

echo "📋 Exibindo logs dos microsserviços..."
echo "============================================================"
echo ""
echo "Pressione Ctrl+C para sair"
echo ""
echo "============================================================"
echo ""

docker compose logs -f
