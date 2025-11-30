#!/bin/bash

echo "Logs dos serviços:"
echo "=================================================="
echo ""

docker compose logs --tail=50 --follow
