# Desafio 4 — Microsserviços Independentes: Forza Garage 🏁

## 1. Descrição Geral da Solução

### 1.1 Proposta do Desafio

Este desafio demonstra a **arquitetura de microsserviços independentes com comunicação HTTP entre serviços**. O objetivo é construir dois microsserviços autônomos onde um consome dados do outro via requisições HTTP, sem necessidade de gateway intermediário, ilustrando os princípios fundamentais de arquiteturas distribuídas.

A implementação explora conceitos essenciais de microsserviços: separação de responsabilidades (SoC - Separation of Concerns), comunicação síncrona via HTTP/REST, descoberta de serviços via DNS interno Docker, tratamento de falhas de comunicação e independência de deploy.

### 1.2 Arquitetura Utilizada

A solução é composta por **três componentes principais**:

**1. Garage Service (Microsserviço A - Provider)**
- **Imagem base**: Python 3.11-slim (custom build)
- **Framework**: Flask (servidor HTTP)
- **Função**: API REST que gerencia inventário de carros (CRUD completo)
- **Porta exposta**: 5100 (mapeada para host)
- **Armazenamento**: Dados em memória (lista Python)
- **Responsabilidade**: Single source of truth para dados de carros

**2. Analytics Service (Microsserviço B - Consumer)**
- **Imagem base**: Python 3.11-slim (custom build)
- **Framework**: Flask + requests (HTTP client)
- **Função**: Consome Garage Service e fornece análises agregadas
- **Porta exposta**: 5101 (mapeada para host)
- **Comunicação**: Requisições HTTP ao Garage Service
- **Responsabilidade**: Processar dados e gerar insights/relatórios

**3. Rede Docker (garage-network)**
- **Tipo**: Bridge customizada
- **DNS interno**: Resolve `garage-service` e `analytics-service`
- **Isolamento**: Comunicação privada entre microsserviços

### 1.3 Decisões Técnicas e Justificativas

**Por que separar em dois microsserviços?**
A separação reflete um design de microsserviços real:
- **Garage Service**: Responsável apenas por CRUD (create, read, update, delete)
- **Analytics Service**: Responsável apenas por análises e agregações

Cada serviço pode ser escalado, deployado e mantido independentemente. Se analytics falhar, o garage continua funcionando.

**Por que comunicação HTTP (não gRPC ou mensageria)?**
HTTP/REST é o padrão mais simples e universal para comunicação entre microsserviços. É síncrono, fácil de debugar (curl, Postman) e não requer protobuf ou message brokers. Para este caso de uso (consultas em tempo real), HTTP é adequado.

**Por que requests library no Analytics Service?**
Requests é a biblioteca HTTP mais popular em Python, com API simples e intuitiva. Suporta timeouts, retry, error handling e é mais fácil que urllib nativo.

**Por que ambos expõem portas ao host?**
Diferente do Desafio 5 (com gateway), aqui os microsserviços são independentes e ambos precisam ser acessíveis externamente para testes. Em produção real, poderia haver um load balancer na frente.

**Por que armazenamento em memória (não banco)?**
O foco do desafio é **comunicação entre microsserviços**, não persistência. Armazenamento em memória simplifica o código e permite focar no que importa: como dois serviços conversam via HTTP.

**Por que timeout de 5 segundos nas requisições?**
Timeout evita que o Analytics Service fique travado esperando resposta infinitamente se o Garage Service estiver lento ou inoperante. É uma boa prática de resiliência.

**Por que `depends_on` do Analytics para Garage?**
Garante que o Garage Service (provider de dados) inicie antes do Analytics Service (consumer). Evita erros de "connection refused" no startup, embora o Analytics deva tratar falhas gracefully.

**Organização do projeto:**
```
desafio4/
├── docker-compose.yml          # Orquestração (2 serviços + rede)
├── start.sh, stop.sh, logs.sh  # Scripts de gerenciamento
├── test.sh                     # Testa endpoints de ambos serviços
├── garage-service/
│   ├── Dockerfile              # Build do Garage Service
│   ├── app.py                  # API Flask - CRUD
│   └── requirements.txt        # Flask
└── analytics-service/
    ├── Dockerfile              # Build do Analytics Service
    ├── app.py                  # API Flask - Análises
    └── requirements.txt        # Flask, requests
```

### 1.4 Tema: Forza Garage

O sistema gerencia uma **garagem profissional de carros de alta performance**:

**10 Carros Cadastrados no Garage Service:**
- **Hypercars**: Ferrari SF90 Stradale (986 HP), Lamborghini Revuelto (1001 HP)
- **Supercars**: McLaren 720S (710 HP), Aston Martin DBS (715 HP), Mercedes-AMG GT Black Series (720 HP)
- **Sports**: Porsche 911 GT3 RS (518 HP), Chevrolet Corvette Z06 (670 HP), Audi R8 V10 (602 HP), BMW M8 Competition (617 HP), Nissan GT-R Nismo (600 HP)

**4 Status Possíveis:**
- `available`: Disponível para uso
- `racing`: Em competição
- `maintenance`: Em manutenção
- `sold`: Vendido

**4 Categorias:**
- **Hypercar**: Extremos (900+ HP)
- **Supercar**: Alta performance (700-899 HP)
- **Sports**: Esportivos (500-699 HP)
- **Luxury**: Luxo (300-499 HP)

**Analytics Service enriquece com:**
- Classificação de preço (Economy, Mid-range, Luxury, Ultra-luxury)
- Classificação de performance (Standard, High, Extreme)
- Valor por HP (custo-benefício)
- Dias na garagem (tempo desde adição)
- Análise de status (interpretação do estado atual)

## 2. Explicação Detalhada do Funcionamento

### 2.1 Fluxo Completo de Inicialização

**1. Docker Compose sobe os serviços:**
```bash
docker-compose up -d
```

**2. Ordem de inicialização (definida por `depends_on`):**
```
garage-service (porta 5100)
    ↓ (inicia primeiro)
analytics-service (porta 5101)
    ↓ (depende de garage-service)
```

**3. Garage Service inicializa:**
- Container `garage-service` sobe
- Flask app inicia na porta 5100
- Função `init_data()` executa:
  - Popula `cars_db` (lista Python) com 10 carros
  - Define `next_id = 11` (próximo ID disponível)
- Endpoints CRUD ficam disponíveis
- Logs: `🏎️ Garage Service running on port 5100`

**4. Analytics Service inicializa:**
- Container `analytics-service` sobe
- Flask app inicia na porta 5101
- Configura `GARAGE_SERVICE_URL = http://garage-service:5100`
- Endpoints de análise ficam disponíveis
- Logs: `📊 Analytics Service running on port 5101`

**5. Sistema pronto:**
- Garage Service: `http://localhost:5100`
- Analytics Service: `http://localhost:5101`
- Comunicação interna: Analytics usa DNS `garage-service:5100`

### 2.2 Garage Service - Arquitetura Interna (Microsserviço A)

**Estrutura de dados em memória:**

```python
# Lista global que armazena todos os carros
cars_db = []

# Contador de IDs (auto-incremento)
next_id = 1

# Exemplo de estrutura de um carro:
{
    "id": 1,
    "manufacturer": "Ferrari",
    "model": "SF90 Stradale",
    "year": 2023,
    "horsepower": 986,
    "top_speed": 211,
    "acceleration": 2.5,  # 0-60 mph em segundos
    "price": 625000,
    "status": "available",
    "category": "Hypercar",
    "added_at": "2025-11-30T14:30:00"  # timestamp ISO 8601
}
```

**Endpoints CRUD - Detalhamento:**

**1. `GET /cars` - Listar todos os carros**
```python
@app.route("/cars")
def get_cars():
    return jsonify({
        "service": "garage-service",
        "total": len(cars_db),
        "cars": cars_db
    })
```

**2. `GET /cars/<id>` - Buscar carro específico**
```python
@app.route("/cars/<int:car_id>")
def get_car(car_id):
    car = next((c for c in cars_db if c["id"] == car_id), None)
    
    if not car:
        return jsonify({"error": "Car not found"}), 404
    
    return jsonify({
        "service": "garage-service",
        "car": car
    })
```

**3. `POST /cars` - Adicionar novo carro**
```python
@app.route("/cars", methods=["POST"])
def add_car():
    global next_id
    
    data = request.json
    
    # Validação de campos obrigatórios
    required = ["manufacturer", "model", "year", "horsepower", 
                "top_speed", "acceleration", "price", "category"]
    
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Cria novo carro
    new_car = {
        "id": next_id,
        **data,
        "status": data.get("status", "available"),
        "added_at": datetime.now().isoformat()
    }
    
    cars_db.append(new_car)
    next_id += 1
    
    return jsonify({
        "message": "Car added successfully",
        "car": new_car
    }), 201
```

**4. `PUT /cars/<id>` - Atualizar carro**
```python
@app.route("/cars/<int:car_id>", methods=["PUT"])
def update_car(car_id):
    car = next((c for c in cars_db if c["id"] == car_id), None)
    
    if not car:
        return jsonify({"error": "Car not found"}), 404
    
    data = request.json
    
    # Atualiza apenas campos fornecidos
    for key, value in data.items():
        if key != "id" and key != "added_at":  # Não permite mudar ID ou timestamp
            car[key] = value
    
    return jsonify({
        "message": "Car updated successfully",
        "car": car
    })
```

**5. `DELETE /cars/<id>` - Remover carro**
```python
@app.route("/cars/<int:car_id>", methods=["DELETE"])
def delete_car(car_id):
    global cars_db
    
    car = next((c for c in cars_db if c["id"] == car_id), None)
    
    if not car:
        return jsonify({"error": "Car not found"}), 404
    
    cars_db = [c for c in cars_db if c["id"] != car_id]
    
    return jsonify({
        "message": "Car deleted successfully",
        "deleted_car": car
    })
```

**6. `GET /stats` - Estatísticas básicas**
```python
@app.route("/stats")
def get_stats():
    if not cars_db:
        return jsonify({"total": 0, "message": "No cars in garage"})
    
    total_value = sum(c["price"] for c in cars_db)
    avg_horsepower = sum(c["horsepower"] for c in cars_db) / len(cars_db)
    
    # Agrupa por status
    by_status = {}
    for car in cars_db:
        status = car["status"]
        by_status[status] = by_status.get(status, 0) + 1
    
    # Agrupa por categoria
    by_category = {}
    for car in cars_db:
        category = car["category"]
        by_category[category] = by_category.get(category, 0) + 1
    
    return jsonify({
        "service": "garage-service",
        "total_cars": len(cars_db),
        "total_value": total_value,
        "average_horsepower": round(avg_horsepower, 2),
        "by_status": by_status,
        "by_category": by_category
    })
```

**7. `GET /health` - Health check**
```python
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "garage-service",
        "port": 5100,
        "total_cars": len(cars_db),
        "timestamp": datetime.now().isoformat()
    })
```

### 2.3 Analytics Service - Comunicação HTTP e Processamento (Microsserviço B)

**Configuração da comunicação:**

```python
import requests

# URL do Garage Service (via variável de ambiente)
GARAGE_SERVICE_URL = os.getenv("GARAGE_SERVICE_URL", "http://garage-service:5100")

# Função para buscar carros do Garage Service
def get_cars_from_garage():
    try:
        # Timeout de 5 segundos
        response = requests.get(f"{GARAGE_SERVICE_URL}/cars", timeout=5)
        
        # Lança exceção se status != 2xx
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        
        # Retorna lista de carros
        return data.get("cars", [])
        
    except requests.exceptions.Timeout:
        print("❌ Timeout: Garage Service não respondeu em 5 segundos")
        return None
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Garage Service inacessível")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
```

**Por que esse tratamento de erros?**
- **Timeout**: Evita travar indefinidamente
- **ConnectionError**: Garage Service pode estar down
- **RequestException**: Captura outros erros HTTP

**Retornar `None` permite que o Analytics responda gracefully:**
```json
{
  "error": "Unable to connect to Garage Service",
  "status": 503
}
```

**Funções de análise (enriquecimento de dados):**

```python
def calculate_price_class(price):
    """Classifica carro por faixa de preço"""
    if price < 150000:
        return "Economy"
    elif price < 300000:
        return "Mid-range"
    elif price < 600000:
        return "Luxury"
    else:
        return "Ultra-luxury"

def calculate_performance_class(horsepower):
    """Classifica carro por potência"""
    if horsepower < 600:
        return "Standard"
    elif horsepower < 900:
        return "High"
    else:
        return "Extreme"

def calculate_days_in_garage(added_at):
    """Calcula dias desde adição"""
    try:
        added_date = datetime.fromisoformat(added_at)
        days = (datetime.now() - added_date).days
        return days
    except:
        return 0

def get_status_analysis(status):
    """Interpreta status do carro"""
    status_map = {
        "available": "Ready for use",
        "racing": "Currently in competition",
        "maintenance": "Under maintenance",
        "sold": "No longer in inventory"
    }
    return status_map.get(status, "Unknown status")
```

**Endpoints do Analytics Service - Detalhamento:**

**1. `GET /report` - Relatório completo de todos os carros**
```python
@app.route("/report")
def get_report():
    # 1. BUSCA DADOS DO GARAGE SERVICE
    cars = get_cars_from_garage()
    
    if cars is None:
        return jsonify({
            "error": "Unable to connect to Garage Service"
        }), 503
    
    if not cars:
        return jsonify({
            "report_type": "complete",
            "total": 0,
            "cars": []
        })
    
    # 2. ENRIQUECE CADA CARRO COM ANÁLISES
    enriched_cars = []
    for car in cars:
        enriched = {
            **car,  # Dados originais do Garage
            "analysis": {
                "price_class": calculate_price_class(car["price"]),
                "performance_class": calculate_performance_class(car["horsepower"]),
                "value_per_hp": round(car["price"] / car["horsepower"], 2),
                "days_in_garage": calculate_days_in_garage(car["added_at"]),
                "status_analysis": get_status_analysis(car["status"])
            }
        }
        enriched_cars.append(enriched)
    
    # 3. RETORNA RELATÓRIO ENRIQUECIDO
    return jsonify({
        "service": "analytics-service",
        "report_type": "complete",
        "total": len(enriched_cars),
        "cars": enriched_cars
    })
```

**Exemplo de resposta:**
```json
{
  "service": "analytics-service",
  "report_type": "complete",
  "total": 10,
  "cars": [
    {
      "id": 1,
      "manufacturer": "Ferrari",
      "model": "SF90 Stradale",
      "horsepower": 986,
      "price": 625000,
      "status": "available",
      "analysis": {
        "price_class": "Ultra-luxury",
        "performance_class": "Extreme",
        "value_per_hp": 633.88,
        "days_in_garage": 3,
        "status_analysis": "Ready for use"
      }
    },
    // ... outros 9 carros
  ]
}
```

**2. `GET /report/<id>` - Relatório detalhado de um carro**
```python
@app.route("/report/<int:car_id>")
def get_car_report(car_id):
    # 1. BUSCA CARRO ESPECÍFICO NO GARAGE SERVICE
    try:
        response = requests.get(
            f"{GARAGE_SERVICE_URL}/cars/{car_id}",
            timeout=5
        )
        
        if response.status_code == 404:
            return jsonify({"error": "Car not found"}), 404
        
        response.raise_for_status()
        data = response.json()
        car = data.get("car")
        
    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Unable to connect to Garage Service"
        }), 503
    
    # 2. GERA ANÁLISE DETALHADA
    detailed_analysis = {
        **car,
        "detailed_analysis": {
            "price_class": calculate_price_class(car["price"]),
            "performance_class": calculate_performance_class(car["horsepower"]),
            "value_per_hp": round(car["price"] / car["horsepower"], 2),
            "days_in_garage": calculate_days_in_garage(car["added_at"]),
            "status_analysis": get_status_analysis(car["status"]),
            "speed_per_hp_ratio": round(car["top_speed"] / car["horsepower"], 4),
            "efficiency_score": round((car["top_speed"] * car["horsepower"]) / car["price"], 2)
        }
    }
    
    return jsonify({
        "service": "analytics-service",
        "report_type": "individual",
        "car": detailed_analysis
    })
```

**3. `GET /summary` - Resumo executivo agregado**
```python
@app.route("/summary")
def get_summary():
    cars = get_cars_from_garage()
    
    if cars is None:
        return jsonify({"error": "Unable to connect"}), 503
    
    if not cars:
        return jsonify({"summary": "No cars in garage"})
    
    # AGREGAÇÕES
    total_value = sum(c["price"] for c in cars)
    avg_price = total_value / len(cars)
    avg_horsepower = sum(c["horsepower"] for c in cars) / len(cars)
    avg_top_speed = sum(c["top_speed"] for c in cars) / len(cars)
    
    # ANÁLISES POR CLASSIFICAÇÃO
    price_classes = {}
    performance_classes = {}
    
    for car in cars:
        pc = calculate_price_class(car["price"])
        price_classes[pc] = price_classes.get(pc, 0) + 1
        
        perf = calculate_performance_class(car["horsepower"])
        performance_classes[perf] = performance_classes.get(perf, 0) + 1
    
    # CARROS DESTAQUE
    most_expensive = max(cars, key=lambda c: c["price"])
    fastest = max(cars, key=lambda c: c["top_speed"])
    most_powerful = max(cars, key=lambda c: c["horsepower"])
    best_value = min(cars, key=lambda c: c["price"] / c["horsepower"])
    
    return jsonify({
        "service": "analytics-service",
        "summary_type": "executive",
        "overview": {
            "total_cars": len(cars),
            "total_value": total_value,
            "average_price": round(avg_price, 2),
            "average_horsepower": round(avg_horsepower, 2),
            "average_top_speed": round(avg_top_speed, 2)
        },
        "distribution": {
            "by_price_class": price_classes,
            "by_performance_class": performance_classes
        },
        "highlights": {
            "most_expensive": {
                "manufacturer": most_expensive["manufacturer"],
                "model": most_expensive["model"],
                "price": most_expensive["price"]
            },
            "fastest": {
                "manufacturer": fastest["manufacturer"],
                "model": fastest["model"],
                "top_speed": fastest["top_speed"]
            },
            "most_powerful": {
                "manufacturer": most_powerful["manufacturer"],
                "model": most_powerful["model"],
                "horsepower": most_powerful["horsepower"]
            },
            "best_value": {
                "manufacturer": best_value["manufacturer"],
                "model": best_value["model"],
                "value_per_hp": round(best_value["price"] / best_value["horsepower"], 2)
            }
        }
    })
```

**4. `GET /activity` - Análise de atividade**
```python
@app.route("/activity")
def get_activity():
    cars = get_cars_from_garage()
    
    if cars is None:
        return jsonify({"error": "Unable to connect"}), 503
    
    # Analisa status atual da garagem
    activity = {
        "available": [],
        "racing": [],
        "maintenance": [],
        "sold": []
    }
    
    for car in cars:
        status = car["status"]
        activity[status].append({
            "id": car["id"],
            "manufacturer": car["manufacturer"],
            "model": car["model"]
        })
    
    return jsonify({
        "service": "analytics-service",
        "analysis_type": "activity",
        "summary": {
            "available_count": len(activity["available"]),
            "racing_count": len(activity["racing"]),
            "maintenance_count": len(activity["maintenance"]),
            "sold_count": len(activity["sold"])
        },
        "details": activity
    })
```

**5. `GET /health` - Health check integrado**
```python
@app.route("/health")
def health():
    # Verifica próprio status
    analytics_status = {
        "status": "healthy",
        "service": "analytics-service",
        "port": 5101
    }
    
    # Verifica Garage Service
    try:
        response = requests.get(
            f"{GARAGE_SERVICE_URL}/health",
            timeout=2
        )
        
        if response.status_code == 200:
            garage_status = {
                "status": "healthy",
                "reachable": True
            }
        else:
            garage_status = {
                "status": "unhealthy",
                "reachable": True,
                "http_code": response.status_code
            }
            
    except requests.exceptions.RequestException:
        garage_status = {
            "status": "unreachable",
            "reachable": False
        }
    
    # Status geral
    overall_healthy = (
        analytics_status["status"] == "healthy" and
        garage_status["status"] == "healthy"
    )
    
    return jsonify({
        "overall_status": "healthy" if overall_healthy else "degraded",
        "analytics_service": analytics_status,
        "garage_service": garage_status,
        "timestamp": datetime.now().isoformat()
    }), 200 if overall_healthy else 503
```

### 2.4 Comunicação entre Microsserviços - Fluxo Detalhado

**Cenário: Cliente solicita relatório ao Analytics Service**

```
1. Cliente (curl/browser)
   ↓
   GET http://localhost:5101/report
   ↓
2. Analytics Service (Flask app)
   ↓
   [Função get_cars_from_garage() executa]
   ↓
3. Requisição HTTP interna
   ↓
   requests.get("http://garage-service:5100/cars", timeout=5)
   ↓
4. DNS interno Docker resolve "garage-service" → IP do container
   ↓
5. Requisição é roteada pela bridge "garage-network"
   ↓
6. Garage Service (Flask app) recebe
   ↓
   GET /cars
   ↓
7. Garage Service processa
   ↓
   Retorna JSON: {"service": "garage-service", "total": 10, "cars": [...]}
   ↓
8. Analytics Service recebe resposta
   ↓
   [Enriquece cada carro com análises]
   ↓
9. Analytics Service retorna JSON enriquecido
   ↓
10. Cliente recebe resposta final
```

**Exemplo de log combinado:**

```
analytics-service | ➡️  Requesting data from Garage Service...
analytics-service | 🔗 GET http://garage-service:5100/cars
garage-service    | 📥 Received GET /cars from 172.21.0.3
garage-service    | ✅ Returning 10 cars
analytics-service | ✅ Received 10 cars from Garage Service
analytics-service | 🔄 Processing analytics...
analytics-service | ✅ Returning enriched report with 10 cars
```

### 2.5 Rede Docker e Descoberta de Serviços

**Rede configurada:**
```yaml
networks:
  garage-network:
    name: garage-network
    driver: bridge
```

**Containers na rede:**
```
Container              IP interno       Porta
─────────────────────────────────────────────
garage-service         172.21.0.2       5100
analytics-service      172.21.0.3       5101
```

**Como DNS funciona:**
```python
# No código do Analytics Service:
GARAGE_SERVICE_URL = "http://garage-service:5100"

# Docker resolve automaticamente:
"garage-service" → 172.21.0.2
```

**Alternativas que NÃO funcionariam:**
```python
# ❌ ERRADO: Usar localhost
GARAGE_SERVICE_URL = "http://localhost:5100"
# Falharia: localhost refere-se ao próprio container, não ao vizinho

# ❌ ERRADO: Usar IP direto
GARAGE_SERVICE_URL = "http://172.21.0.2:5100"
# Funcionaria, mas IP pode mudar a cada restart

# ✅ CORRETO: Usar nome do container
GARAGE_SERVICE_URL = "http://garage-service:5100"
# DNS resolve dinamicamente
```

### 2.6 Tratamento de Falhas e Resiliência

**Cenário 1: Garage Service está down**

```python
# Analytics tenta conectar:
response = requests.get(f"{GARAGE_SERVICE_URL}/cars", timeout=5)

# Exceção: requests.exceptions.ConnectionError
# "Connection refused" ou "Name or service not known"

# Analytics responde gracefully:
return jsonify({
    "error": "Unable to connect to Garage Service",
    "service": "Analytics Service"
}), 503  # Service Unavailable
```

**Cenário 2: Garage Service demora a responder**

```python
# Timeout após 5 segundos:
response = requests.get(..., timeout=5)

# Exceção: requests.exceptions.Timeout

# Analytics não fica travado:
return jsonify({
    "error": "Garage Service timeout",
    "message": "Service did not respond in 5 seconds"
}), 503
```

**Cenário 3: Garage Service retorna erro**

```python
# Exemplo: GET /cars/999 (não existe)
response = requests.get(f"{GARAGE_SERVICE_URL}/cars/999")

# Garage retorna: 404 Not Found

# Analytics propaga erro:
if response.status_code == 404:
    return jsonify({"error": "Car not found"}), 404
```

**Logs de falha esperados:**

```
analytics-service | ➡️  Requesting data from Garage Service...
analytics-service | ❌ Connection Error: Garage Service inacessível
analytics-service | 🔄 Returning error response to client
```

### 2.7 Logs e Observabilidade

**Logs esperados - Garage Service:**
```
🏎️  FORZA GARAGE - Garage Service
🚀 Starting on port 5100...
✅ Initialized with 10 cars
📋 Inventory loaded successfully

[Request logs]
172.21.0.1 - - [30/Nov/2025 14:30:00] "GET /cars HTTP/1.1" 200 -
172.21.0.3 - - [30/Nov/2025 14:30:05] "GET /cars HTTP/1.1" 200 -
172.21.0.1 - - [30/Nov/2025 14:30:10] "POST /cars HTTP/1.1" 201 -
```

**Logs esperados - Analytics Service:**
```
📊 FORZA GARAGE - Analytics Service
🚀 Starting on port 5101...
🔗 Garage Service URL: http://garage-service:5100
✅ Service ready

[Request logs]
172.21.0.1 - - [30/Nov/2025 14:30:05] "GET /report HTTP/1.1" 200 -
➡️  Fetching data from Garage Service...
✅ Received 10 cars
🔄 Processing analytics...
```

**Visualizar logs:**
```bash
# Todos os serviços
docker-compose logs

# Apenas Garage
docker-compose logs garage-service

# Apenas Analytics
docker-compose logs analytics-service

# Tempo real
docker-compose logs -f
```

## 3. Instruções de Execução – Passo a Passo

### 3.1 Pré-requisitos

**Software necessário:**
- Docker Engine 20.10 ou superior
- Docker Compose 1.29 ou superior
- Sistema operacional: Linux, macOS ou Windows com WSL2

**Verificar instalação:**
```bash
docker --version
docker-compose --version
```

### 3.2 Preparação do Ambiente

**1. Navegar até o diretório:**
```bash
cd /caminho/para/desafio4
```

**2. Verificar estrutura:**
```bash
ls -la
# Deve conter: docker-compose.yml, garage-service/, analytics-service/
```

**3. Tornar scripts executáveis:**
```bash
chmod +x *.sh
```

### 3.3 Construir e Iniciar Microsserviços

**Opção 1: Script automatizado**
```bash
./start.sh
```

**Opção 2: Comandos manuais**
```bash
# Build das imagens
docker-compose build

# Subir serviços
docker-compose up -d
```

**Saída esperada:**
```
Creating network "garage-network" with driver "bridge"
Creating garage-service ... done
Creating analytics-service ... done

🏁 Forza Garage - Microsserviços iniciados!
🏎️  Garage Service: http://localhost:5100
📊 Analytics Service: http://localhost:5101
```

**Verificar containers:**
```bash
docker-compose ps
```

**Saída esperada:**
```
NAME                  STATUS    PORTS
garage-service        Up        0.0.0.0:5100->5100/tcp
analytics-service     Up        0.0.0.0:5101->5101/tcp
```

### 3.4 Testar Garage Service (Microsserviço A)

**1. Informações do serviço:**
```bash
curl http://localhost:5100/
```

**2. Listar todos os carros:**
```bash
curl http://localhost:5100/cars | jq
```

**Resposta (resumida):**
```json
{
  "service": "garage-service",
  "total": 10,
  "cars": [
    {
      "id": 1,
      "manufacturer": "Ferrari",
      "model": "SF90 Stradale",
      "horsepower": 986,
      "price": 625000,
      "status": "available"
    },
    // ... outros 9 carros
  ]
}
```

**3. Buscar carro específico:**
```bash
curl http://localhost:5100/cars/1 | jq
```

**4. Estatísticas da garagem:**
```bash
curl http://localhost:5100/stats | jq
```

**Resposta:**
```json
{
  "service": "garage-service",
  "total_cars": 10,
  "total_value": 3037000,
  "average_horsepower": 693.9,
  "by_status": {
    "available": 7,
    "racing": 1,
    "maintenance": 1,
    "sold": 1
  },
  "by_category": {
    "Hypercar": 2,
    "Supercar": 3,
    "Sports": 5
  }
}
```

**5. Health check:**
```bash
curl http://localhost:5100/health | jq
```

**6. Adicionar novo carro (POST):**
```bash
curl -X POST http://localhost:5100/cars \
  -H "Content-Type: application/json" \
  -d '{
    "manufacturer": "Bugatti",
    "model": "Chiron",
    "year": 2024,
    "horsepower": 1500,
    "top_speed": 261,
    "acceleration": 2.3,
    "price": 3000000,
    "category": "Hypercar",
    "status": "available"
  }' | jq
```

**Resposta:**
```json
{
  "message": "Car added successfully",
  "car": {
    "id": 11,
    "manufacturer": "Bugatti",
    "model": "Chiron",
    "horsepower": 1500,
    "price": 3000000,
    "added_at": "2025-11-30T14:35:22"
  }
}
```

**7. Atualizar status de um carro (PUT):**
```bash
curl -X PUT http://localhost:5100/cars/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "racing"}' | jq
```

**8. Deletar carro (DELETE):**
```bash
curl -X DELETE http://localhost:5100/cars/11 | jq
```

### 3.5 Testar Analytics Service (Microsserviço B)

**1. Informações do serviço:**
```bash
curl http://localhost:5101/
```

**2. Relatório completo (consome Garage Service):**
```bash
curl http://localhost:5101/report | jq
```

**Resposta (resumida):**
```json
{
  "service": "analytics-service",
  "report_type": "complete",
  "total": 10,
  "cars": [
    {
      "id": 1,
      "manufacturer": "Ferrari",
      "model": "SF90 Stradale",
      "horsepower": 986,
      "price": 625000,
      "analysis": {
        "price_class": "Ultra-luxury",
        "performance_class": "Extreme",
        "value_per_hp": 633.88,
        "days_in_garage": 0,
        "status_analysis": "Ready for use"
      }
    },
    // ... outros 9 com análise
  ]
}
```

**3. Relatório individual detalhado:**
```bash
curl http://localhost:5101/report/1 | jq
```

**4. Resumo executivo:**
```bash
curl http://localhost:5101/summary | jq
```

**Resposta:**
```json
{
  "service": "analytics-service",
  "summary_type": "executive",
  "overview": {
    "total_cars": 10,
    "total_value": 3037000,
    "average_price": 303700,
    "average_horsepower": 693.9,
    "average_top_speed": 201.2
  },
  "distribution": {
    "by_price_class": {
      "Economy": 1,
      "Mid-range": 3,
      "Luxury": 4,
      "Ultra-luxury": 2
    },
    "by_performance_class": {
      "Standard": 5,
      "High": 3,
      "Extreme": 2
    }
  },
  "highlights": {
    "most_expensive": {
      "manufacturer": "Ferrari",
      "model": "SF90 Stradale",
      "price": 625000
    },
    "fastest": {
      "manufacturer": "Lamborghini",
      "model": "Revuelto",
      "top_speed": 217
    },
    "most_powerful": {
      "manufacturer": "Lamborghini",
      "model": "Revuelto",
      "horsepower": 1001
    },
    "best_value": {
      "manufacturer": "Chevrolet",
      "model": "Corvette Z06",
      "value_per_hp": 158.21
    }
  }
}
```

**5. Análise de atividade:**
```bash
curl http://localhost:5101/activity | jq
```

**6. Health check integrado:**
```bash
curl http://localhost:5101/health | jq
```

**Resposta:**
```json
{
  "overall_status": "healthy",
  "analytics_service": {
    "status": "healthy",
    "service": "analytics-service",
    "port": 5101
  },
  "garage_service": {
    "status": "healthy",
    "reachable": true
  },
  "timestamp": "2025-11-30T14:40:00"
}
```

### 3.6 Validar Comunicação entre Microsserviços

**Teste: Analytics consome dados do Garage**

**1. Ver logs do Analytics em tempo real:**
```bash
docker-compose logs -f analytics-service
```

**2. Em outro terminal, fazer requisição ao Analytics:**
```bash
curl http://localhost:5101/report
```

**3. Observar logs mostrando comunicação:**
```
analytics-service | ➡️  Requesting data from Garage Service...
analytics-service | 🔗 GET http://garage-service:5100/cars
analytics-service | ✅ Received 10 cars from Garage Service
analytics-service | 🔄 Processing analytics...
analytics-service | ✅ Returning enriched report
```

**4. Ver logs do Garage em paralelo:**
```bash
docker-compose logs -f garage-service
```

```
garage-service | 📥 Received GET /cars from 172.21.0.3 (analytics-service)
garage-service | ✅ Returning 10 cars
```

### 3.7 Testar Resiliência (Falha de Comunicação)

**Cenário: O que acontece se Garage Service cai?**

**1. Parar apenas o Garage Service:**
```bash
docker stop garage-service
```

**2. Tentar acessar Analytics:**
```bash
curl http://localhost:5101/report
```

**Resposta esperada:**
```json
{
  "error": "Unable to connect to Garage Service",
  "service": "Analytics Service"
}
```
**HTTP Status: 503 Service Unavailable**

**3. Ver logs do Analytics:**
```bash
docker-compose logs analytics-service
```

```
analytics-service | ➡️  Requesting data from Garage Service...
analytics-service | ❌ Connection Error: Garage Service inacessível
analytics-service | 🔄 Returning error response to client
```

**4. Restart Garage Service:**
```bash
docker start garage-service
```

**5. Aguardar 2-3 segundos e tentar novamente:**
```bash
curl http://localhost:5101/report | jq '.total'
# 10 ✅ Funcionando novamente!
```

### 3.8 Testar Todos os Endpoints Automaticamente

**Script de testes:**
```bash
./test.sh
```

**O script testa:**

**Garage Service:**
1. GET / (info)
2. GET /cars (listar)
3. GET /cars/1 (buscar)
4. GET /stats (estatísticas)
5. GET /health (saúde)
6. POST /cars (adicionar)
7. PUT /cars/11 (atualizar)
8. DELETE /cars/11 (deletar)

**Analytics Service:**
1. GET / (info)
2. GET /report (relatório completo)
3. GET /report/1 (relatório individual)
4. GET /summary (resumo executivo)
5. GET /activity (atividade)
6. GET /health (saúde integrada)

### 3.9 Inspecionar Comunicação entre Containers

**Entrar no Analytics Service:**
```bash
docker exec -it analytics-service /bin/bash
```

**Testar conectividade com Garage:**
```bash
# Ping (se disponível)
ping garage-service

# Curl manual
curl http://garage-service:5100/cars
```

**Verificar variável de ambiente:**
```bash
echo $GARAGE_SERVICE_URL
# http://garage-service:5100
```

**Resolver DNS:**
```bash
nslookup garage-service
# Retorna IP do container garage-service
```

**Sair:**
```bash
exit
```

### 3.10 Monitorar Logs em Tempo Real

**Logs combinados (ambos serviços):**
```bash
./logs.sh
# OU:
docker-compose logs -f
```

**Exemplo de saída:**
```
garage-service    | 🏎️  Garage Service running on port 5100
analytics-service | 📊 Analytics Service running on port 5101
garage-service    | ✅ Initialized with 10 cars
analytics-service | 🔗 Connected to Garage Service

analytics-service | ➡️  GET /report from 172.21.0.1
analytics-service | 🔗 Requesting http://garage-service:5100/cars
garage-service    | 📥 GET /cars from 172.21.0.3
garage-service    | ✅ Returning 10 cars (2KB)
analytics-service | ✅ Received 10 cars
analytics-service | 🔄 Enriching with analytics...
analytics-service | ✅ Returning report (5KB)
```

### 3.11 Limpar e Reiniciar

**Parar serviços:**
```bash
./stop.sh
# OU:
docker-compose down
```

**Rebuild completo:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 3.12 Troubleshooting

**Problema: Analytics não consegue conectar ao Garage**
```bash
# Verificar que ambos estão na mesma rede
docker network inspect garage-network

# Verificar DNS funciona
docker exec analytics-service ping garage-service

# Ver logs
docker-compose logs garage-service
docker-compose logs analytics-service
```

**Problema: Porta 5100 ou 5101 já em uso**
```bash
# Verificar o que está usando
lsof -i :5100
lsof -i :5101

# Alterar porta no docker-compose.yml
ports:
  - "5102:5100"  # host:container
```

**Problema: Timeout ao conectar**
```bash
# Aumentar timeout no analytics-service/app.py:
response = requests.get(..., timeout=10)  # 10 segundos
```

---

## Observações Finais

**✅ Arquitetura de Microsserviços:**
Dois serviços independentes com responsabilidades bem definidas (CRUD vs Analytics), comunicando-se via HTTP/REST.

**✅ Comunicação HTTP:**
Analytics Service consome Garage Service via `requests.get()`, usando DNS interno Docker para descoberta de serviço.

**✅ Separação de Responsabilidades:**
Garage Service é o single source of truth para dados. Analytics Service apenas consome e processa, nunca modifica.

**✅ Tratamento de Falhas:**
Analytics responde gracefully (HTTP 503) quando Garage está inacessível, com timeout de 5 segundos para evitar travamentos.

**✅ Independência de Deploy:**
Cada serviço pode ser escalado, atualizado ou reiniciado independentemente. Se Analytics cai, Garage continua operacional.

**✅ Enriquecimento de Dados:**
Analytics adiciona valor processando dados brutos: classificações de preço/performance, análises de custo-benefício, agregações.

**✅ Health Check Integrado:**
Analytics verifica não só seu próprio status, mas também a disponibilidade do Garage Service, fornecendo visão completa do sistema.

**✅ Logs Descritivos:**
Ambos serviços geram logs detalhados mostrando fluxo de requisições, facilitando debugging e observabilidade.
