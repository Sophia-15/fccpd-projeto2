#!/bin/bash

echo "Parando Desafio 3 - Forza Garage"
echo "===================="

docker compose down

echo ""
echo "Containers removidos!"
echo ""
echo "IMPORTANTE: O volume NAO foi removido!"
echo "Os dados da garagem persistem em: forza-postgres-data"
echo ""
echo "Para remover tambem o volume, use:"
echo "  docker compose down -v"
