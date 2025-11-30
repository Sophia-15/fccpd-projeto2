# Desafio 3 — Docker Compose Orquestrando Serviços: Forza Garage 🏎️

## 📋 Descrição da Solução

Este projeto implementa uma **API REST de garagem de carros do Forza Horizon**, utilizando três serviços orquestrados via Docker Compose:

1. **API Web (Flask)**: API REST que gerencia um catálogo de carros de corrida
2. **Banco de Dados (PostgreSQL)**: Armazena informações detalhadas dos veículos
3. **Cache (Redis)**: Cache em memória para melhorar performance das consultas

### 🏎️ Tema: Forza Garage

O sistema simula uma garagem de carros de corrida do jogo Forza Horizon, com especificações reais de veículos high-performance. A API permite consultar carros por classe, raridade, e fornece estatísticas completas da coleção.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│              Rede: forza-network (bridge)                       │
│                                                                 │
│  ┌────────────────────────┐       ┌────────────────────────┐  │
│  │   forza-api            │──────▶│   forza-database       │  │
│  │   🐍 Flask REST API   │       │   🗄️ PostgreSQL 15     │  │
│  │   Port: 5000           │       │   Port: 5432           │  │
│  │                        │       │   DB: forza_garage     │  │
│  │   GET /cars            │       └──────────┬─────────────┘  │
│  │   GET /stats           │                  │                 │
│  │   GET /health          │                  │                 │
│  └────────┬───────────────┘       💾 forza-postgres-data      │
│           │                          (Volume Persistente)      │
│           │                                                     │
│           │               ┌────────────────────────┐          │
│           └──────────────▶│   forza-cache          │          │
│                           │   ⚡ Redis 7           │          │
│                           │   Port: 6379           │          │
│                           │   Cache: 60s TTL       │          │
│                           └────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ▲
         │ Port Mapping 5000:5000
         │
    [Host Machine]
  http://localhost:5000
```

## 🔧 Componentes Técnicos

### 1. API Web - Flask REST API (forza-api)

**Tecnologia**: Python 3.11 + Flask + psycopg2 + redis

**Funcionalidades**:
- **CRUD de Carros**: Gerencia catálogo de veículos
- **Cache Inteligente**: Redis armazena consultas por 60 segundos
- **Filtros Avançados**: Busca por classe, raridade
- **Estatísticas**: Análise completa da garagem
- **Health Check**: Monitora status de todos os serviços

**Endpoints**:
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Informações da API |
| GET | `/cars` | Lista todos os carros |
| GET | `/cars/<id>` | Busca carro por ID |
| GET | `/cars/class/<class>` | Filtra por classe (A, S1, S2, X) |
| GET | `/cars/rarity/<rarity>` | Filtra por raridade |
| GET | `/stats` | Estatísticas da garagem |
| GET | `/health` | Status dos serviços |

**Carros no Catálogo** (12 veículos):

| Fabricante | Modelo | Classe | HP | Velocidade | Raridade |
|------------|--------|--------|----|-----------| ---------|
| Bugatti | Chiron | X | 1500 | 261 mph | Legendary |
| Koenigsegg | Jesko | X | 1600 | 278 mph | Legendary |
| Ferrari | LaFerrari | S2 | 950 | 217 mph | Legendary |
| Lamborghini | Aventador SVJ | S2 | 770 | 217 mph | Epic |
| Porsche | 918 Spyder | S2 | 887 | 214 mph | Legendary |
| McLaren | P1 | S2 | 903 | 217 mph | Legendary |
| Ford | GT | S1 | 647 | 216 mph | Epic |
| Nissan | GT-R Nismo | S1 | 600 | 196 mph | Rare |
| Chevrolet | Corvette C8 Z06 | S1 | 670 | 194 mph | Rare |
| Mercedes-AMG | GT R | S1 | 577 | 198 mph | Rare |
| Audi | R8 V10 Plus | S1 | 602 | 205 mph | Rare |
| BMW | M4 Competition | A | 503 | 180 mph | Common |

**Classificação por Classe**:
- **X Class**: Hypercars extremos (1500+ HP)
- **S2 Class**: Supercars de alta performance
- **S1 Class**: Esportivos premium
- **A Class**: Esportivos de entrada

**Raridades**:
- **Legendary**: Veículos ultra-raros e exclusivos
- **Epic**: Carros de edição limitada
- **Rare**: Modelos especiais
- **Common**: Disponibilidade geral

### 2. Banco de Dados - PostgreSQL (forza-database)

**Tecnologia**: PostgreSQL 15 Alpine

**Funcionalidades**:
- **Persistência**: Volume Docker para dados permanentes
- **Schema Rico**: 10 campos por veículo
- **Indexação**: Otimizado para consultas por classe/raridade
- **Health Check**: Monitora disponibilidade

**Schema da Tabela**:
```sql
CREATE TABLE cars (
    id SERIAL PRIMARY KEY,
    manufacturer VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    class VARCHAR(50) NOT NULL,
    horsepower INTEGER NOT NULL,
    top_speed INTEGER NOT NULL,
    acceleration DECIMAL(4, 2) NOT NULL,
    price INTEGER NOT NULL,
    rarity VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos**:
- `manufacturer`: Fabricante do veículo
- `model`: Modelo específico
- `year`: Ano de fabricação
- `class`: Classificação de performance (A, S1, S2, X)
- `horsepower`: Potência em cavalos
- `top_speed`: Velocidade máxima em mph
- `acceleration`: 0-60 mph em segundos
- `price`: Valor em créditos do jogo
- `rarity`: Nível de raridade

### 3. Cache - Redis (forza-cache)

**Tecnologia**: Redis 7 Alpine

**Funcionalidades**:
- **Cache de Consultas**: Armazena resultados por 60 segundos
- **TTL Automático**: Expiração configurável
- **Redução de Carga**: Menos consultas ao banco
- **Performance**: Resposta instantânea para dados em cache

**Estratégia de Cache**:
- Consultas individuais: TTL 60s
- Listas completas: TTL 60s
- Estatísticas: TTL 30s (atualiza mais frequentemente)
- Filtros: TTL 60s por classe/raridade

**Chaves de Cache**:
- `all_cars`: Lista completa
- `car_{id}`: Carro específico
- `class_{class}`: Carros por classe
- `rarity_{rarity}`: Carros por raridade
- `garage_stats`: Estatísticas gerais

## 🎮 Como Funciona

### Fluxo de Requisição

1. **Cliente faz requisição**:
   ```
   GET http://localhost:5000/cars/class/S2
   ```

2. **API verifica cache**:
   - Consulta Redis com chave `class_S2`
   - Se encontrado: retorna imediatamente (source: cache)
   - Se não: prossegue para banco de dados

3. **Consulta ao banco** (cache miss):
   - Conecta ao PostgreSQL via psycopg2
   - Executa query filtrada: `SELECT * FROM cars WHERE class = 'S2'`
   - Processa resultados

4. **Armazena em cache**:
   - Salva JSON no Redis com TTL 60s
   - Próximas requisições usarão cache

5. **Retorna resposta**:
   ```json
   {
     "source": "database",
     "class": "S2",
     "total": 4,
     "cars": [...]
   }
   ```

### Dependências entre Serviços

```
forza-api
    │
    ├──depends_on──▶ forza-database (condition: service_healthy)
    │                    └── health check: pg_isready
    │
    └──depends_on──▶ forza-cache (condition: service_healthy)
                         └── health check: redis-cli ping
```

**Comportamento**:
- Docker Compose aguarda PostgreSQL estar pronto
- Docker Compose aguarda Redis estar pronto
- Apenas então inicia a API
- API possui retry logic adicional (30 tentativas)

### Sistema de Persistência

- **Volume PostgreSQL**: `forza-postgres-data`
- **Localização**: `/var/lib/postgresql/data`
- **Lifecycle**: Independente dos containers
- **Dados**: 12 carros pre-populados
- **Backup**: Sobrevive a `docker compose down`

## 🚀 Instruções de Execução

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Sistema: Linux, macOS ou Windows com WSL2

### Passo 1: Acessar o Projeto

```bash
cd desafio3
```

### Passo 2: Dar Permissões aos Scripts

```bash
chmod +x *.sh
```

### Passo 3: Iniciar a Garagem

```bash
./start.sh
```

**Saída esperada**:
```
Iniciando Desafio 3 - Forza Garage
==================================================
Construindo imagens Docker...
[+] Building 12.5s

Iniciando servicos...
[+] Running 4/4
 ✔ Network forza-network       Created
 ✔ Volume forza-postgres-data  Created
 ✔ Container forza-database    Healthy
 ✔ Container forza-cache       Healthy
 ✔ Container forza-api         Started

Servicos iniciados!

Status dos containers:
NAME              IMAGE              STATUS
forza-database    postgres:15-alpine healthy
forza-cache       redis:7-alpine     healthy
forza-api         desafio3-api       Up

==================================================
Forza Garage rodando!
==================================================

API disponivel em: http://localhost:5000
```

### Passo 4: Testar os Endpoints

```bash
./test.sh
```

Este script testa automaticamente:
1. Endpoint raiz (/)
2. Health check (/health)
3. Lista de carros (/cars)
4. Busca por ID (/cars/1)
5. Filtro por classe (/cars/class/S2)
6. Filtro por raridade (/cars/rarity/Legendary)
7. Estatísticas (/stats)
8. Cache (segunda requisição)

**Ou testar manualmente**:

```bash
# Listar todos os carros
curl http://localhost:5000/cars | python3 -m json.tool

# Buscar carro específico
curl http://localhost:5000/cars/1 | python3 -m json.tool

# Carros classe S2
curl http://localhost:5000/cars/class/S2 | python3 -m json.tool

# Carros Legendary
curl http://localhost:5000/cars/rarity/Legendary | python3 -m json.tool

# Estatísticas
curl http://localhost:5000/stats | python3 -m json.tool

# Health check
curl http://localhost:5000/health | python3 -m json.tool
```

### Passo 5: Ver Logs

```bash
./logs.sh
```

### Passo 6: Parar os Serviços

```bash
./stop.sh
```

## 🧪 Exemplos de Saída

### Exemplo 1: Listar Carros (/cars)

```json
{
  "source": "database",
  "total": 12,
  "cars": [
    {
      "id": 6,
      "manufacturer": "Audi",
      "model": "R8 V10 Plus",
      "year": 2020,
      "class": "S1",
      "horsepower": 602,
      "top_speed": 205,
      "acceleration": 3.1,
      "price": 195000,
      "rarity": "Rare",
      "created_at": "2025-11-19 10:30:15.123456"
    },
    {
      "id": 10,
      "manufacturer": "BMW",
      "model": "M4 Competition",
      "year": 2021,
      "class": "A",
      "horsepower": 503,
      "top_speed": 180,
      "acceleration": 3.5,
      "price": 75000,
      "rarity": "Common",
      "created_at": "2025-11-19 10:30:15.234567"
    }
  ]
}
```

### Exemplo 2: Carros por Classe (/cars/class/X)

```json
{
  "source": "database",
  "class": "X",
  "total": 2,
  "cars": [
    {
      "id": 6,
      "manufacturer": "Koenigsegg",
      "model": "Jesko",
      "year": 2020,
      "class": "X",
      "horsepower": 1600,
      "top_speed": 278,
      "acceleration": 2.5,
      "price": 2800000,
      "rarity": "Legendary",
      "created_at": "2025-11-19 10:30:15.345678"
    },
    {
      "id": 5,
      "manufacturer": "Bugatti",
      "model": "Chiron",
      "year": 2018,
      "class": "X",
      "horsepower": 1500,
      "top_speed": 261,
      "acceleration": 2.3,
      "price": 3000000,
      "rarity": "Legendary",
      "created_at": "2025-11-19 10:30:15.456789"
    }
  ]
}
```

### Exemplo 3: Estatísticas (/stats)

```json
{
  "source": "database",
  "stats": {
    "total_cars": 12,
    "average_horsepower": 772.42,
    "average_price": 992916.67,
    "max_top_speed": 278,
    "best_acceleration": 2.2,
    "cars_by_class": [
      {"class": "S1", "count": 5},
      {"class": "S2", "count": 4},
      {"class": "X", "count": 2},
      {"class": "A", "count": 1}
    ],
    "cars_by_rarity": [
      {"rarity": "Legendary", "count": 5},
      {"rarity": "Rare", "count": 4},
      {"rarity": "Epic", "count": 2},
      {"rarity": "Common", "count": 1}
    ]
  }
}
```

### Exemplo 4: Health Check (/health)

```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected"
}
```

### Exemplo 5: Demonstração de Cache

**Primeira requisição** (cache miss):
```json
{
  "source": "database",
  "stats": {...}
}
```

**Segunda requisição** (cache hit - em até 30 segundos):
```json
{
  "source": "cache",
  "stats": {...}
}
```

## 🔧 Explicação Técnica

### Docker Compose - Orquestração Completa

O arquivo `docker-compose.yml` orquestra os 3 serviços.

**Pontos-chave**:
- **depends_on com condition**: API só inicia após DB e cache estarem prontos
- **healthcheck**: Garante disponibilidade antes de prosseguir
- **environment**: Variáveis de ambiente para configuração
- **networks**: Todos na mesma rede para comunicação
- **volumes**: Persistência de dados do PostgreSQL

### Dockerfile da API

**Funcionamento**: Imagem Python leve com Flask, psycopg2 e redis instalados.

### Comunicação entre Serviços

```
┌─────────────────────┐
│    forza-api        │
│                     │
│  1. Consulta cache  │──────▶ redis://forza-cache:6379
│                     │◀────── PONG / cache hit/miss
│                     │
│  2. Query database  │──────▶ postgres://forza-database:5432
│                     │◀────── ResultSet
│                     │
│  3. Atualiza cache  │──────▶ redis://forza-cache:6379
│                     │◀────── OK
│                     │
│  4. Retorna JSON    │──────▶ HTTP Response
└─────────────────────┘
```

### Variáveis de Ambiente

A API recebe configurações via environment:
- `DB_HOST=postgres`: Nome do serviço no compose
- `DB_PORT=5432`: Porta padrão PostgreSQL
- `REDIS_HOST=redis`: Nome do serviço Redis
- `REDIS_PORT=6379`: Porta padrão Redis

DNS interno do Docker resolve nomes para IPs automaticamente.

### Health Checks

**PostgreSQL**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
```
Verifica se o banco aceita conexões.

**Redis**:
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
```
Verifica se o Redis responde com PONG.

**API**:
```python
@app.route('/health')
def health():
    conn = get_db_connection()
    cache.ping()
    return {'status': 'healthy'}
```
Endpoint que valida todos os serviços.

