#!/bin/bash

echo "Iniciando Desafio 2 - Docker Volumes e Persistencia"
echo "=================================================="

echo "Construindo imagens Docker..."
docker compose build

echo "Iniciando containers..."
docker compose up -d

sleep 5

echo ""
echo "Logs do container principal:"
docker logs headphones-catalog

echo ""
echo "Logs do container leitor:"
docker logs headphones-reader

echo ""
echo "Containers iniciados!"
echo ""
echo "Status dos containers:"
docker compose ps

echo ""
echo "Volume criado:"
docker volume ls | grep desafio2

echo ""
echo "=================================================="
echo "Desafio 2 rodando!"
echo "=================================================="
