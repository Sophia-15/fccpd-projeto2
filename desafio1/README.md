# Desafio 1 — Containers em Rede: Central Perk ☕

## 📋 Descrição da Solução

Este projeto implementa um sistema de cafeteria baseado no **Central Perk**, utilizando dois containers Docker que se comunicam através de uma rede customizada:

1. **Servidor (Central Perk)**: Uma API Flask que simula a cafeteria, processando pedidos e gerenciando cashback
2. **Cliente (Sistema de Pedidos)**: Sistema automatizado que faz pedidos na cafeteria a cada 5 segundos
3. **Rede Docker Customizada**: Rede bridge isolada para comunicação entre os containers

### ☕ Tema: Central Perk

O sistema simula uma cafeteria onde clientes fazem pedidos que são atendidos por Gunther, o barista. Cada cliente possui um CPF único e acumula cashback de 1% em suas compras.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│              Rede: desafio1-network (bridge)                    │
│                                                                 │
│  ┌────────────────────────┐       ┌────────────────────────┐  │
│  │   web-server           │       │   web-client           │  │
│  │   (Central Perk)       │◄──────│   (Sistema Pedidos)    │  │
│  │   ☕ Flask API         │ HTTP  │   � Pedidos a cada 5s │  │
│  │   👨‍🦲 Gunther          │       │   Clientes aleatórios  │  │
│  │   Port: 8080           │       │                        │  │
│  └────────────────────────┘       └────────────────────────┘  │
│          ▲                                                      │
│          │                                                      │
└──────────┼──────────────────────────────────────────────────────┘
           │
           │ Port Mapping 8080:8080
           │
      [Host Machine]
    http://localhost:8080
```

## 🔧 Componentes Técnicos

### 1. Servidor Web - Central Perk (web-server)

**Tecnologia**: Python + Flask

**Funcionalidades**:
- **Menu Completo**: 8 itens incluindo cafés, doces e sobremesas
- **Sistema de Cashback**: 1% de cashback em cada compra
- **Cashback por CPF**: Cada cliente possui um CPF único onde o cashback é acumulado
- **Seleção Aleatória**: Sistema escolhe aleatoriamente o item e o cliente
- **Controle de Vendas**: Registra total de pedidos e vendas diárias

**Endpoints**:
- `GET /` - Fazer um pedido (seleciona item e cliente aleatoriamente)
- `GET /menu` - Visualizar cardápio completo com informações de cashback
- `GET /stats` - Estatísticas da cafeteria e saldos de cashback por CPF
- `GET /health` - Verificar status da cafeteria

**Cardápio**:
| Item | Preço | Cashback (1%) | Emoji |
|------|-------|---------------|-------|
| Espresso | $2.50 | $0.03 | ☕ |
| Cappuccino | $3.75 | $0.04 | 🍵 |
| Latte | $4.00 | $0.04 | 🥛 |
| Mocha | $4.50 | $0.05 | 🍫 |
| Frappuccino | $5.50 | $0.06 | 🥤 |
| Muffin | $3.00 | $0.03 | 🧁 |
| Cookie | $2.00 | $0.02 | 🍪 |
| Cheesecake | $4.75 | $0.05 | 🍰 |

**Clientes Cadastrados**:
| Nome | CPF |
|------|-----|
| Ross | 111.111.111-11 |
| Rachel | 222.222.222-22 |
| Monica | 333.333.333-33 |
| Chandler | 444.444.444-44 |
| Joey | 555.555.555-55 |
| Phoebe | 666.666.666-66 |

### 2. Cliente HTTP - Sistema de Pedidos (web-client)

**Tecnologia**: Shell Script + curl

**Funcionalidades**:
- Sistema automatizado que simula pedidos contínuos
- Faz requisições automáticas a cada 5 segundos
- Exibe respostas formatadas em JSON
- Logs organizados e estruturados

### 3. Rede Docker Customizada

**Nome**: `desafio1-network`  
**Tipo**: Bridge  
**Características**:
- DNS interno automático (web-client resolve "web-server")
- Isolamento completo entre containers
- Comunicação segura e eficiente

## 🎮 Como Funciona

### Fluxo de Pedido

1. **Requisição HTTP**: Cliente faz GET para `http://web-server:8080`
2. **Central Perk processa**:
   - Seleciona aleatoriamente um cliente (Ross, Rachel, Monica, Chandler, Joey ou Phoebe)
   - Seleciona aleatoriamente um item do menu
   - Calcula o cashback (1% do valor da compra)
   - Adiciona o cashback ao saldo do CPF do cliente
   - Registra a venda e incrementa estatísticas
3. **Resposta enviada**: JSON com detalhes do pedido, cliente, CPF e saldo de cashback
4. **Aguarda 5 segundos**: Cliente espera antes do próximo pedido
5. **Ciclo se repete**: Processo continua indefinidamente

### Sistema de Cashback

- **Percentual**: 1% sobre o valor de cada compra
- **Vinculação**: Cashback vinculado ao CPF do cliente
- **Acumulação**: Saldo é acumulado a cada compra
- **Consulta**: Disponível via endpoint `/stats`
- **Exemplo**: Compra de $4.00 gera $0.04 de cashback

## 📦 Estrutura de Arquivos

```
desafio1/
├── docker compose .yml          # Orquestração dos serviços
├── README.md                   # Esta documentação
├── start.sh                    # Inicia a cafeteria
├── stop.sh                     # Fecha a cafeteria
├── logs.sh                     # Visualiza pedidos em tempo real
├── test.sh                     # Testa todos os endpoints
├── .gitignore                  # Arquivos ignorados pelo Git
├── server/
│   ├── Dockerfile             # Imagem do Central Perk
│   ├── app.py                 # API Flask da cafeteria
│   └── requirements.txt       # Dependências Python
└── client/
    ├── Dockerfile             # Imagem dos clientes
    └── client.sh              # Script de pedidos automáticos
```

## 🚀 Instruções de Execução

### Pré-requisitos

- Docker 20.10+
- Docker Compose 1.29+
- Sistema: Linux, macOS ou Windows com WSL2

### Passo 1: Acessar o Projeto

```bash
cd desafio1
```

### Passo 2: Dar Permissões aos Scripts

```bash
chmod +x *.sh
```

### Passo 3: Abrir o Central Perk

```bash
./start.sh
```

**Saída esperada**:
```
☕ Iniciando Central Perk
============================================================

✅ Cafeteria iniciada com sucesso!

📋 Informações:
  🏪 Cafeteria: http://localhost:8080
  👨‍🦲 Barista: Gunther
  � Cashback: 1% em cada compra
```

### Passo 4: Ver Pedidos em Tempo Real

```bash
./logs.sh
```

**Exemplo de logs**:
```
desafio1-web-server  | ☕ CENTRAL PERK CAFETERIA
desafio1-web-server  | 🚀 Cafeteria aberta na porta 8080...
desafio1-web-server  | [2025-11-17 15:30:15] 📋 Pedido #1 | Rachel | ☕ Espresso ($2.50) | Cashback: +$0.03
desafio1-web-client  | ✅ Status: Pedido processado com sucesso
desafio1-web-server  | [2025-11-17 15:30:20] 📋 Pedido #2 | Joey | 🥤 Frappuccino ($5.50) | Cashback: +$0.06
desafio1-web-client  | ✅ Status: Pedido processado com sucesso
```

### Passo 5: Testar os Endpoints

```bash
./test.sh
```

Ou testar manualmente:

**Fazer um pedido**:
```bash
curl http://localhost:8080
```

**Ver cardápio**:
```bash
curl http://localhost:8080/menu
```

**Ver estatísticas**:
```bash
curl http://localhost:8080/stats
```

**Verificar status**:
```bash
curl http://localhost:8080/health
```

### Passo 6: Fechar a Cafeteria

```bash
./stop.sh
```

## 🧪 Exemplos de Resposta

### Exemplo 1: Pedido Normal

```json
{
  "order": {
    "number": 5,
    "item": "🍵 Cappuccino",
    "price": "$3.75",
    "status": "confirmed"
  },
  "customer": {
    "name": "Rachel",
    "cpf": "222.222.222-22",
    "cashback_earned": "$0.04",
    "cashback_balance": "$0.18"
  },
  "server_info": {
    "barista": "Gunther",
    "container": "abc123def456",
    "client_ip": "172.20.0.3",
    "timestamp": "2025-11-17 15:30:25"
  }
}
```

### Exemplo 2: Estatísticas da Cafeteria

```json
{
  "cafeteria": {
    "total_orders": 25,
    "daily_sales": "$98.75",
    "average_order": "$3.95",
    "total_cashback_distributed": "$0.99",
    "status": "open"
  },
  "customers": {
    "Ross": {
      "cpf": "111.111.111-11",
      "cashback_balance": "$0.15"
    },
    "Rachel": {
      "cpf": "222.222.222-22",
      "cashback_balance": "$0.18"
    },
    "Monica": {
      "cpf": "333.333.333-33",
      "cashback_balance": "$0.12"
    },
    "Chandler": {
      "cpf": "444.444.444-44",
      "cashback_balance": "$0.21"
    },
    "Joey": {
      "cpf": "555.555.555-55",
      "cashback_balance": "$0.19"
    },
    "Phoebe": {
      "cpf": "666.666.666-66",
      "cashback_balance": "$0.14"
    }
  },
  "server": {
    "barista": "Gunther",
    "container": "abc123def456",
    "timestamp": "2025-11-17 15:40:00"
  }
}
```

### Exemplo 3: Cardápio Completo

```json
{
  "menu": {
    "Espresso": {
      "name": "☕ Espresso",
      "price": "$2.50",
      "cashback": "$0.03 (1%)"
    },
    "Cappuccino": {
      "name": "🍵 Cappuccino",
      "price": "$3.75",
      "cashback": "$0.04 (1%)"
    },
    "Latte": {
      "name": "🥛 Latte",
      "price": "$4.00",
      "cashback": "$0.04 (1%)"
    }
  },
  "cashback_info": "Ganhe 1% de cashback em cada compra, vinculado ao seu CPF!",
  "location": "New York, NY"
}
```

## 🔧 Explicação Técnica

### Docker Compose - Orquestração dos Serviços

O arquivo `docker compose .yml` define toda a infraestrutura:

```yaml
services:
  web-server:
    build: ./server              # Constrói imagem do Dockerfile em server/
    container_name: desafio1-web-server
    ports:
      - "8080:8080"              # Expõe porta 8080 para o host
    networks:
      - desafio1-network         # Conecta à rede customizada
    
  web-client:
    build: ./client              # Constrói imagem do Dockerfile em client/
    container_name: desafio1-web-client
    depends_on:
      - web-server               # Inicia após o servidor
    networks:
      - desafio1-network         # Mesma rede que o servidor

networks:
  desafio1-network:
    driver: bridge               # Rede bridge isolada com DNS interno
```

**Pontos-chave**:
- `depends_on` garante que o servidor inicie antes do cliente
- A rede `bridge` permite que os containers se comuniquem usando nomes (ex: `http://web-server:8080`)
- DNS interno do Docker resolve automaticamente `web-server` para o IP do container

### Dockerfile do Servidor (Python + Flask)

```dockerfile
FROM python:3.11-slim            # Imagem base leve do Python

WORKDIR /app                     # Define diretório de trabalho

COPY requirements.txt .          # Copia arquivo de dependências
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .                    # Copia código da aplicação

EXPOSE 8080                      # Documenta porta exposta

CMD ["python", "app.py"]         # Comando para iniciar a API Flask
```

**Funcionamento**: Container roda a API Flask que processa pedidos, calcula cashback e mantém estado em memória.

### Dockerfile do Cliente (Alpine + Shell Script)

```dockerfile
FROM alpine:3.19                 # Imagem minimalista Linux

RUN apk add --no-cache curl bash python3   # Instala ferramentas necessárias

COPY client.sh /client.sh        # Copia script de automação
RUN chmod +x /client.sh          # Torna executável

CMD ["/client.sh"]               # Executa script em loop infinito
```

**Funcionamento**: Container executa script bash que faz requisições HTTP a cada 5 segundos para `http://web-server:8080`.

### Comunicação entre Containers

```
┌─────────────────────┐         HTTP GET          ┌─────────────────────┐
│   web-client        │  ───────────────────────>  │   web-server        │
│   (Alpine + curl)   │  <───────────────────────  │   (Python + Flask)  │
│   172.20.0.3        │      JSON Response         │   172.20.0.2:8080   │
└─────────────────────┘                            └─────────────────────┘
         │                                                    │
         └──────────────── desafio1-network ────────────────┘
                     (DNS interno resolve nomes)
```

1. Cliente chama `curl http://web-server:8080`
2. DNS interno resolve `web-server` → IP do container
3. Servidor Flask processa e retorna JSON
4. Cliente formata resposta e aguarda 5 segundos
5. Ciclo se repete

## 🔍 Comandos Úteis

```bash
# Ver containers rodando
docker ps

# Ver logs específicos
docker logs desafio1-web-server
docker logs desafio1-web-client

# Entrar no container
docker exec -it desafio1-web-server sh
docker exec -it desafio1-web-client sh

# Testar DNS interno
docker exec desafio1-web-client ping -c 2 web-server

# Ver estatísticas de recursos
docker stats desafio1-web-server desafio1-web-client

# Inspecionar rede
docker network inspect desafio1-network

# Reiniciar container específico
docker restart desafio1-web-server
```

## ⚠️ Troubleshooting

**Problema**: Porta 8080 já em uso  
**Solução**: Altere no docker compose .yml:
```yaml
ports:
  - "8081:8080"
```

**Problema**: Containers não se comunicam  
**Solução**: Verifique se estão na mesma rede:
```bash
docker network inspect desafio1-network
```

**Problema**: JSON não está formatado no cliente  
**Solução**: Verifique se python3 está instalado no Dockerfile do cliente

**Problema**: Cashback não está sendo acumulado  
**Solução**: Os dados são mantidos em memória durante a execução. Ao reiniciar os containers, o cashback é resetado (comportamento esperado para este projeto de demonstração)
