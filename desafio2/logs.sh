#!/bin/bash

echo "Visualizando logs - Desafio 2"
echo "================================="

echo ""
echo "Container: postgres"
echo "---------------------------------"
docker logs headphones-postgres

echo ""
echo "Container: headphones-catalog"
echo "---------------------------------"
docker logs headphones-catalog

echo ""
echo "Container: headphones-reader"
echo "--------------------------------"
docker logs headphones-reader

echo ""
echo "================================="
