# Desafio 5 — API Gateway: Central Perk Cafeteria ☕

## 1. Descrição Geral da Solução

### 1.1 Proposta do Desafio

Este desafio implementa o **padrão arquitetural API Gateway** aplicado a microsserviços. O objetivo é demonstrar como um gateway centraliza o acesso a múltiplos microsserviços backend, oferecendo um ponto único de entrada, orquestrando chamadas entre serviços e agregando dados de fontes distintas.

A arquitetura explora conceitos avançados de microsserviços: **gateway como frontend para backend** (BFF - Backend For Frontend), **orquestração vs coreografia**, **roteamento inteligente**, **agregação de dados cross-service** e **health monitoring centralizado**.

### 1.2 Arquitetura Utilizada

A solução é composta por **quatro componentes principais**:

**1. API Gateway (Ponto Único de Entrada)**
- **Imagem base**: Python 3.11-slim (custom build)
- **Framework**: Flask + requests (HTTP client)
- **Função**: Orquestrador central - roteia requisições e combina dados
- **Porta exposta**: 8000 (única porta pública)
- **Comunicação**: HTTP para Users Service (5001) e Orders Service (5002)
- **Responsabilidade**: Single entry point para todos os clientes

**2. Users Service (Microsserviço Backend A)**
- **Imagem base**: Python 3.11-slim (custom build)
- **Framework**: Flask (servidor HTTP)
- **Função**: Gerencia clientes da cafeteria
- **Porta**: 5001 (interna, não exposta ao host)
- **Armazenamento**: Dados em memória (dicionário Python)
- **Responsabilidade**: CRUD de usuários, filtros por bebida favorita

**3. Orders Service (Microsserviço Backend B)**
- **Imagem base**: Python 3.11-slim (custom build)
- **Framework**: Flask (servidor HTTP)
- **Função**: Gerencia pedidos da cafeteria
- **Porta**: 5002 (interna, não exposta ao host)
- **Armazenamento**: Dados em memória (dicionário Python)
- **Responsabilidade**: CRUD de pedidos, filtros por status/categoria

**4. Rede Docker (microservices-network)**
- **Tipo**: Bridge customizada
- **DNS interno**: Resolve `users-service`, `orders-service`, `api-gateway`
- **Isolamento**: Comunicação privada, apenas gateway exposto

### 1.3 Decisões Técnicas e Justificativas

**Por que usar API Gateway?**
O Gateway resolve problemas críticos de arquiteturas distribuídas:
- **Ponto único de entrada**: Clientes conhecem apenas o gateway (localhost:8000), não precisam conhecer IPs/portas dos microsserviços
- **Desacoplamento**: Microsserviços podem mudar de localização/porta sem afetar clientes
- **Orquestração**: Gateway combina dados de múltiplos serviços em uma única resposta
- **Segurança**: Gateway pode implementar autenticação/autorização centralizadas
- **Observabilidade**: Logging e monitoring centralizados no gateway

**Por que microsserviços backend não expõem portas?**
```yaml
# users-service e orders-service:
ports: []  # SEM mapeamento para host

# Apenas gateway:
ports:
  - "8000:8000"  # Único ponto de acesso externo
```

Essa decisão força o padrão Gateway:
- Clientes **DEVEM** acessar via gateway (não há forma de acessar services diretamente)
- Backend fica **isolado e protegido** da internet
- Simula ambiente de produção real (microsserviços em rede privada)

**Por que Flask + requests?**
- Flask: Framework HTTP minimalista, ideal para microsserviços leves
- Requests: Biblioteca HTTP cliente mais popular em Python, com timeout/retry/error handling

**Por que timeout de 5 segundos?**
Evita que gateway fique travado se um microsserviço estiver lento/inoperante. Retorna erro 503 (Service Unavailable) rapidamente ao cliente.

**Por que `depends_on` do Gateway para os Services?**
```yaml
api-gateway:
  depends_on:
    - users-service
    - orders-service
```

Garante que os microsserviços backend estejam rodando antes do gateway iniciar. Evita erros de "connection refused" no startup do gateway.

**Por que 3 tipos de endpoints no Gateway?**

**1. Endpoints de Proxy (simples passthrough):**
```python
# Gateway apenas encaminha
GET /users → users-service:5001/users
GET /orders → orders-service:5002/orders
```
Simplifica acesso, mas não agrega valor além de roteamento.

**2. Endpoints de Orquestração (agregação multi-service):**
```python
# Gateway faz múltiplas chamadas e combina
GET /users/1/orders:
  1. GET users-service:5001/users/1
  2. GET orders-service:5002/orders (filtra por user_id=1)
  3. Retorna: {user: {...}, orders: [...]}
```
**VALOR**: Uma única requisição do cliente resulta em resposta agregada.

**3. Endpoints de Monitoring:**
```python
# Gateway verifica saúde de todos
GET /health:
  1. GET users-service:5001/health
  2. GET orders-service:5002/health
  3. Retorna: status agregado de todos serviços
```
**VALOR**: Visibilidade centralizada da saúde do sistema.

**Por que não usar gRPC ou message broker?**
Este desafio foca em **comunicação síncrona** (HTTP/REST) para demonstrar orquestração clássica. gRPC seria mais performático, message broker (RabbitMQ/Kafka) seria mais resiliente, mas HTTP é mais simples e didático.

**Organização do projeto:**
```
desafio5/
├── docker-compose.yml       # Orquestração (3 serviços + rede)
├── start.sh, stop.sh, logs.sh  # Scripts de gerenciamento
├── test.sh                  # Testa endpoints do gateway
├── gateway/
│   ├── Dockerfile           # Build do Gateway
│   ├── app.py               # API Gateway - Orquestração
│   └── requirements.txt     # Flask, requests
├── users-service/
│   ├── Dockerfile           # Build do Users Service
│   ├── app.py               # API Flask - CRUD Users
│   └── requirements.txt     # Flask
└── orders-service/
    ├── Dockerfile           # Build do Orders Service
    ├── app.py               # API Flask - CRUD Orders
    └── requirements.txt     # Flask
```

### 1.4 Tema: Central Perk Cafeteria

O sistema gerencia a **cafeteria Central Perk** (série Friends), com Gunther como barista principal.

**6 Clientes Cadastrados (Users Service):**
| ID | Nome | Bebida Favorita | Pontos Fidelidade |
|----|------|-----------------|-------------------|
| 1 | Ana Clara Gomes | Cappuccino | 150 |
| 2 | Gabriel Albuquerque | Espresso | 220 |
| 3 | Paulo Rosado | Latte | 95 |
| 4 | Gustavo Mourato | Mocha | 180 |
| 5 | Vinícius de Andrade | Americano | 65 |
| 6 | Luan Kato | Macchiato | 310 |

**10 Pedidos Cadastrados (Orders Service):**
| ID | Cliente | Produto | Categoria | Status | Preço |
|----|---------|---------|-----------|--------|-------|
| 1 | Ana Clara | Cappuccino Grande | Bebida Quente | delivered | R$ 12.50 |
| 2 | Gabriel | Espresso Duplo | Bebida Quente | delivered | R$ 8.00 |
| 3 | Paulo | Latte com Caramelo | Bebida Quente | ready | R$ 14.00 |
| 4 | Ana Clara | Cheesecake | Sobremesa | delivered | R$ 18.00 |
| 5 | Gustavo | Mocha com Chantilly | Bebida Quente | preparing | R$ 15.50 |
| 6 | Vinícius | Americano | Bebida Quente | delivered | R$ 9.00 |
| 7 | Luan | Macchiato | Bebida Quente | ready | R$ 11.00 |
| 8 | Gabriel | Croissant de Chocolate | Doce | delivered | R$ 8.50 |
| 9 | Paulo | Frappuccino de Morango | Bebida Gelada | delivered | R$ 16.00 |
| 10 | Ana Clara | Brownie com Sorvete | Sobremesa | ready | R$ 20.00 |

**4 Status de Pedido:**
- `preparing`: Pedido sendo preparado
- `ready`: Pronto para retirada
- `delivered`: Entregue ao cliente
- `cancelled`: Cancelado

**4 Categorias de Produto:**
- **Bebida Quente**: Cappuccino, Espresso, Latte, Mocha, Americano, Macchiato
- **Bebida Gelada**: Frappuccino, Iced Coffee, Smoothies
- **Doce**: Croissants, Muffins, Cookies
- **Sobremesa**: Cheesecake, Brownie, Tortas

## 2. Explicação Detalhada do Funcionamento

### 2.1 Fluxo Completo de Inicialização

**1. Docker Compose sobe os serviços:**
```bash
docker-compose up -d
```

**2. Ordem de inicialização (definida por `depends_on`):**
```
users-service (porta 5001 - interna)
    ↓ (inicia primeiro)
orders-service (porta 5002 - interna)
    ↓ (inicia em paralelo com users)
api-gateway (porta 8000 - exposta ao host)
    ↓ (depende de ambos services)
```

**3. Users Service inicializa:**
- Container `users-service` sobe
- Flask app inicia na porta 5001 (interna)
- Carrega `USERS_DB` (dicionário com 6 clientes)
- Endpoints disponíveis: `/users`, `/users/<id>`, `/users/drink/<drink>`, `/health`
- Logs: `👤 Users Service running on port 5001`
- **Porta 5001 NÃO é acessível de fora do Docker**

**4. Orders Service inicializa:**
- Container `orders-service` sobe
- Flask app inicia na porta 5002 (interna)
- Carrega `ORDERS_DB` (dicionário com 10 pedidos)
- Endpoints disponíveis: `/orders`, `/orders/<id>`, `/orders/user/<user_id>`, `/orders/status/<status>`, `/orders/category/<category>`, `/health`
- Logs: `📦 Orders Service running on port 5002`
- **Porta 5002 NÃO é acessível de fora do Docker**

**5. API Gateway inicializa:**
- Container `api-gateway` sobe
- Flask app inicia na porta 8000
- Configura URLs dos services:
  - `USERS_SERVICE_URL = http://users-service:5001`
  - `ORDERS_SERVICE_URL = http://orders-service:5002`
- Endpoints disponíveis: proxy, orquestração, monitoring
- Logs: `☕ Central Perk Gateway running on port 8000`
- **Porta 8000 É ACESSÍVEL em localhost:8000**

**6. Sistema pronto:**
- **Cliente externo**: `http://localhost:8000` (GATEWAY)
- **Comunicação interna**: Gateway → `http://users-service:5001` e `http://orders-service:5002`
- **Microsserviços isolados**: não acessíveis diretamente do host

### 2.2 Users Service - Arquitetura Interna (Backend A)

**Estrutura de dados em memória:**

```python
USERS_DB = {
    1: {
        "id": 1,
        "name": "Ana Clara Gomes",
        "email": "ana.gomes@centralperk.com",
        "cpf": "123.456.789-01",
        "member_since": "2023-06-10",
        "favorite_drink": "Cappuccino",
        "loyalty_points": 150,
        "active": True
    },
    # ... outros 5 usuários
}
```

**Endpoints - Detalhamento:**

**1. `GET /users` - Listar todos os clientes**
```python
@app.route("/users", methods=["GET"])
def get_users():
    # Suporta filtro ?active=true|false
    active_filter = request.args.get("active")
    
    users = list(USERS_DB.values())
    
    if active_filter is not None:
        active_bool = active_filter.lower() == "true"
        users = [u for u in users if u["active"] == active_bool]
    
    return jsonify({
        "service": "users-service",
        "total": len(users),
        "users": users
    })
```

**2. `GET /users/<id>` - Buscar cliente por ID**
```python
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = USERS_DB.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "service": "users-service",
        "user": user
    })
```

**3. `GET /users/drink/<drink>` - Filtrar por bebida favorita**
```python
@app.route("/users/drink/<drink>", methods=["GET"])
def get_users_by_drink(drink):
    # Case-insensitive
    drink_lower = drink.lower()
    
    filtered = [
        u for u in USERS_DB.values()
        if u["favorite_drink"].lower() == drink_lower
    ]
    
    return jsonify({
        "service": "users-service",
        "drink": drink,
        "total": len(filtered),
        "users": filtered
    })
```

**4. `GET /health` - Health check**
```python
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "users-service",
        "port": 5001,
        "total_users": len(USERS_DB)
    })
```

### 2.3 Orders Service - Arquitetura Interna (Backend B)

**Estrutura de dados em memória:**

```python
ORDERS_DB = {
    1: {
        "id": 1,
        "user_id": 1,
        "user_name": "Ana Clara Gomes",
        "product": "Cappuccino Grande",
        "category": "Bebida Quente",
        "quantity": 2,
        "price": 12.50,
        "status": "delivered",
        "order_date": "2024-11-28 08:30",
        "served_by": "Gunther"
    },
    # ... outros 9 pedidos
}
```

**Endpoints - Detalhamento:**

**1. `GET /orders` - Listar todos os pedidos**
```python
@app.route("/orders", methods=["GET"])
def get_orders():
    orders = list(ORDERS_DB.values())
    
    return jsonify({
        "service": "orders-service",
        "total": len(orders),
        "orders": orders
    })
```

**2. `GET /orders/<id>` - Buscar pedido por ID**
```python
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = ORDERS_DB.get(order_id)
    
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify({
        "service": "orders-service",
        "order": order
    })
```

**3. `GET /orders/user/<user_id>` - Pedidos de um cliente**
```python
@app.route("/orders/user/<int:user_id>", methods=["GET"])
def get_orders_by_user(user_id):
    filtered = [
        o for o in ORDERS_DB.values()
        if o["user_id"] == user_id
    ]
    
    return jsonify({
        "service": "orders-service",
        "user_id": user_id,
        "total": len(filtered),
        "orders": filtered
    })
```

**4. `GET /orders/status/<status>` - Filtrar por status**
```python
@app.route("/orders/status/<status>", methods=["GET"])
def get_orders_by_status(status):
    # Case-insensitive
    status_lower = status.lower()
    
    filtered = [
        o for o in ORDERS_DB.values()
        if o["status"].lower() == status_lower
    ]
    
    return jsonify({
        "service": "orders-service",
        "status": status,
        "total": len(filtered),
        "orders": filtered
    })
```

**5. `GET /orders/category/<category>` - Filtrar por categoria**
```python
@app.route("/orders/category/<category>", methods=["GET"])
def get_orders_by_category(category):
    # Normaliza categoria
    category_normalized = category.replace("-", " ").title()
    
    filtered = [
        o for o in ORDERS_DB.values()
        if o["category"] == category_normalized
    ]
    
    return jsonify({
        "service": "orders-service",
        "category": category_normalized,
        "total": len(filtered),
        "orders": filtered
    })
```

**6. `GET /health` - Health check**
```python
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "orders-service",
        "port": 5002,
        "total_orders": len(ORDERS_DB)
    })
```

### 2.4 API Gateway - Orquestração e Roteamento (Frontend)

**Configuração:**

```python
import requests

USERS_SERVICE_URL = os.environ.get("USERS_SERVICE_URL", "http://users-service:5001")
ORDERS_SERVICE_URL = os.environ.get("ORDERS_SERVICE_URL", "http://orders-service:5002")

REQUEST_TIMEOUT = 5  # segundos
```

**TIPO 1: Endpoints de Proxy (passthrough simples)**

**1. `GET /users` - Proxy para Users Service**
```python
@app.route("/users", methods=["GET"])
def get_users():
    try:
        # Encaminha requisição com query params
        response = requests.get(
            f"{USERS_SERVICE_URL}/users",
            params=request.args,  # ?active=true passa para o service
            timeout=REQUEST_TIMEOUT
        )
        
        # Retorna mesma resposta que o service
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Users service unavailable",
            "message": str(e)
        }), 503
```

**Fluxo:**
```
Cliente → Gateway:8000/users
         ↓
Gateway → Users:5001/users
         ↓
Gateway ← Users: {"service": "users-service", "total": 6, ...}
         ↓
Cliente ← Gateway: (mesma resposta)
```

**2. `GET /users/<id>` - Proxy para buscar usuário**
```python
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        response = requests.get(
            f"{USERS_SERVICE_URL}/users/{user_id}",
            timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Users service unavailable"}), 503
```

**3. `GET /orders` - Proxy para Orders Service**
```python
@app.route("/orders", methods=["GET"])
def get_orders():
    try:
        response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders",
            params=request.args,
            timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Orders service unavailable"}), 503
```

**4. `GET /orders/<id>` - Proxy para buscar pedido**
```python
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    try:
        response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders/{order_id}",
            timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Orders service unavailable"}), 503
```

**5-7. Outros proxies** (similar - `/users/drink/<drink>`, `/orders/status/<status>`, `/orders/category/<category>`)

**TIPO 2: Endpoints de Orquestração (agregação multi-service)**

**8. `GET /users/<id>/orders` - Cliente com seus pedidos**

**Este é o PRINCIPAL endpoint de orquestração - combina dois services:**

```python
@app.route("/users/<int:user_id>/orders", methods=["GET"])
def get_user_with_orders(user_id):
    try:
        # PASSO 1: Buscar dados do cliente no Users Service
        user_response = requests.get(
            f"{USERS_SERVICE_URL}/users/{user_id}",
            timeout=REQUEST_TIMEOUT
        )
        
        # Se usuário não existe, retorna 404 imediatamente
        if user_response.status_code == 404:
            return jsonify({"error": "User not found"}), 404
        
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # PASSO 2: Buscar pedidos do cliente no Orders Service
        orders_response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders/user/{user_id}",
            timeout=REQUEST_TIMEOUT
        )
        
        orders_response.raise_for_status()
        orders_data = orders_response.json()
        
        # PASSO 3: COMBINAR dados de ambos services
        combined = {
            "service": "api-gateway (orchestration)",
            "user": user_data.get("user"),
            "orders_summary": {
                "total_orders": orders_data.get("total", 0),
                "orders": orders_data.get("orders", [])
            }
        }
        
        return jsonify(combined)
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Unable to orchestrate services",
            "message": str(e)
        }), 503
```

**Fluxo de orquestração:**
```
Cliente → Gateway:8000/users/1/orders
         ↓
[1] Gateway → Users:5001/users/1
    Gateway ← {"user": {"id": 1, "name": "Ana Clara", ...}}
         ↓
[2] Gateway → Orders:5002/orders/user/1
    Gateway ← {"total": 3, "orders": [{...}, {...}, {...}]}
         ↓
[3] Gateway combina:
    {
      "user": {...},
      "orders_summary": {
        "total_orders": 3,
        "orders": [...]
      }
    }
         ↓
Cliente ← Gateway: (resposta agregada)
```

**Exemplo de resposta:**
```json
{
  "service": "api-gateway (orchestration)",
  "user": {
    "id": 1,
    "name": "Ana Clara Gomes",
    "email": "ana.gomes@centralperk.com",
    "favorite_drink": "Cappuccino",
    "loyalty_points": 150
  },
  "orders_summary": {
    "total_orders": 3,
    "orders": [
      {
        "id": 1,
        "product": "Cappuccino Grande",
        "price": 12.50,
        "status": "delivered"
      },
      {
        "id": 4,
        "product": "Cheesecake de Frutas Vermelhas",
        "price": 18.00,
        "status": "delivered"
      },
      {
        "id": 10,
        "product": "Brownie com Sorvete",
        "price": 20.00,
        "status": "ready"
      }
    ]
  }
}
```

**9. `GET /dashboard` - Dashboard da cafeteria (orquestração complexa)**

```python
@app.route("/dashboard", methods=["GET"])
def get_dashboard():
    try:
        # PASSO 1: Buscar todos os usuários
        users_response = requests.get(
            f"{USERS_SERVICE_URL}/users",
            timeout=REQUEST_TIMEOUT
        )
        users_response.raise_for_status()
        users_data = users_response.json()
        
        # PASSO 2: Buscar todos os pedidos
        orders_response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders",
            timeout=REQUEST_TIMEOUT
        )
        orders_response.raise_for_status()
        orders_data = orders_response.json()
        
        # PASSO 3: PROCESSAR e AGREGAR dados
        users = users_data.get("users", [])
        orders = orders_data.get("orders", [])
        
        # Análises agregadas
        total_revenue = sum(o["price"] * o["quantity"] for o in orders)
        avg_order_value = total_revenue / len(orders) if orders else 0
        
        # Agrupa pedidos por status
        orders_by_status = {}
        for order in orders:
            status = order["status"]
            orders_by_status[status] = orders_by_status.get(status, 0) + 1
        
        # Agrupa pedidos por categoria
        orders_by_category = {}
        for order in orders:
            category = order["category"]
            orders_by_category[category] = orders_by_category.get(category, 0) + 1
        
        # Cliente mais ativo (mais pedidos)
        user_order_count = {}
        for order in orders:
            user_id = order["user_id"]
            user_order_count[user_id] = user_order_count.get(user_id, 0) + 1
        
        if user_order_count:
            most_active_user_id = max(user_order_count, key=user_order_count.get)
            most_active_user = next(
                (u for u in users if u["id"] == most_active_user_id),
                None
            )
        else:
            most_active_user = None
        
        # PASSO 4: Retornar dashboard agregado
        dashboard = {
            "service": "api-gateway (dashboard orchestration)",
            "overview": {
                "total_users": len(users),
                "total_orders": len(orders),
                "total_revenue": round(total_revenue, 2),
                "average_order_value": round(avg_order_value, 2)
            },
            "orders_analysis": {
                "by_status": orders_by_status,
                "by_category": orders_by_category
            },
            "most_active_user": {
                "name": most_active_user["name"] if most_active_user else None,
                "total_orders": user_order_count.get(most_active_user_id, 0) if most_active_user else 0
            } if most_active_user else None
        }
        
        return jsonify(dashboard)
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Unable to generate dashboard",
            "message": str(e)
        }), 503
```

**Fluxo:**
```
Cliente → Gateway:8000/dashboard
         ↓
[1] Gateway → Users:5001/users (busca todos)
[2] Gateway → Orders:5002/orders (busca todos)
         ↓
[3] Gateway processa:
    - Calcula receita total
    - Agrupa por status/categoria
    - Identifica cliente mais ativo
         ↓
Cliente ← Gateway: dashboard agregado
```

**TIPO 3: Endpoint de Monitoring (health check agregado)**

**10. `GET /health` - Status de todos os serviços**

```python
@app.route("/health", methods=["GET"])
def health():
    health_status = {
        "gateway": {
            "status": "healthy",
            "service": "api-gateway",
            "port": 8000
        },
        "users_service": {},
        "orders_service": {}
    }
    
    # VERIFICA USERS SERVICE
    try:
        response = requests.get(
            f"{USERS_SERVICE_URL}/health",
            timeout=2
        )
        if response.status_code == 200:
            health_status["users_service"] = {
                "status": "healthy",
                "reachable": True,
                "data": response.json()
            }
        else:
            health_status["users_service"] = {
                "status": "unhealthy",
                "reachable": True,
                "http_code": response.status_code
            }
    except requests.exceptions.RequestException:
        health_status["users_service"] = {
            "status": "unreachable",
            "reachable": False
        }
    
    # VERIFICA ORDERS SERVICE
    try:
        response = requests.get(
            f"{ORDERS_SERVICE_URL}/health",
            timeout=2
        )
        if response.status_code == 200:
            health_status["orders_service"] = {
                "status": "healthy",
                "reachable": True,
                "data": response.json()
            }
        else:
            health_status["orders_service"] = {
                "status": "unhealthy",
                "reachable": True,
                "http_code": response.status_code
            }
    except requests.exceptions.RequestException:
        health_status["orders_service"] = {
            "status": "unreachable",
            "reachable": False
        }
    
    # STATUS GERAL
    all_healthy = (
        health_status["gateway"]["status"] == "healthy" and
        health_status["users_service"].get("status") == "healthy" and
        health_status["orders_service"].get("status") == "healthy"
    )
    
    health_status["overall_status"] = "healthy" if all_healthy else "degraded"
    
    return jsonify(health_status), 200 if all_healthy else 503
```

### 2.5 Comunicação Gateway → Services - Fluxo Detalhado

**Cenário: Cliente solicita usuário com pedidos**

```
1. Cliente (curl/browser)
   ↓
   GET http://localhost:8000/users/1/orders
   ↓
2. API Gateway (Flask app)
   ↓
   [Endpoint get_user_with_orders executa]
   ↓
3. Requisição HTTP #1 (buscar usuário)
   ↓
   requests.get("http://users-service:5001/users/1", timeout=5)
   ↓
4. DNS interno Docker resolve "users-service" → 172.21.0.2
   ↓
5. Requisição roteada pela bridge "microservices-network"
   ↓
6. Users Service (Flask app) recebe
   ↓
   GET /users/1
   ↓
7. Users Service responde:
   {"service": "users-service", "user": {...}}
   ↓
8. Gateway recebe resposta #1
   ↓
9. Requisição HTTP #2 (buscar pedidos do usuário)
   ↓
   requests.get("http://orders-service:5002/orders/user/1", timeout=5)
   ↓
10. DNS resolve "orders-service" → 172.21.0.3
   ↓
11. Orders Service recebe
   ↓
   GET /orders/user/1
   ↓
12. Orders Service responde:
   {"service": "orders-service", "total": 3, "orders": [...]}
   ↓
13. Gateway recebe resposta #2
   ↓
14. Gateway COMBINA ambas respostas:
   {
     "service": "api-gateway (orchestration)",
     "user": {...},
     "orders_summary": {...}
   }
   ↓
15. Cliente recebe resposta agregada
```

**Logs combinados (exemplo real):**

```
api-gateway      | 📥 GET /users/1/orders from 172.21.0.1
api-gateway      | ➡️  Orchestrating request...
api-gateway      | 🔗 GET http://users-service:5001/users/1
users-service    | 📥 GET /users/1 from 172.21.0.4 (api-gateway)
users-service    | ✅ Returning user: Ana Clara Gomes
api-gateway      | ✅ Received user data
api-gateway      | 🔗 GET http://orders-service:5002/orders/user/1
orders-service   | 📥 GET /orders/user/1 from 172.21.0.4 (api-gateway)
orders-service   | ✅ Returning 3 orders for user 1
api-gateway      | ✅ Received orders data
api-gateway      | 🔄 Combining data...
api-gateway      | ✅ Returning orchestrated response (5.2KB)
```

### 2.6 Isolamento dos Microsserviços Backend

**Configuração do docker-compose.yml:**

```yaml
services:
  users-service:
    # SEM ports: - não expõe ao host
    networks:
      - microservices-network
  
  orders-service:
    # SEM ports: - não expõe ao host
    networks:
      - microservices-network
  
  api-gateway:
    ports:
      - "8000:8000"  # ÚNICO ponto de acesso
    networks:
      - microservices-network
```

**Teste de isolamento:**

```bash
# ❌ FALHA: Users Service não é acessível diretamente
curl http://localhost:5001/users
# curl: (7) Failed to connect to localhost port 5001: Connection refused

# ❌ FALHA: Orders Service não é acessível diretamente
curl http://localhost:5002/orders
# curl: (7) Failed to connect to localhost port 5002: Connection refused

# ✅ SUCESSO: Apenas Gateway é acessível
curl http://localhost:8000/users
# {"service": "users-service", "total": 6, ...}
```

**Acessar services de dentro do Gateway:**

```bash
# Entrar no container do gateway
docker exec -it api-gateway /bin/bash

# De dentro do gateway, services são acessíveis via DNS interno
curl http://users-service:5001/users
# {"service": "users-service", ...} ✅

curl http://orders-service:5002/orders
# {"service": "orders-service", ...} ✅

exit
```

### 2.7 Tratamento de Falhas e Resiliência no Gateway

**Cenário 1: Users Service está down**

```python
# Gateway tenta conectar:
response = requests.get(f"{USERS_SERVICE_URL}/users", timeout=5)

# Exceção: requests.exceptions.ConnectionError

# Gateway responde gracefully:
return jsonify({
    "error": "Users service unavailable",
    "message": str(e)
}), 503  # Service Unavailable
```

**Cenário 2: Timeout no Orders Service**

```python
# Timeout após 5 segundos:
response = requests.get(f"{ORDERS_SERVICE_URL}/orders", timeout=5)

# Exceção: requests.exceptions.Timeout

# Gateway não fica travado:
return jsonify({
    "error": "Orders service timeout",
    "message": "Service did not respond in 5 seconds"
}), 503
```

**Cenário 3: Falha na orquestração (um service falha no meio)**

```python
# Orquestração /users/1/orders:
# PASSO 1 sucesso - user obtido
user_response = requests.get(f"{USERS_SERVICE_URL}/users/1")

# PASSO 2 falha - orders service down
orders_response = requests.get(f"{ORDERS_SERVICE_URL}/orders/user/1")
# ConnectionError!

# Gateway captura exceção e retorna erro parcial:
return jsonify({
    "error": "Unable to orchestrate services",
    "message": "Orders service unavailable",
    "partial_data": {
        "user": user_data  # Retorna pelo menos o usuário
    }
}), 503
```

### 2.8 Logs e Observabilidade Centralizada

**Logs esperados - Gateway:**
```
☕ Central Perk API Gateway
🚀 Starting on port 8000...
🔗 Users Service: http://users-service:5001
🔗 Orders Service: http://orders-service:5002
✅ Gateway ready

[Request logs]
172.21.0.1 - - [30/Nov/2025 15:00:00] "GET / HTTP/1.1" 200 -
172.21.0.1 - - [30/Nov/2025 15:00:05] "GET /users HTTP/1.1" 200 -
➡️  Proxying to users-service...
172.21.0.1 - - [30/Nov/2025 15:00:10] "GET /users/1/orders HTTP/1.1" 200 -
➡️  Orchestrating: users + orders...
🔗 GET http://users-service:5001/users/1
🔗 GET http://orders-service:5002/orders/user/1
✅ Orchestration successful (2 services combined)
```

**Logs esperados - Users Service:**
```
👤 Central Perk - Users Service
🚀 Starting on port 5001...
✅ Loaded 6 users
📋 Service ready

[Request logs]
172.21.0.4 - - [30/Nov/2025 15:00:05] "GET /users HTTP/1.1" 200 -
🔗 Request from: api-gateway
172.21.0.4 - - [30/Nov/2025 15:00:10] "GET /users/1 HTTP/1.1" 200 -
✅ Returned user: Ana Clara Gomes
```

**Logs esperados - Orders Service:**
```
📦 Central Perk - Orders Service
🚀 Starting on port 5002...
✅ Loaded 10 orders
📋 Service ready

[Request logs]
172.21.0.4 - - [30/Nov/2025 15:00:10] "GET /orders/user/1 HTTP/1.1" 200 -
🔗 Request from: api-gateway
✅ Returned 3 orders for user 1
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
cd /caminho/para/desafio5
```

**2. Verificar estrutura:**
```bash
ls -la
# Deve conter: docker-compose.yml, gateway/, users-service/, orders-service/
```

**3. Tornar scripts executáveis:**
```bash
chmod +x *.sh
```

### 3.3 Construir e Iniciar Sistema com Gateway

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
Creating network "microservices-network" with driver "bridge"
Creating users-service ... done
Creating orders-service ... done
Creating api-gateway ... done

☕ Central Perk - Sistema iniciado!
🌐 API Gateway: http://localhost:8000
👤 Users Service: interno (não acessível)
📦 Orders Service: interno (não acessível)
```

**Verificar containers:**
```bash
docker-compose ps
```

**Saída esperada:**
```
NAME              STATUS    PORTS
api-gateway       Up        0.0.0.0:8000->8000/tcp
users-service     Up        5001/tcp (internal)
orders-service    Up        5002/tcp (internal)
```

### 3.4 Testar Gateway (Ponto Único de Entrada)

**1. Informações do Gateway:**
```bash
curl http://localhost:8000/ | jq
```

**Resposta:**
```json
{
  "service": "Central Perk API Gateway ☕",
  "version": "1.0.0",
  "description": "Centralized gateway for Central Perk microservices",
  "barista": "Gunther",
  "available_endpoints": {
    "users": [
      "GET /users - List all users",
      "GET /users/<id> - Get user by ID",
      "GET /users/drink/<drink> - Filter by favorite drink"
    ],
    "orders": [
      "GET /orders - List all orders",
      "GET /orders/<id> - Get order by ID",
      "GET /orders/user/<user_id> - Get orders by user",
      "GET /orders/status/<status> - Filter orders by status",
      "GET /orders/category/<category> - Filter by category"
    ],
    "combined": [
      "GET /users/<id>/orders - Get user with their orders",
      "GET /dashboard - Get cafe dashboard with statistics"
    ],
    "health": [
      "GET /health - Health check of all services"
    ]
  }
}
```

### 3.5 Testar Endpoints de Proxy (Users)

**2. Listar todos os clientes (proxy para Users Service):**
```bash
curl http://localhost:8000/users | jq
```

**Resposta:**
```json
{
  "service": "users-service",
  "total": 6,
  "users": [
    {
      "id": 1,
      "name": "Ana Clara Gomes",
      "email": "ana.gomes@centralperk.com",
      "favorite_drink": "Cappuccino",
      "loyalty_points": 150,
      "active": true
    },
    // ... outros 5 usuários
  ]
}
```

**3. Buscar cliente específico:**
```bash
curl http://localhost:8000/users/1 | jq
```

**4. Filtrar clientes por bebida favorita:**
```bash
curl http://localhost:8000/users/drink/cappuccino | jq
```

**Resposta:**
```json
{
  "service": "users-service",
  "drink": "cappuccino",
  "total": 1,
  "users": [
    {
      "id": 1,
      "name": "Ana Clara Gomes",
      "favorite_drink": "Cappuccino"
    }
  ]
}
```

### 3.6 Testar Endpoints de Proxy (Orders)

**5. Listar todos os pedidos:**
```bash
curl http://localhost:8000/orders | jq
```

**Resposta:**
```json
{
  "service": "orders-service",
  "total": 10,
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "user_name": "Ana Clara Gomes",
      "product": "Cappuccino Grande",
      "category": "Bebida Quente",
      "quantity": 2,
      "price": 12.50,
      "status": "delivered"
    },
    // ... outros 9 pedidos
  ]
}
```

**6. Buscar pedido específico:**
```bash
curl http://localhost:8000/orders/1 | jq
```

**7. Filtrar pedidos por status:**
```bash
curl http://localhost:8000/orders/status/delivered | jq
```

**8. Filtrar pedidos por categoria:**
```bash
curl http://localhost:8000/orders/category/bebida-quente | jq
```

### 3.7 Testar Endpoints de Orquestração (Agregação Multi-Service)

**9. Cliente com seus pedidos (ORQUESTRAÇÃO):**
```bash
curl http://localhost:8000/users/1/orders | jq
```

**Resposta (COMBINADA de Users + Orders Services):**
```json
{
  "service": "api-gateway (orchestration)",
  "user": {
    "id": 1,
    "name": "Ana Clara Gomes",
    "email": "ana.gomes@centralperk.com",
    "cpf": "123.456.789-01",
    "member_since": "2023-06-10",
    "favorite_drink": "Cappuccino",
    "loyalty_points": 150,
    "active": true
  },
  "orders_summary": {
    "total_orders": 3,
    "orders": [
      {
        "id": 1,
        "product": "Cappuccino Grande",
        "category": "Bebida Quente",
        "quantity": 2,
        "price": 12.50,
        "status": "delivered",
        "order_date": "2024-11-28 08:30"
      },
      {
        "id": 4,
        "product": "Cheesecake de Frutas Vermelhas",
        "category": "Sobremesa",
        "quantity": 1,
        "price": 18.00,
        "status": "delivered",
        "order_date": "2024-11-29 14:30"
      },
      {
        "id": 10,
        "product": "Brownie com Sorvete",
        "category": "Sobremesa",
        "quantity": 1,
        "price": 20.00,
        "status": "ready",
        "order_date": "2024-11-30 13:30"
      }
    ]
  }
}
```

**10. Dashboard da cafeteria (ORQUESTRAÇÃO COMPLEXA):**
```bash
curl http://localhost:8000/dashboard | jq
```

**Resposta (AGREGADA de Users + Orders Services):**
```json
{
  "service": "api-gateway (dashboard orchestration)",
  "overview": {
    "total_users": 6,
    "total_orders": 10,
    "total_revenue": 135.0,
    "average_order_value": 13.5
  },
  "orders_analysis": {
    "by_status": {
      "delivered": 6,
      "ready": 3,
      "preparing": 1
    },
    "by_category": {
      "Bebida Quente": 6,
      "Sobremesa": 2,
      "Doce": 1,
      "Bebida Gelada": 1
    }
  },
  "most_active_user": {
    "name": "Ana Clara Gomes",
    "total_orders": 3
  }
}
```

### 3.8 Testar Health Check (Monitoring Agregado)

**11. Status de todos os serviços:**
```bash
curl http://localhost:8000/health | jq
```

**Resposta:**
```json
{
  "overall_status": "healthy",
  "gateway": {
    "status": "healthy",
    "service": "api-gateway",
    "port": 8000
  },
  "users_service": {
    "status": "healthy",
    "reachable": true,
    "data": {
      "status": "healthy",
      "service": "users-service",
      "port": 5001,
      "total_users": 6
    }
  },
  "orders_service": {
    "status": "healthy",
    "reachable": true,
    "data": {
      "status": "healthy",
      "service": "orders-service",
      "port": 5002,
      "total_orders": 10
    }
  }
}
```

### 3.9 Validar Isolamento dos Microsserviços Backend

**Teste: Tentar acessar services diretamente (deve falhar)**

```bash
# ❌ Users Service (porta 5001 não exposta)
curl http://localhost:5001/users
# curl: (7) Failed to connect to localhost port 5001: Connection refused

# ❌ Orders Service (porta 5002 não exposta)
curl http://localhost:5002/orders
# curl: (7) Failed to connect to localhost port 5002: Connection refused

# ✅ Apenas Gateway é acessível
curl http://localhost:8000/users | jq '.total'
# 6 ✅
```

**Confirmar que services funcionam internamente:**

```bash
# Entrar no container do gateway
docker exec -it api-gateway /bin/bash

# De dentro do gateway, services são acessíveis
curl http://users-service:5001/users | jq '.total'
# 6 ✅

curl http://orders-service:5002/orders | jq '.total'
# 10 ✅

exit
```

### 3.10 Monitorar Fluxo de Orquestração (Logs em Tempo Real)

**Visualizar logs de todos os serviços:**
```bash
./logs.sh
# OU:
docker-compose logs -f
```

**Em outro terminal, fazer requisição de orquestração:**
```bash
curl http://localhost:8000/users/1/orders
```

**Logs esperados (mostrando fluxo completo):**

```
api-gateway      | 📥 GET /users/1/orders from 172.21.0.1
api-gateway      | ➡️  Starting orchestration...
api-gateway      | 🔗 Request #1: GET http://users-service:5001/users/1
users-service    | 📥 GET /users/1 from 172.21.0.4 (api-gateway)
users-service    | ✅ Returning user: Ana Clara Gomes
api-gateway      | ✅ Received user data (1.2KB)
api-gateway      | 🔗 Request #2: GET http://orders-service:5002/orders/user/1
orders-service   | 📥 GET /orders/user/1 from 172.21.0.4 (api-gateway)
orders-service   | ✅ Returning 3 orders for user 1
api-gateway      | ✅ Received orders data (2.3KB)
api-gateway      | 🔄 Combining data from 2 services...
api-gateway      | ✅ Orchestration complete - returning aggregated response (3.5KB)
```

### 3.11 Testar Resiliência (Falha de Service Backend)

**Cenário: O que acontece se Users Service cai?**

**1. Parar apenas o Users Service:**
```bash
docker stop users-service
```

**2. Tentar acessar usuários via Gateway:**
```bash
curl http://localhost:8000/users
```

**Resposta esperada:**
```json
{
  "error": "Users service unavailable",
  "message": "HTTPConnectionPool(...): Max retries exceeded"
}
```
**HTTP Status: 503 Service Unavailable**

**3. Verificar que Orders ainda funciona:**
```bash
curl http://localhost:8000/orders | jq '.total'
# 10 ✅ (Orders Service independente)
```

**4. Tentar orquestração (deve falhar parcialmente):**
```bash
curl http://localhost:8000/users/1/orders
```

**Resposta:**
```json
{
  "error": "Unable to orchestrate services",
  "message": "Users service unavailable"
}
```

**5. Health check mostra degradação:**
```bash
curl http://localhost:8000/health | jq
```

**Resposta:**
```json
{
  "overall_status": "degraded",
  "gateway": {
    "status": "healthy"
  },
  "users_service": {
    "status": "unreachable",
    "reachable": false
  },
  "orders_service": {
    "status": "healthy",
    "reachable": true
  }
}
```

**6. Restart Users Service:**
```bash
docker start users-service
```

**7. Aguardar 2-3 segundos e testar novamente:**
```bash
curl http://localhost:8000/users | jq '.total'
# 6 ✅ Funcionando novamente!

curl http://localhost:8000/health | jq '.overall_status'
# "healthy" ✅
```

### 3.12 Testar Todos os Endpoints Automaticamente

**Script de testes:**
```bash
./test.sh
```

**O script testa:**

**Endpoints de Proxy (Users):**
1. GET /users
2. GET /users/1
3. GET /users/drink/cappuccino

**Endpoints de Proxy (Orders):**
4. GET /orders
5. GET /orders/1
6. GET /orders/status/delivered
7. GET /orders/category/bebida-quente

**Endpoints de Orquestração:**
8. GET /users/1/orders (combina Users + Orders)
9. GET /dashboard (agregação complexa)

**Endpoint de Monitoring:**
10. GET /health (status de todos serviços)

### 3.13 Inspecionar Rede e Comunicação

**Inspecionar rede Docker:**
```bash
docker network inspect microservices-network
```

**Saída esperada:**
```json
{
  "Containers": {
    "api-gateway": {
      "IPv4Address": "172.21.0.4/16"
    },
    "users-service": {
      "IPv4Address": "172.21.0.2/16"
    },
    "orders-service": {
      "IPv4Address": "172.21.0.3/16"
    }
  }
}
```

**Testar DNS de dentro do Gateway:**
```bash
docker exec api-gateway nslookup users-service
# Name: users-service
# Address: 172.21.0.2 ✅

docker exec api-gateway nslookup orders-service
# Name: orders-service
# Address: 172.21.0.3 ✅
```

### 3.14 Limpar e Reiniciar

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

### 3.15 Troubleshooting

**Problema: Gateway não consegue conectar aos services**
```bash
# Verificar que todos estão na mesma rede
docker network inspect microservices-network

# Verificar DNS funciona
docker exec api-gateway ping users-service
docker exec api-gateway ping orders-service

# Ver logs
docker-compose logs api-gateway
docker-compose logs users-service
docker-compose logs orders-service
```

**Problema: Porta 8000 já em uso**
```bash
# Verificar o que está usando
lsof -i :8000

# Alterar porta no docker-compose.yml
ports:
  - "8080:8000"  # Muda porta do host para 8080
```

**Problema: Timeout ao orquestrar**
```bash
# Aumentar timeout no gateway/app.py:
REQUEST_TIMEOUT = 10  # 10 segundos

# Rebuild
docker-compose build api-gateway
docker-compose up -d
```

**Problema: Services iniciaram antes de estarem prontos**
```bash
# Adicionar healthcheck no docker-compose.yml:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
  interval: 5s
  timeout: 3s
  retries: 3
```

---

## Observações Finais

**✅ API Gateway Pattern:**
Gateway centraliza acesso a microsserviços backend, fornecendo ponto único de entrada, roteamento inteligente e orquestração de serviços.

**✅ Isolamento de Backend:**
Microsserviços Users e Orders não expõem portas ao host. Apenas Gateway é acessível externamente (localhost:8000), simulando ambiente de produção real.

**✅ Orquestração vs Proxy:**
Gateway implementa dois padrões: **proxy simples** (repassa requisições) e **orquestração** (combina dados de múltiplos services em uma resposta agregada).

**✅ Agregação de Dados:**
Endpoints como `/users/<id>/orders` e `/dashboard` demonstram agregação cross-service, retornando dados de Users + Orders em uma única requisição.

**✅ Health Monitoring Centralizado:**
Gateway monitora saúde de todos os services, retornando status agregado. Se um service falha, gateway detecta e reporta `overall_status: degraded`.

**✅ Resiliência e Timeout:**
Gateway implementa timeout de 5 segundos em requisições aos services. Se service não responde, gateway retorna erro 503 ao cliente sem travar.

**✅ Desacoplamento:**
Microsserviços backend podem mudar de localização/porta sem afetar clientes, pois apenas Gateway é visível externamente.

**✅ Comunicação DNS:**
Services descobrem uns aos outros via DNS interno Docker (users-service:5001, orders-service:5002), sem necessidade de IPs fixos.

**✅ Logs Descritivos:**
Todos os serviços geram logs mostrando fluxo de requisições, facilitando debugging e observabilidade centralizada no gateway.

**✅ Comparação com Desafio 4:**
- **Desafio 4**: Microsserviços independentes, ambos expostos ao host
- **Desafio 5**: API Gateway centralizado, backend isolado, apenas gateway exposto
