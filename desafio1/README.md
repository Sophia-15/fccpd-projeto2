# Desafio 1 — Containers em Rede: Central Perk ☕

## 1. Descrição Geral da Solução

### 1.1 Proposta do Desafio

Este desafio demonstra a **comunicação entre containers Docker utilizando redes personalizadas**. O objetivo é criar dois containers isolados que se comunicam através de uma rede bridge customizada, simulando um ambiente de cafeteria onde um cliente automatizado faz pedidos para um servidor web.

A implementação explora conceitos fundamentais de Docker: isolamento de containers, resolução de nomes via DNS interno, comunicação HTTP entre serviços e mapeamento de portas para acesso externo.

### 1.2 Arquitetura Utilizada

A solução é composta por **três componentes principais**:

**1. Container Servidor (web-server)**
- **Imagem base**: Python 3.11-slim
- **Framework**: Flask (servidor web HTTP)
- **Função**: API REST que processa pedidos de cafeteria
- **Porta exposta**: 8080 (mapeada para host)
- **Armazenamento**: Dados em memória (dicionários Python)

**2. Container Cliente (web-client)**
- **Imagem base**: Alpine Linux
- **Tecnologia**: Shell script + curl
- **Função**: Cliente automatizado que envia requisições HTTP a cada 5 segundos
- **Comportamento**: Loop infinito simulando pedidos contínuos

**3. Rede Docker Customizada (desafio1-network)**
- **Tipo**: Bridge
- **Driver**: bridge (padrão Docker)
- **Características**: DNS interno automático, isolamento de tráfego
- **Resolução de nomes**: `web-client` pode acessar `web-server` pelo nome do container

### 1.3 Decisões Técnicas e Justificativas

**Por que Flask?**
Flask foi escolhido por ser um framework minimalista e ideal para APIs simples. Possui roteamento intuitivo, suporte nativo a JSON e permite criar endpoints REST rapidamente sem overhead de frameworks maiores.

**Por que Shell Script + curl no cliente?**
A escolha de Shell Script elimina dependências complexas. O Alpine Linux é extremamente leve (~5MB) e o curl é suficiente para fazer requisições HTTP. Essa abordagem demonstra que containers podem ser minimalistas e eficientes.

**Por que uma rede customizada?**
Redes customizadas fornecem DNS interno automático, permitindo que containers se referenciem por nome (ex: `http://web-server:8080`). Isso é mais robusto que usar IPs, que podem mudar a cada execução.

**Por que armazenamento em memória?**
Este desafio foca em comunicação de rede, não em persistência. Usar estruturas Python (dicionários, listas) simplifica o código e demonstra que nem todo serviço precisa de banco de dados.

**Organização do projeto:**
```
desafio1/
├── docker-compose.yml          # Orquestração dos serviços
├── start.sh, stop.sh, logs.sh  # Scripts de gerenciamento
├── server/
│   ├── app.py                  # API Flask
│   ├── Dockerfile              # Build do servidor
│   └── requirements.txt        # Dependências Python
└── client/
    ├── client.sh               # Script de automação
    └── Dockerfile              # Build do cliente
```

### 1.4 Tema: Central Perk

A cafeteria Central Perk (série Friends) foi escolhida como tema. O sistema gerencia:
- **6 clientes cadastrados**: Ross, Rachel, Monica, Chandler, Joey, Phoebe
- **8 itens no menu**: cafés (Espresso, Cappuccino, Latte, Mocha, Frappuccino) e doces (Muffin, Cookie, Cheesecake)
- **Sistema de cashback**: 1% de cada compra acumulado no CPF do cliente
- **Gunther como barista**: Todas as mensagens são atribuídas ao barista Gunther


## 2. Explicação Detalhada do Funcionamento

### 2.1 Container Servidor (web-server) - Arquitetura Interna

O servidor Flask (`app.py`) é uma API REST completa com as seguintes características técnicas:

**Estrutura de Dados em Memória:**
```python
# Dicionário com preços dos produtos
MENU = {
    "Espresso": {"price": 2.50},
    "Cappuccino": {"price": 3.75},
    # ... 8 itens no total
}

# Mapeamento nome -> CPF dos clientes
CUSTOMER_CPFS = {
    "Ross": "111.111.111-11",
    "Rachel": "222.222.222-22",
    # ... 6 clientes no total
}

# Cashback acumulado por CPF
customer_cashback = {}  # {"111.111.111-11": 0.12, ...}

# Contadores globais
total_orders = 0
daily_sales = 0.0
```

**Endpoints Implementados:**

1. **`GET /` - Fazer Pedido**
   - Seleciona aleatoriamente: 1 cliente + 1 item do menu
   - Calcula cashback (1% do preço)
   - Atualiza saldo do CPF no dicionário `customer_cashback`
   - Incrementa contadores de vendas
   - Retorna JSON com informações completas do pedido

2. **`GET /menu` - Visualizar Cardápio**
   - Lista todos os itens com preços
   - Calcula e mostra o cashback de cada item (1%)
   - Útil para conhecer a oferta da cafeteria

3. **`GET /stats` - Estatísticas**
   - Total de pedidos processados
   - Faturamento total (`daily_sales`)
   - Saldo de cashback acumulado por CPF de cada cliente
   - Ticket médio (vendas / pedidos)

4. **`GET /health` - Health Check**
   - Verifica se o servidor está respondendo
   - Retorna status operacional e hostname do container

**Fluxo de Processamento de um Pedido:**

```
Requisição GET / chega
    ↓
1. get_random_customer() → seleciona cliente aleatoriamente
2. get_random_item() → seleciona item do menu aleatoriamente
3. Busca preço no MENU[item]["price"]
4. calculate_cashback(price) → price * 0.01
5. Busca CPF do cliente em CUSTOMER_CPFS[name]
6. add_cashback(cpf, cashback_value) → atualiza customer_cashback[cpf]
7. total_orders += 1
8. daily_sales += price
9. Formata resposta JSON com todas as informações
    ↓
Resposta enviada ao cliente
```

**Exemplo de Resposta JSON:**
```json
{
  "order_number": 42,
  "timestamp": "2025-11-30 14:23:15",
  "customer": {
    "name": "Rachel",
    "cpf": "222.222.222-22"
  },
  "item": "Cappuccino",
  "price": 3.75,
  "cashback_earned": 0.04,
  "total_cashback": 0.87,
  "message": "Gunther preparou seu Cappuccino! ☕",
  "barista": "Gunther"
}
```

### 2.2 Container Cliente (web-client) - Comportamento Automatizado

O cliente é um **shell script Bash** executado no Alpine Linux que implementa um loop infinito:

**Lógica do Script (`client.sh`):**

```bash
SERVER_URL="http://web-server:8080"  # DNS interno resolve para o container
INTERVAL=5

while true; do
    # Faz requisição HTTP GET
    response=$(curl -s $SERVER_URL)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" $SERVER_URL)
    
    # Verifica sucesso (HTTP 200)
    if [ $http_code = "200" ]; then
        # Formata JSON com python3 (disponível no Alpine)
        echo "$response" | python3 -m json.tool
    else
        echo "Erro ao conectar (HTTP $http_code)"
    fi
    
    # Aguarda 5 segundos antes do próximo pedido
    sleep $INTERVAL
done
```

**Por que `curl` funciona aqui?**
O curl consegue acessar `http://web-server:8080` porque:
1. Ambos containers estão na mesma rede Docker (`desafio1-network`)
2. Docker fornece DNS interno que resolve `web-server` para o IP do container servidor
3. A porta 8080 está exposta no container servidor (EXPOSE no Dockerfile)

**Logs Esperados no Cliente:**
```
Central Perk - Sistema de Pedidos Automático
============================================================
Intervalo entre pedidos: 5 segundos
============================================================

Pedido #1 - 14:23:10
{
  "order_number": 1,
  "customer": {"name": "Ross", "cpf": "111.111.111-11"},
  "item": "Espresso",
  "price": 2.5,
  "cashback_earned": 0.03
}
Status: Pedido processado com sucesso (HTTP 200)
Aguardando 5 segundos...

Pedido #2 - 14:23:15
...
```

### 2.3 Comunicação de Rede entre Containers

**Rede Docker Customizada (`desafio1-network`):**

```yaml
networks:
  desafio1-network:
    name: desafio1-network
    driver: bridge
```

**Como funciona a resolução de nomes:**

1. Docker cria uma rede bridge isolada quando o compose sobe
2. Cada container recebe um IP interno (ex: 172.18.0.2, 172.18.0.3)
3. Docker injeta um **servidor DNS interno** (127.0.0.11) em cada container
4. Quando `web-client` faz `curl http://web-server:8080`:
   - O DNS interno resolve "web-server" para o IP do container servidor
   - A requisição é roteada internamente pela bridge
   - Nenhum tráfego sai para a rede externa

**Isolamento de Rede:**
- Apenas containers na mesma rede podem se comunicar
- O host pode acessar via port mapping (8080:8080)
- Outros containers fora da rede não conseguem se conectar

### 2.4 Mapeamento de Portas e Acesso Externo

**Port Mapping no docker-compose.yml:**

```yaml
web-server:
  ports:
    - "8080:8080"  # host:container
```

**Como funciona:**
- Container escuta internamente na porta 8080
- Docker mapeia: `localhost:8080` (host) → `172.18.0.2:8080` (container)
- Permite testar a API do host: `curl http://localhost:8080`

**Por que o cliente NÃO tem port mapping?**
O cliente apenas **faz requisições**, não precisa receber conexões. Ele acessa o servidor via DNS interno, não precisa ser acessado de fora.

### 2.5 Dependências e Ordem de Inicialização

**Configuração no docker-compose.yml:**

```yaml
web-client:
  depends_on:
    - web-server
```

**O que isso garante:**
- Docker inicia `web-server` ANTES de `web-client`
- Evita que o cliente tente se conectar antes do servidor estar pronto
- **Importante**: `depends_on` apenas garante ordem de início, não espera o servidor estar 100% operacional (para isso seria necessário `healthcheck`)

### 2.6 Logs e Observabilidade

**Estrutura de Logs:**

**Servidor Flask:**
```
☕ CENTRAL PERK CAFETERIA
🚀 Cafeteria aberta na porta 8080...
👨‍🦲 Barista: Gunther
[2025-11-30 14:23:15] 📋 Pedido #1 | Ross | ☕ Espresso ($2.50) | Cashback: +$0.03
[2025-11-30 14:23:20] 📋 Pedido #2 | Rachel | 🥛 Latte ($4.00) | Cashback: +$0.04
```

**Cliente Shell:**
```
Pedido #1 - 14:23:15
{"order_number": 1, "customer": "Ross", ...}
Status: Pedido processado com sucesso (HTTP 200)
Aguardando 5 segundos...
```

**Como visualizar logs:**
```bash
# Logs combinados (servidor + cliente)
docker-compose logs -f

# Apenas servidor
docker-compose logs -f web-server

# Apenas cliente
docker-compose logs -f web-client
```

## 3. Instruções de Execução – Passo a Passo

### 3.1 Pré-requisitos

**Software necessário:**
- Docker Engine 20.10 ou superior
- Docker Compose 1.29 ou superior (ou plugin Compose V2)
- Sistema operacional: Linux, macOS ou Windows com WSL2

**Verificar instalação:**
```bash
docker --version        # Docker version 24.0.7
docker-compose --version  # docker-compose version 1.29.2
```

### 3.2 Preparação do Ambiente

**1. Navegar até o diretório do desafio:**
```bash
cd /caminho/para/desafio1
```

**2. Verificar estrutura de arquivos:**
```bash
ls -la
# Deve conter: docker-compose.yml, server/, client/, *.sh
```

**3. Tornar scripts executáveis:**
```bash
chmod +x start.sh stop.sh logs.sh test.sh
```

### 3.3 Construção dos Containers

**Opção 1: Usar script automatizado (recomendado)**
```bash
./start.sh
```

**Opção 2: Comandos manuais**
```bash
# Construir as imagens
docker-compose build

# Verificar imagens criadas
docker images | grep desafio1
# desafio1-server  latest  ...
# desafio1-client  latest  ...
```

**O que acontece no build:**
- **Servidor**: Instala Python 3.11, copia `app.py`, instala Flask via `requirements.txt`
- **Cliente**: Usa Alpine Linux, copia `client.sh`, instala curl e python3

### 3.4 Iniciar a Aplicação

**Subir os containers:**
```bash
./start.sh
# OU manualmente:
docker-compose up -d
```

**Saída esperada:**
```
Creating network "desafio1-network" with driver "bridge"
Creating desafio1-web-server ... done
Creating desafio1-web-client ... done

☕ Central Perk iniciado com sucesso!
🏪 API: http://localhost:8080
👨‍� Barista: Gunther
```

**Verificar containers em execução:**
```bash
docker-compose ps
# NAME                    STATUS    PORTS
# desafio1-web-server     Up        0.0.0.0:8080->8080/tcp
# desafio1-web-client     Up
```

### 3.5 Testar a Aplicação

**1. Testar endpoint principal (fazer um pedido):**
```bash
curl http://localhost:8080
```

**Resposta esperada (exemplo):**
```json
{
  "order_number": 1,
  "timestamp": "2025-11-30 14:30:00",
  "customer": {
    "name": "Monica",
    "cpf": "333.333.333-33"
  },
  "item": "Mocha",
  "price": 4.5,
  "cashback_earned": 0.05,
  "total_cashback": 0.05,
  "message": "Gunther preparou seu Mocha! �",
  "barista": "Gunther"
}
```

**2. Visualizar cardápio:**
```bash
curl http://localhost:8080/menu
```

**Resposta esperada:**
```json
{
  "service": "Central Perk",
  "menu": [
    {
      "item": "Espresso",
      "price": 2.5,
      "cashback": 0.03,
      "emoji": "☕"
    },
    ...
  ]
}
```

**3. Ver estatísticas da cafeteria:**
```bash
curl http://localhost:8080/stats
```

**Resposta esperada:**
```json
{
  "service": "Central Perk Stats",
  "total_orders": 15,
  "daily_sales": 58.25,
  "average_ticket": 3.88,
  "customer_cashback": {
    "111.111.111-11": 0.12,
    "222.222.222-22": 0.08,
    "333.333.333-33": 0.15,
    ...
  }
}
```

**4. Verificar saúde do servidor:**
```bash
curl http://localhost:8080/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "service": "Central Perk",
  "timestamp": "2025-11-30 14:35:22",
  "hostname": "abc123def456"
}
```

### 3.6 Observar Logs em Tempo Real

**Visualizar logs combinados (servidor + cliente):**
```bash
./logs.sh
# OU manualmente:
docker-compose logs -f
```

**Exemplo de saída:**
```
web-server  | ☕ CENTRAL PERK CAFETERIA
web-server  | 🚀 Cafeteria aberta na porta 8080...
web-server  | [14:30:05] 📋 Pedido #1 | Rachel | ☕ Espresso ($2.50)
web-client  | Pedido #1 - 14:30:05
web-client  | Status: Pedido processado com sucesso (HTTP 200)
web-client  | Aguardando 5 segundos...
web-server  | [14:30:10] 📋 Pedido #2 | Joey | 🥤 Frappuccino ($5.50)
web-client  | Pedido #2 - 14:30:10
web-client  | Status: Pedido processado com sucesso (HTTP 200)
```

**Apenas logs do servidor:**
```bash
docker-compose logs -f web-server
```

**Apenas logs do cliente:**
```bash
docker-compose logs -f web-client
```

**Pressione `Ctrl+C` para sair dos logs** (não encerra os containers)

### 3.7 Testar Todos os Endpoints Automaticamente

```bash
./test.sh
```

**O script executa:**
1. Teste do endpoint `/`
2. Teste do endpoint `/menu`
3. Teste do endpoint `/stats`
4. Teste do endpoint `/health`
5. Verifica códigos HTTP 200

### 3.8 Inspecionar Rede e Containers

**Verificar rede criada:**
```bash
docker network inspect desafio1-network
```

**Informações exibidas:**
- Driver: bridge
- Subnet: 172.18.0.0/16 (exemplo)
- Containers conectados com seus IPs internos

**Inspecionar container servidor:**
```bash
docker inspect desafio1-web-server | grep IPAddress
# "IPAddress": "172.18.0.2"
```

**Acessar shell do container (debugging):**
```bash
# Entrar no servidor
docker exec -it desafio1-web-server /bin/bash

# Entrar no cliente
docker exec -it desafio1-web-client /bin/sh
```

### 3.9 Parar a Aplicação

**Opção 1: Script automatizado**
```bash
./stop.sh
```

**Opção 2: Manual**
```bash
docker-compose down
```

**O que acontece:**
- Containers são parados e removidos
- Rede `desafio1-network` é removida
- Imagens permanecem (não são deletadas)
- **Dados em memória são perdidos** (cashback, pedidos)

**Verificar que tudo foi removido:**
```bash
docker-compose ps
# Should show no containers
```

### 3.10 Remover Imagens (Limpeza Completa)

**Remover apenas imagens deste projeto:**
```bash
docker rmi desafio1-server desafio1-client
```

**Limpeza completa do Docker (cuidado!):**
```bash
docker system prune -a
# Remove TODAS imagens não utilizadas
```

### 3.11 Recriar do Zero

**Para garantir rebuild completo:**
```bash
./stop.sh
docker-compose build --no-cache
./start.sh
```

**Por que `--no-cache`?**
- Força rebuild completo sem usar cache de camadas anteriores
- Útil quando há alterações em `requirements.txt` ou dependências

---

## Observações Finais

**✅ Persistência de Dados:**
Os dados são armazenados em memória (estruturas Python). Ao parar os containers, todo o histórico de pedidos e cashback é perdido. Este desafio não utiliza volumes Docker intencionalmente, pois o foco é comunicação de rede.

**✅ Port Mapping:**
A porta 8080 deve estar livre no host. Se estiver ocupada, altere no `docker-compose.yml`: `"8081:8080"` e acesse via `http://localhost:8081`.

**✅ DNS Interno:**
O cliente acessa `http://web-server:8080` (nome do container), não `localhost` ou IP direto. Isso só funciona porque ambos estão na mesma rede Docker customizada.

**✅ Monitoramento:**
Use `./logs.sh` para visualizar a atividade em tempo real e entender o fluxo de comunicação HTTP entre os containers.

**✅ Testes Automatizados:**
Execute `./test.sh` para validar todos os endpoints da API automaticamente e verificar que a comunicação está funcionando corretamente.
