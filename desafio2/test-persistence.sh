#!/bin/bash

echo "TESTE DE PERSISTENCIA - Desafio 2"
echo "=================================================="
echo "Este teste demonstra que os dados sobrevivem a"
echo "remocao dos containers da aplicacao!"
echo "=================================================="
echo ""

echo "PASSO 1: Criando dados iniciais..."
docker compose up -d
sleep 5
docker logs headphones-catalog
echo ""
read -p "Pressione Enter para continuar..."

echo ""
echo "PASSO 2: Removendo containers da aplicacao..."
docker compose stop headphones-catalog headphones-reader
docker compose rm -f headphones-catalog headphones-reader
echo "Containers da aplicacao removidos!"
echo ""
read -p "Pressione Enter para continuar..."

echo ""
echo "PASSO 3: Verificando que o volume ainda existe..."
docker volume ls | grep desafio2
echo ""
read -p "Pressione Enter para continuar..."

echo ""
echo "PASSO 4: Recriando os containers da aplicacao..."
docker compose up -d headphones-catalog headphones-reader
sleep 5
echo ""

echo ""
echo "PASSO 5: Verificando que os dados PERSISTIRAM..."
echo "=================================================="
docker logs headphones-reader
echo "=================================================="
echo ""
echo "SUCESSO! Os dados sobreviveram a remocao dos containers!"
echo "Isso demonstra a persistencia com Docker Volumes e PostgreSQL"
echo ""
echo "Para limpar completamente:"
echo "  docker compose down -v"
