#!/bin/bash

echo "Visualizando logs - Desafio 3"
echo "================================="

echo ""
echo "Container: postgres"
echo "---------------------------------"
docker logs forza-database --tail 50

echo ""
echo "Container: redis"
echo "---------------------------------"
docker logs forza-cache --tail 50

echo ""
echo "Container: api"
echo "--------------------------------"
docker logs forza-api --tail 50

echo ""
echo "================================="
