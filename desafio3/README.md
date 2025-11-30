# Desafio 3 — Docker Compose Orquestrando Serviços: Forza Garage 🏎️

## 1. Descrição Geral da Solução

### 1.1 Proposta do Desafio

Este desafio demonstra a **orquestração de múltiplos serviços com Docker Compose**, explorando a integração entre uma API web, banco de dados relacional e sistema de cache em memória. O objetivo é construir uma aplicação completa que utiliza três containers distintos trabalhando de forma coordenada, com dependências explícitas, health checks e volumes persistentes.

A implementação aborda conceitos avançados de Docker: orquestração declarativa via docker-compose.yml, gerenciamento de dependências entre serviços, health checks para garantir disponibilidade, estratégias de cache para otimizar performance e persistência de dados em volumes.

### 1.2 Arquitetura Utilizada

A solução é composta por **quatro componentes principais**:

**1. Container API Web (forza-api)**
- **Imagem base**: Python 3.11-slim (custom build)
- **Framework**: Flask (servidor HTTP) + psycopg2 (PostgreSQL) + redis-py (Redis)
- **Função**: API REST completa que gerencia garagem de carros de corrida
- **Porta exposta**: 5000 (mapeada para host)
- **Dependências**: Aguarda PostgreSQL e Redis ficarem `healthy` antes de iniciar

**2. Container PostgreSQL (forza-database)**
- **Imagem**: postgres:15-alpine (oficial)
- **Função**: Banco de dados relacional que armazena catálogo de 12 carros
- **Porta interna**: 5432 (não exposta ao host)
- **Volume persistente**: `forza-postgres-data` montado em `/var/lib/postgresql/data`
- **Health check**: `pg_isready -U postgres` a cada 5 segundos

**3. Container Redis (forza-cache)**
- **Imagem**: redis:7-alpine (oficial)
- **Função**: Cache em memória para otimizar consultas repetidas
- **Porta interna**: 6379 (não exposta ao host)
- **TTL**: 60 segundos para resultados de queries
- **Health check**: `redis-cli ping` a cada 5 segundos

**4. Volume Docker (forza-postgres-data)**
- **Tipo**: Volume nomeado (driver local)
- **Propósito**: Persistir dados do PostgreSQL
- **Sobrevive**: A remoção de containers (`docker-compose down`)

**5. Rede Docker (forza-network)**
- **Tipo**: Bridge customizada
- **DNS interno**: Resolve nomes (postgres, redis, api)
- **Isolamento**: Apenas containers nesta rede se comunicam

### 1.3 Decisões Técnicas e Justificativas

**Por que Flask + psycopg2 + redis-py?**
Flask é ideal para APIs REST minimalistas. Psycopg2 é o driver PostgreSQL mais maduro e performático para Python. Redis-py é a biblioteca oficial para Redis, com API simples e suporte completo a TTL e expiração automática.

**Por que Redis para cache?**
Redis é um cache in-memory extremamente rápido (< 1ms de latência). Suporta TTL automático, expirando dados antigos sem intervenção manual. É mais adequado que cache em memória Python (que seria perdido a cada restart) e mais leve que Memcached para este caso de uso.

**Por que PostgreSQL Alpine?**
A versão Alpine (~80MB) é significativamente menor que a padrão (~350MB), reduzindo tempo de build e uso de disco. Mantém todas as funcionalidades necessárias para este projeto.

**Por que health checks com `condition: service_healthy`?**
`depends_on` simples apenas garante ordem de start, mas não espera o serviço estar operacional. Health checks + `condition: service_healthy` garantem que PostgreSQL e Redis estão **realmente prontos** antes da API tentar conectar, evitando falhas de conexão no startup.

**Por que TTL de 60 segundos no cache?**
É um balanço entre performance (dados em cache respondem instantaneamente) e atualização (dados não ficam obsoletos por muito tempo). Para estatísticas, o TTL é reduzido para 30s pois mudam mais frequentemente.

**Por que NÃO expor portas do PostgreSQL e Redis?**
Apenas a API precisa ser acessada externamente. Manter PostgreSQL e Redis apenas na rede interna é uma **best practice de segurança**: reduz superfície de ataque, evita acessos não autorizados e previne conflitos de porta no host.

**Organização do projeto:**
```
desafio3/
├── docker-compose.yml          # Orquestração (3 serviços + volume + rede)
├── Dockerfile                  # Build da API Flask
├── start.sh, stop.sh, logs.sh  # Scripts de gerenciamento
├── test.sh                     # Testa todos os endpoints
└── api/
    ├── app.py                  # API Flask completa
    └── requirements.txt        # Flask, psycopg2-binary, redis
```

### 1.4 Tema: Forza Garage

O sistema gerencia uma **garagem de carros de corrida do Forza Horizon**:

**12 Carros Cadastrados:**
- **X Class**: Bugatti Chiron (1500 HP, 261 mph), Koenigsegg Jesko (1600 HP, 278 mph)
- **S2 Class**: Ferrari LaFerrari (950 HP), Lamborghini Aventador SVJ (770 HP), Porsche 918 Spyder (887 HP), McLaren P1 (903 HP)
- **S1 Class**: Ford GT (647 HP), Nissan GT-R Nismo (600 HP), Chevrolet Corvette Z06 (670 HP), Mercedes-AMG GT R (577 HP), Audi R8 V10 Plus (602 HP)
- **A Class**: BMW M4 Competition (503 HP)

**Classificação:**
- **Classe**: A (esportivos), S1 (alta performance), S2 (supercars), X (hypercars)
- **Raridade**: Common, Rare, Epic, Legendary

**10 Campos por Veículo:**
Fabricante, modelo, ano, classe, potência, velocidade máxima, aceleração (0-60mph), preço, raridade, timestamp de criação.

## 2. Explicação Detalhada do Funcionamento

### 2.1 Fluxo Completo de Inicialização

**1. Docker Compose Analisa docker-compose.yml:**
```bash
docker-compose up -d
```

**2. Ordem de Inicialização (definida por `depends_on` + `condition`):**

```
┌─ FASE 1: Inicialização Paralela ─┐
│  postgres (com healthcheck)       │
│  redis (com healthcheck)          │
└───────────┬───────────────────────┘
            │ (aguarda ambos ficarem healthy)
            ↓
┌─ FASE 2: API Inicia ─────────────┐
│  forza-api                        │
│  (depende de postgres + redis)    │
└───────────────────────────────────┘
```

**3. PostgreSQL Inicializa:**
- Container `forza-database` sobe
- PostgreSQL monta volume `forza-postgres-data` em `/var/lib/postgresql/data`
- Se é primeira vez: cria estrutura do banco
- Se volume existe: carrega dados existentes
- Health check executa `pg_isready -U postgres` a cada 5s
- Após 5 checks bem-sucedidos consecutivos: status = `healthy`

**4. Redis Inicializa:**
- Container `forza-cache` sobe
- Redis inicia em memória (sem persistência)
- Health check executa `redis-cli ping` a cada 5s
- Resposta `PONG`: incrementa contador de sucesso
- Após 5 PONGs consecutivos: status = `healthy`

**5. API Flask Inicializa:**
- Aguarda PostgreSQL E Redis ficarem `healthy`
- Container `forza-api` sobe
- Flask app inicia na porta 5000
- Função `init_database()` executa:
  - Conecta ao PostgreSQL com retry logic (30 tentativas)
  - Cria tabela `cars` se não existir
  - Verifica se tabela está vazia
  - Se vazia: popula com 12 carros
  - Se já tem dados: reutiliza existentes
- API fica disponível em `http://localhost:5000`

### 2.2 API Flask - Arquitetura Interna

**Estrutura de Conexões:**

```python
# Conexão PostgreSQL (com retry logic)
def get_db_connection():
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host="postgres",  # DNS interno
                port="5432",
                database="forza_garage",
                user="postgres",
                password="postgres"
            )
            return conn
        except psycopg2.OperationalError:
            retry_count += 1
            time.sleep(1)
    
    raise Exception("PostgreSQL unavailable after 30 attempts")

# Conexão Redis (global)
cache = redis.Redis(
    host="redis",  # DNS interno
    port=6379,
    decode_responses=True  # Retorna strings, não bytes
)
```

**Por que retry logic?**
Mesmo com health check, pode haver um delay entre "accepting connections" e "fully operational". Retry logic adiciona robustez.

### 2.3 Sistema de Cache - Estratégia de Implementação

**Como o cache funciona:**

**Exemplo 1: Listar todos os carros (`GET /cars`)**

```python
@app.route("/cars")
def get_cars():
    cache_key = "all_cars"
    
    # 1. TENTA BUSCAR NO CACHE
    cached = cache.get(cache_key)
    if cached:
        return jsonify({
            "source": "cache",
            "cars": json.loads(cached)
        })
    
    # 2. CACHE MISS - BUSCA NO BANCO
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars ORDER BY manufacturer, model")
    
    # 3. PROCESSA RESULTADOS
    cars = []
    column_names = [desc[0] for desc in cursor.description]
    for row in cursor.fetchall():
        car = dict(zip(column_names, row))
        # Converte tipos para JSON-serializável
        car["created_at"] = str(car["created_at"])
        car["acceleration"] = float(car["acceleration"])
        car["price"] = int(car["price"])
        cars.append(car)
    
    cursor.close()
    conn.close()
    
    # 4. ARMAZENA NO CACHE (TTL 60 segundos)
    cache.setex(cache_key, 60, json.dumps(cars))
    
    # 5. RETORNA RESULTADO
    return jsonify({
        "source": "database",
        "total": len(cars),
        "cars": cars
    })
```

**Fluxo visual:**

```
Requisição → API Flask
              │
              ├─→ Redis.get("all_cars")
              │   │
              │   ├─→ HIT: Retorna imediatamente (source: cache)
              │   │
              │   └─→ MISS: Continua ↓
              │
              ├─→ PostgreSQL.query("SELECT * FROM cars")
              │
              ├─→ Processa resultados
              │
              ├─→ Redis.setex("all_cars", 60, json_data)
              │
              └─→ Retorna resposta (source: database)
```

**Exemplo 2: Buscar carro por classe (`GET /cars/class/S2`)**

```python
@app.route("/cars/class/<car_class>")
def get_cars_by_class(car_class):
    cache_key = f"class_{car_class}"  # Chave: "class_S2"
    
    cached = cache.get(cache_key)
    if cached:
        return jsonify({
            "source": "cache",
            "class": car_class,
            "cars": json.loads(cached)
        })
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cars WHERE class = %s ORDER BY horsepower DESC",
        (car_class,)
    )
    
    # ... processamento ...
    
    cache.setex(cache_key, 60, json.dumps(cars))
    
    return jsonify({
        "source": "database",
        "class": car_class,
        "total": len(cars),
        "cars": cars
    })
```

**Chaves de cache usadas:**
- `all_cars`: Lista completa (TTL 60s)
- `car_{id}`: Carro específico (ex: `car_1`, TTL 60s)
- `class_{class}`: Carros por classe (ex: `class_S2`, TTL 60s)
- `rarity_{rarity}`: Carros por raridade (ex: `rarity_Legendary`, TTL 60s)
- `garage_stats`: Estatísticas (TTL 30s - atualiza mais rápido)

**Benefícios do cache:**
- **Performance**: Requisições em cache respondem em < 1ms (vs 50-100ms do PostgreSQL)
- **Reduz carga**: Menos queries no banco de dados
- **Escalabilidade**: Suporta mais requisições simultâneas

### 2.4 Endpoints da API - Detalhamento Completo

**1. `GET /` - Informações da API**
```bash
curl http://localhost:5000/
```
```json
{
  "service": "Forza Garage API",
  "version": "1.0",
  "endpoints": {
    "/": "Service info",
    "/cars": "List all cars",
    "/cars/<id>": "Get car by ID",
    "/cars/class/<class>": "Get cars by class",
    "/cars/rarity/<rarity>": "Get cars by rarity",
    "/stats": "Garage statistics",
    "/health": "Health check"
  }
}
```

**2. `GET /cars` - Listar todos os carros**
```bash
curl http://localhost:5000/cars
```
```json
{
  "source": "database",  // ou "cache" se estava em cache
  "total": 12,
  "cars": [
    {
      "id": 1,
      "manufacturer": "Ferrari",
      "model": "LaFerrari",
      "year": 2013,
      "class": "S2",
      "horsepower": 950,
      "top_speed": 217,
      "acceleration": 2.4,
      "price": 1500000,
      "rarity": "Legendary",
      "created_at": "2025-11-30 14:30:00"
    },
    // ... outros 11 carros
  ]
}
```

**3. `GET /cars/<id>` - Buscar carro específico**
```bash
curl http://localhost:5000/cars/5
```
```json
{
  "source": "cache",
  "car": {
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
    "created_at": "2025-11-30 14:30:00"
  }
}
```

**4. `GET /cars/class/<class>` - Filtrar por classe**
```bash
curl http://localhost:5000/cars/class/S2
```
```json
{
  "source": "database",
  "class": "S2",
  "total": 4,
  "cars": [
    {
      "manufacturer": "McLaren",
      "model": "P1",
      "horsepower": 903,
      "class": "S2"
    },
    // ... outros carros S2 ordenados por HP
  ]
}
```

**Classes válidas:** A, S1, S2, X

**5. `GET /cars/rarity/<rarity>` - Filtrar por raridade**
```bash
curl http://localhost:5000/cars/rarity/Legendary
```
```json
{
  "source": "cache",
  "rarity": "Legendary",
  "total": 6,
  "cars": [
    // Carros raros ordenados por preço
  ]
}
```

**Raridades válidas:** Common, Rare, Epic, Legendary

**6. `GET /stats` - Estatísticas da garagem**
```bash
curl http://localhost:5000/stats
```
```json
{
  "source": "database",
  "total_cars": 12,
  "total_horsepower": 9529,
  "average_horsepower": 794.08,
  "total_value": 11534000,
  "average_price": 961166.67,
  "fastest_car": {
    "manufacturer": "Koenigsegg",
    "model": "Jesko",
    "top_speed": 278
  },
  "most_powerful": {
    "manufacturer": "Koenigsegg",
    "model": "Jesko",
    "horsepower": 1600
  },
  "by_class": {
    "A": 1,
    "S1": 5,
    "S2": 4,
    "X": 2
  },
  "by_rarity": {
    "Common": 1,
    "Rare": 5,
    "Epic": 2,
    "Legendary": 6
  }
}
```

**7. `GET /health` - Health check**
```bash
curl http://localhost:5000/health
```
```json
{
  "status": "healthy",
  "api": "running",
  "database": {
    "status": "connected",
    "total_cars": 12
  },
  "cache": {
    "status": "connected",
    "redis_version": "7.2.3"
  },
  "timestamp": "2025-11-30T14:35:22"
}
```

**Verifica:**
- API está respondendo
- PostgreSQL está acessível (tenta query simples)
- Redis está acessível (tenta ping)

### 2.5 Comunicação entre Containers

**Rede Docker (forza-network):**

```
Container         IP interno        Portas
─────────────────────────────────────────
forza-api         172.20.0.4        5000 (mapeada para host)
forza-database    172.20.0.2        5432 (apenas interna)
forza-cache       172.20.0.3        6379 (apenas interna)
```

**Como funciona a comunicação:**

**API → PostgreSQL:**
```python
# No código Python da API:
conn = psycopg2.connect(host="postgres", port="5432", ...)
```
1. DNS interno resolve "postgres" → IP do container `forza-database`
2. Conexão é roteada pela bridge `forza-network`
3. PostgreSQL recebe conexão na porta 5432

**API → Redis:**
```python
cache = redis.Redis(host="redis", port=6379)
cache.get("all_cars")
```
1. DNS interno resolve "redis" → IP do container `forza-cache`
2. Comando GET é enviado via protocolo Redis
3. Redis retorna valor (ou nil se não existir)

**Host → API:**
```bash
curl http://localhost:5000/cars
```
1. Requisição chega em `localhost:5000` do host
2. Docker mapeia para `172.20.0.4:5000` (IP interno da API)
3. Flask recebe e processa requisição

**Por que PostgreSQL e Redis NÃO têm port mapping:**
Apenas a API precisa ser acessada externamente. Manter bancos e cache isolados na rede interna é seguro e evita conflitos.

### 2.6 Persistência com Volume Docker

**Volume configurado:**
```yaml
volumes:
  postgres-data:
    name: forza-postgres-data
    driver: local
```

**Montagem no container:**
```yaml
postgres:
  volumes:
    - postgres-data:/var/lib/postgresql/data
```

**Como funciona:**

**Primeira execução:**
1. Volume `forza-postgres-data` não existe → Docker cria
2. PostgreSQL inicializa banco vazio em `/var/lib/postgresql/data`
3. API popula com 12 carros
4. Dados são gravados no volume (no host)

**Após `docker-compose down`:**
1. Containers são removidos
2. Volume **permanece intacto**
3. Dados estão salvos em `/var/lib/docker/volumes/forza-postgres-data/_data`

**Próxima execução (`docker-compose up`):**
1. Containers são recriados
2. PostgreSQL monta volume existente
3. Dados já estão lá!
4. API detecta 12 carros existentes → não reinsere

**Testar persistência:**
```bash
# 1. Subir sistema
docker-compose up -d

# 2. Verificar dados
curl http://localhost:5000/cars | jq '.total'
# 12

# 3. Parar e remover containers
docker-compose down

# 4. Subir novamente
docker-compose up -d

# 5. Verificar dados ainda existem
curl http://localhost:5000/cars | jq '.total'
# 12 ✅
```

### 2.7 Health Checks e Dependências

**PostgreSQL Health Check:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 5s
  timeout: 5s
  retries: 5
```

**Como funciona:**
- A cada 5s, executa `pg_isready -U postgres`
- Se retorna exit code 0: sucesso
- Após 5 sucessos consecutivos: status = `healthy`
- Se falha 5 vezes: status = `unhealthy`

**Redis Health Check:**
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 3s
  retries: 5
```

**Como funciona:**
- A cada 5s, executa `redis-cli ping`
- Resposta esperada: "PONG"
- Após 5 PONGs: status = `healthy`

**Dependências da API:**
```yaml
api:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
```

**O que isso garante:**
- API só inicia após PostgreSQL E Redis ficarem `healthy`
- Evita erros de "connection refused" no startup
- Sistema sobe de forma ordenada e confiável

### 2.8 Logs e Observabilidade

**Logs esperados - PostgreSQL:**
```
LOG:  database system was shut down at 2025-11-30 14:20:00 UTC
LOG:  database system is ready to accept connections
```

**Logs esperados - Redis:**
```
* Ready to accept connections tcp
* Running mode=standalone, port=6379
```

**Logs esperados - API Flask:**
```
🏎️  FORZA GARAGE - Initializing...
✅ Connected to PostgreSQL successfully
✅ Database initialized
ℹ️  Found 12 cars in database
✅ Connected to Redis cache
🚀 API running on http://0.0.0.0:5000

[request logs]
172.20.0.1 - - [30/Nov/2025 14:30:00] "GET /cars HTTP/1.1" 200 -
Cache HIT: all_cars
172.20.0.1 - - [30/Nov/2025 14:30:05] "GET /cars HTTP/1.1" 200 -
```

**Visualizar logs:**
```bash
# Todos os serviços
docker-compose logs

# Apenas API
docker-compose logs api

# Logs em tempo real
docker-compose logs -f

# Últimas 50 linhas
docker-compose logs --tail=50
```

## 3. Instruções de Execução – Passo a Passo

### 3.1 Pré-requisitos

**Software necessário:**
- Docker Engine 20.10 ou superior
- Docker Compose 1.29 ou superior (ou Compose V2)
- Sistema operacional: Linux, macOS ou Windows com WSL2

**Verificar instalação:**
```bash
docker --version
docker-compose --version
```

### 3.2 Preparação do Ambiente

**1. Navegar até o diretório:**
```bash
cd /caminho/para/desafio3
```

**2. Verificar estrutura:**
```bash
ls -la
# Deve conter: docker-compose.yml, Dockerfile, api/, *.sh
```

**3. Tornar scripts executáveis:**
```bash
chmod +x *.sh
```

### 3.3 Construir e Iniciar Sistema

**Opção 1: Script automatizado (recomendado)**
```bash
./start.sh
```

**Opção 2: Comandos manuais**
```bash
# Build da imagem da API
docker-compose build

# Subir todos os serviços
docker-compose up -d
```

**Saída esperada:**
```
Creating network "forza-network" with driver "bridge"
Creating volume "forza-postgres-data" with driver "local"
Creating forza-database ... done
Creating forza-cache ... done
Waiting for postgres to be healthy...
Waiting for redis to be healthy...
Creating forza-api ... done

🏎️  Forza Garage iniciado com sucesso!
🌐 API: http://localhost:5000
💾 Volume: forza-postgres-data
📊 Verificando status...
```

**Verificar containers:**
```bash
docker-compose ps
```

**Saída esperada:**
```
NAME            STATUS                    PORTS
forza-api       Up                        0.0.0.0:5000->5000/tcp
forza-database  Up (healthy)              5432/tcp
forza-cache     Up (healthy)              6379/tcp
```

### 3.4 Testar Endpoints da API

**1. Informações da API:**
```bash
curl http://localhost:5000/
```

**2. Listar todos os carros (primeira vez - database):**
```bash
curl http://localhost:5000/cars
```

**Resposta:**
```json
{
  "source": "database",
  "total": 12,
  "cars": [...]
}
```

**3. Listar todos os carros (segunda vez - cache):**
```bash
curl http://localhost:5000/cars
```

**Resposta:**
```json
{
  "source": "cache",  // ✅ Agora vem do cache!
  "cars": [...]
}
```

**4. Buscar carro específico:**
```bash
curl http://localhost:5000/cars/1
```

**5. Filtrar por classe S2:**
```bash
curl http://localhost:5000/cars/class/S2
```

**6. Filtrar por raridade Legendary:**
```bash
curl http://localhost:5000/cars/rarity/Legendary
```

**7. Estatísticas da garagem:**
```bash
curl http://localhost:5000/stats
```

**8. Health check:**
```bash
curl http://localhost:5000/health
```

### 3.5 Testar Sistema de Cache

**Verificar comportamento do cache:**

**Primeira requisição (cache miss):**
```bash
time curl -s http://localhost:5000/cars/class/X | jq '.source'
# "database"
# real    0m0.085s  (busca no banco leva ~80ms)
```

**Segunda requisição (cache hit):**
```bash
time curl -s http://localhost:5000/cars/class/X | jq '.source'
# "cache"
# real    0m0.012s  (cache retorna em ~10ms)
```

**Aguardar expiração do cache (60 segundos):**
```bash
sleep 61
time curl -s http://localhost:5000/cars/class/X | jq '.source'
# "database"  (cache expirou, busca no banco novamente)
```

**Inspecionar Redis diretamente:**
```bash
docker exec -it forza-cache redis-cli

# No Redis CLI:
KEYS *
# 1) "all_cars"
# 2) "class_S2"
# 3) "car_1"

GET all_cars
# (retorna JSON dos carros)

TTL all_cars
# (retorna segundos restantes até expirar)

# Sair
exit
```

### 3.6 Verificar Logs em Tempo Real

**Logs combinados (todos os serviços):**
```bash
./logs.sh
# OU manualmente:
docker-compose logs -f
```

**Logs apenas da API:**
```bash
docker-compose logs -f api
```

**Exemplo de saída:**
```
forza-api | 🏎️  FORZA GARAGE - Initializing...
forza-api | ✅ Connected to PostgreSQL
forza-api | ✅ Database has 12 cars
forza-api | ✅ Connected to Redis cache
forza-api | 🚀 API running on http://0.0.0.0:5000
forza-api | 
forza-api | 172.20.0.1 - - [30/Nov/2025 14:30:15] "GET /cars HTTP/1.1" 200 -
forza-api | 💾 Database query: SELECT * FROM cars
forza-api | 
forza-api | 172.20.0.1 - - [30/Nov/2025 14:30:20] "GET /cars HTTP/1.1" 200 -
forza-api | ⚡ Cache HIT: all_cars
```

**Logs do PostgreSQL:**
```bash
docker-compose logs postgres
```

**Logs do Redis:**
```bash
docker-compose logs redis
```

### 3.7 Testar Todos os Endpoints Automaticamente

**Executar script de testes:**
```bash
./test.sh
```

**O script testa:**
1. `GET /` - Info da API
2. `GET /cars` - Lista completa
3. `GET /cars/1` - Carro específico
4. `GET /cars/class/S2` - Filtro por classe
5. `GET /cars/class/X` - Filtro hypercars
6. `GET /cars/rarity/Legendary` - Filtro por raridade
7. `GET /stats` - Estatísticas
8. `GET /health` - Health check

**Verifica:**
- Todos retornam HTTP 200
- Respostas contêm dados esperados
- Cache está funcionando (segunda requisição vem do cache)

### 3.8 Acessar Banco de Dados Diretamente

**Entrar no PostgreSQL:**
```bash
docker exec -it forza-database psql -U postgres -d forza_garage
```

**Comandos úteis no psql:**
```sql
-- Listar tabelas
\dt

-- Ver estrutura da tabela cars
\d cars

-- Contar carros
SELECT COUNT(*) FROM cars;

-- Listar carros por classe
SELECT manufacturer, model, class, horsepower, top_speed
FROM cars
ORDER BY class, horsepower DESC;

-- Estatísticas rápidas
SELECT 
    class,
    COUNT(*) as total,
    AVG(horsepower) as avg_hp,
    MAX(top_speed) as max_speed
FROM cars
GROUP BY class
ORDER BY class;

-- Carro mais rápido
SELECT manufacturer, model, top_speed
FROM cars
ORDER BY top_speed DESC
LIMIT 1;

-- Sair
\q
```

### 3.9 Testar Persistência de Dados

**Cenário: Dados devem sobreviver a remoção de containers**

**1. Verificar dados atuais:**
```bash
curl -s http://localhost:5000/stats | jq '.total_cars'
# 12
```

**2. Parar e remover containers:**
```bash
docker-compose down
# Stopping forza-api ... done
# Stopping forza-cache ... done
# Stopping forza-database ... done
# Removing forza-api ... done
# Removing forza-cache ... done
# Removing forza-database ... done
# Removing network forza-network
```

**3. Verificar que volume ainda existe:**
```bash
docker volume ls | grep forza
# local     forza-postgres-data  ✅
```

**4. Inspecionar volume:**
```bash
docker volume inspect forza-postgres-data
```

**5. Subir sistema novamente:**
```bash
docker-compose up -d
```

**6. Verificar que dados persistiram:**
```bash
# Aguardar API inicializar (5-10 segundos)
sleep 10

curl -s http://localhost:5000/stats | jq '.total_cars'
# 12  ✅ Dados ainda estão lá!
```

**7. Verificar logs da API:**
```bash
docker-compose logs api | grep "Found"
# ℹ️  Found 12 cars in database  (não reinseriu!)
```

### 3.10 Monitorar Performance do Cache

**Ver hits e misses do cache:**

```bash
# Limpar cache existente
docker exec -it forza-cache redis-cli FLUSHALL

# Fazer 3 requisições iguais
for i in {1..3}; do
  echo "Requisição $i:"
  curl -s http://localhost:5000/cars/class/S2 | jq '.source'
  sleep 1
done
```

**Saída esperada:**
```
Requisição 1:
"database"  (cache miss - busca no banco)

Requisição 2:
"cache"  (cache hit - retorna do Redis)

Requisição 3:
"cache"  (cache hit - retorna do Redis)
```

**Inspecionar estatísticas do Redis:**
```bash
docker exec -it forza-cache redis-cli INFO stats
```

### 3.11 Limpar e Reiniciar

**Opção 1: Parar containers (mantém volume):**
```bash
./stop.sh
# OU:
docker-compose down
```

**Opção 2: Parar e remover volume (limpa tudo):**
```bash
docker-compose down -v
```

**Opção 3: Rebuild completo:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### 3.12 Troubleshooting

**Problema: API não conecta ao PostgreSQL**
```bash
# Verificar health check do PostgreSQL
docker-compose ps
# Se não está healthy, ver logs:
docker-compose logs postgres

# Verificar conectividade
docker exec -it forza-api ping postgres
```

**Problema: Cache não funciona**
```bash
# Verificar Redis está rodando
docker exec -it forza-cache redis-cli ping
# Deve retornar: PONG

# Ver logs do Redis
docker-compose logs redis
```

**Problema: Porta 5000 já está em uso**
```bash
# Alterar porta no docker-compose.yml:
ports:
  - "5001:5000"  # host:container

# Acessar em: http://localhost:5001
```

**Problema: Containers não iniciam**
```bash
# Ver logs detalhados
docker-compose logs --tail=100

# Verificar status
docker-compose ps -a

# Rebuild do zero
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

---

## Observações Finais

**✅ Orquestração Completa:**
Docker Compose gerencia 3 containers interdependentes com health checks, garantindo inicialização ordenada e confiável.

**✅ Sistema de Cache:**
Redis reduz latência de requisições repetidas de ~80ms (banco) para ~10ms (cache), melhorando performance significativamente.

**✅ Persistência Garantida:**
Volume `forza-postgres-data` mantém dados do PostgreSQL mesmo após `docker-compose down`, demonstrando persistência real.

**✅ Health Checks:**
`condition: service_healthy` garante que dependências estão realmente operacionais antes de iniciar serviços dependentes.

**✅ Isolamento de Rede:**
PostgreSQL e Redis ficam isolados na rede interna, apenas API é exposta - segurança por design.

**✅ TTL Automático:**
Cache expira automaticamente após 60 segundos, mantendo dados atualizados sem intervenção manual.

**✅ Retry Logic:**
Conexões ao banco implementam retry logic para lidar com delays de inicialização de forma robusta.

**✅ Source Tracking:**
Respostas da API indicam se dados vieram do cache ou banco (`"source": "cache"` ou `"database"`), facilitando debug.
