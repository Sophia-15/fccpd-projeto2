#!/bin/bash

echo "Parando Desafio 2"
echo "===================="

docker compose down

echo ""
echo "Containers removidos!"
echo ""
echo "IMPORTANTE: O volume NAO foi removido!"
echo "Os dados persistem em: desafio2-postgres-data"
echo ""
echo "Para remover tambem o volume, use:"
echo "  docker compose down -v"
