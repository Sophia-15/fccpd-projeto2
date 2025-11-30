# Desafio 4 — Microsserviços Independentes: Forza Garage 🏁

## 📋 Descrição da Solução

Este projeto implementa uma **arquitetura de microsserviços independentes** para gerenciar uma garagem de carros de alta performance, com dois serviços que se comunicam via HTTP:

1. **Garage Service (Microsserviço A)**: API REST que gerencia o inventário de carros na garagem
2. **Analytics Service (Microsserviço B)**: Consome o Garage Service e fornece análises, relatórios e agregações de dados
3. **Comunicação HTTP**: Os microsserviços se comunicam via requisições HTTP sem necessidade de gateway

### 🏁 Tema: Forza Garage

O sistema simula uma garagem profissional de carros de corrida, onde o **Garage Service** mantém o inventário completo de veículos e o **Analytics Service** processa essas informações para gerar relatórios executivos, análises de atividade e insights sobre a coleção.

## 🏗️ Arquitetura de Microsserviços

```
┌─────────────────────────────────────────────────────────────────┐
│              Rede: garage-network (bridge)                      │
│                                                                 │
│  ┌────────────────────────┐       ┌────────────────────────┐  │
│  │   analytics-service    │       │   garage-service       │  │
│  │   (Microsserviço B)    │──────▶│   (Microsserviço A)    │  │
│  │   📊 Analytics API    │ HTTP  │   🏎️ Inventory API     │  │
│  │   Port: 5101           │       │   Port: 5100           │  │
│  │                        │       │                        │  │
│  │   Relatórios           │       │   CRUD de Carros       │  │
│  │   Agregações           │       │   Gestão de Status     │  │
│  │   Análises             │       │   Dados Brutos         │  │
│  └────────────────────────┘       └────────────────────────┘  │
│          ▲                                  ▲                   │
│          │                                  │                   │
└──────────┼──────────────────────────────────┼───────────────────┘
           │                                  │
           │ Port 5101:5101                   │ Port 5100:5100
           │                                  │
      [Host Machine]                    [Host Machine]
http://localhost:5101              http://localhost:5100
```

## 🔧 Componentes Técnicos

### 1. Garage Service - Microsserviço A (garage-service)

**Tecnologia**: Python 3.11 + Flask

**Responsabilidade**: Gerenciar o inventário de carros da garagem

**Funcionalidades**:
- **CRUD Completo**: Criar, ler, atualizar e deletar carros
- **Gestão de Status**: Controla status dos carros (available, racing, maintenance, sold)
- **Armazenamento em Memória**: Dados mantidos em lista Python (simples e direto)
- **API RESTful**: Endpoints padronizados e documentados
- **Validação de Dados**: Verifica integridade dos dados de entrada

**Endpoints**:

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Informações do serviço |
| GET | `/cars` | Lista todos os carros |
| GET | `/cars/<id>` | Busca carro por ID |
| POST | `/cars` | Adiciona novo carro |
| PUT | `/cars/<id>` | Atualiza carro existente |
| DELETE | `/cars/<id>` | Remove carro do inventário |
| GET | `/stats` | Estatísticas básicas do inventário |
| GET | `/health` | Health check do serviço |

**Modelo de Dados**:
```json
{
  "id": 1,
  "manufacturer": "Ferrari",
  "model": "SF90 Stradale",
  "year": 2023,
  "horsepower": 986,
  "top_speed": 211,
  "acceleration": 2.5,
  "price": 625000,
  "status": "available",
  "category": "Hypercar",
  "added_at": "2025-11-30T10:30:00"
}
```

**Status Disponíveis**:
- `available` - Disponível para uso
- `racing` - Em competição
- `maintenance` - Em manutenção
- `sold` - Vendido

**Categorias**:
- `Hypercar` - Carros extremos (900+ HP)
- `Supercar` - Alta performance (700-899 HP)
- `Sports` - Esportivos (500-699 HP)
- `Luxury` - Luxo e conforto (300-499 HP)

**Inventário Inicial** (10 carros):

| Fabricante | Modelo | Ano | HP | Vel. Máx | Categoria | Status | Preço |
|------------|--------|-----|----|-----------| ----------|--------|-------|
| Ferrari | SF90 Stradale | 2023 | 986 | 211 mph | Hypercar | available | $625,000 |
| Lamborghini | Revuelto | 2024 | 1001 | 217 mph | Hypercar | available | $608,000 |
| Porsche | 911 GT3 RS | 2023 | 518 | 184 mph | Sports | racing | $241,000 |
| McLaren | 720S | 2023 | 710 | 212 mph | Supercar | available | $310,000 |
| Aston Martin | DBS Superleggera | 2023 | 715 | 211 mph | Supercar | maintenance | $316,000 |
| Mercedes-AMG | GT Black Series | 2023 | 720 | 202 mph | Supercar | available | $325,000 |
| Chevrolet | Corvette Z06 | 2023 | 670 | 194 mph | Sports | available | $106,000 |
| Audi | R8 V10 | 2023 | 602 | 205 mph | Sports | available | $148,000 |
| BMW | M8 Competition | 2023 | 617 | 190 mph | Sports | sold | $133,000 |
| Nissan | GT-R Nismo | 2023 | 600 | 196 mph | Sports | available | $215,000 |

### 2. Analytics Service - Microsserviço B (analytics-service)

**Tecnologia**: Python 3.11 + Flask + requests

**Responsabilidade**: Consumir o Garage Service e fornecer análises agregadas e relatórios

**Funcionalidades**:
- **Relatórios Completos**: Gera relatórios detalhados de todos os carros
- **Relatórios Individuais**: Análise detalhada de um carro específico
- **Resumo Executivo**: Agregações e insights da garagem
- **Análise de Atividade**: Processa dados e calcula métricas de performance
- **Health Check Integrado**: Verifica próprio status e do Garage Service
- **Tratamento de Erros**: Gerencia falhas de comunicação com graciosidade

**Endpoints**:

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Informações do serviço |
| GET | `/report` | Relatório completo de todos os carros |
| GET | `/report/<id>` | Relatório detalhado de um carro específico |
| GET | `/summary` | Resumo executivo agregado |
| GET | `/activity` | Análise de atividade processada |
| GET | `/health` | Health check (verifica também o Garage Service) |

**Funcionalidades de Análise**:

#### 📋 GET `/report` - Relatório Completo
Retorna lista completa de carros com enriquecimento de dados:
- **Classificação de Preço**: Economy, Mid-range, Luxury, Ultra-luxury
- **Classificação de Performance**: Standard, High, Extreme
- **Cálculo de Valor**: Valor por HP, análise de custo-benefício
- **Tempo Desde Adição**: Dias na garagem

```json
{
  "service": "Analytics Service",
  "report_type": "complete",
  "total_cars": 10,
  "timestamp": "2025-11-30T10:30:00",
  "cars": [
    {
      "id": 1,
      "manufacturer": "Ferrari",
      "model": "SF90 Stradale",
      "analytics": {
        "price_class": "Ultra-luxury",
        "performance_class": "Extreme",
        "value_per_hp": 633.67,
        "days_in_garage": 15,
        "status_analysis": "Ready for use"
      }
    }
  ]
}
```

#### 🔍 GET `/report/<id>` - Relatório Individual
Análise profunda de um carro específico:
- **Scores de Performance**: Aceleração, velocidade, potência
- **Posicionamento**: Ranking na garagem
- **Comparação**: Vs. média da categoria
- **Recomendações**: Insights baseados nos dados

```json
{
  "car_id": 1,
  "manufacturer": "Ferrari",
  "model": "SF90 Stradale",
  "detailed_analysis": {
    "performance_score": 95.2,
    "acceleration_score": 98,
    "speed_score": 92,
    "power_score": 96,
    "ranking_in_garage": 2,
    "category_comparison": {
      "vs_category_avg_hp": "+23.5%",
      "vs_category_avg_speed": "+8.2%"
    },
    "recommendations": [
      "Excellent power-to-weight ratio",
      "Top acceleration in category",
      "Premium value retention"
    ]
  }
}
```

#### 📊 GET `/summary` - Resumo Executivo
Agregações e estatísticas da garagem completa:
- **Valor Total**: Inventário completo
- **Médias**: HP, velocidade, preço, aceleração
- **Distribuições**: Por categoria, status, fabricante
- **Rankings**: Top 3 em cada métrica
- **Insights**: Análises automáticas

```json
{
  "summary_type": "executive",
  "timestamp": "2025-11-30T10:30:00",
  "overview": {
    "total_cars": 10,
    "total_value": 3027000,
    "avg_horsepower": 713.9,
    "avg_top_speed": 202.7,
    "avg_price": 302700,
    "avg_acceleration": 2.89
  },
  "by_category": {
    "Hypercar": {"count": 2, "avg_hp": 993.5},
    "Supercar": {"count": 3, "avg_hp": 715.0},
    "Sports": {"count": 5, "avg_hp": 601.4}
  },
  "by_status": {
    "available": 6,
    "racing": 1,
    "maintenance": 1,
    "sold": 1
  },
  "top_performers": {
    "most_powerful": "Lamborghini Revuelto (1001 HP)",
    "fastest": "Lamborghini Revuelto (217 mph)",
    "quickest": "Ferrari SF90 Stradale (2.5s 0-60)"
  }
}
```

#### 📈 GET `/activity` - Análise de Atividade
Processa dados e gera métricas de utilização:
- **Taxa de Utilização**: % de carros em uso
- **Eficiência da Garagem**: Métricas operacionais
- **Análise de Categorias**: Performance por tipo
- **Alertas**: Carros que precisam atenção

```json
{
  "activity_type": "operational",
  "utilization": {
    "active_cars": 7,
    "inactive_cars": 3,
    "utilization_rate": 70.0,
    "racing_count": 1,
    "maintenance_count": 1
  },
  "efficiency_metrics": {
    "avg_hp_per_available_car": 728.5,
    "total_racing_power": 518,
    "maintenance_backlog": 1
  },
  "category_analysis": {
    "Hypercar": {
      "total": 2,
      "available": 2,
      "availability_rate": 100.0
    }
  },
  "alerts": [
    "1 car in maintenance needs attention",
    "High-value inventory available (6 cars)"
  ]
}
```

#### 🏥 GET `/health` - Health Check Integrado
Verifica status de ambos os microsserviços:
- **Analytics Service**: Status próprio
- **Garage Service**: Status via HTTP request
- **Conectividade**: Testa comunicação
- **Latência**: Mede tempo de resposta

```json
{
  "analytics_service": "healthy",
  "garage_service": "healthy",
  "connectivity": "ok",
  "latency_ms": 45,
  "timestamp": "2025-11-30T10:30:00"
}
```

### 3. Comunicação HTTP Entre Microsserviços

**Padrão de Comunicação**:
- Analytics Service faz requisições HTTP ao Garage Service
- Sem gateway ou proxy intermediário
- Descoberta via nome DNS do Docker (garage-service:5100)
- Timeout configurado (5 segundos)
- Retry logic para resiliência

**Fluxo de Requisição**:
```
Cliente HTTP
    │
    ▼
Analytics Service (port 5101)
    │
    │ requests.get("http://garage-service:5100/cars")
    ▼
Garage Service (port 5100)
    │
    │ Processa requisição
    │ Retorna JSON
    ▼
Analytics Service
    │
    │ Processa dados
    │ Adiciona análises
    │ Retorna relatório
    ▼
Cliente HTTP
```

## 📦 Estrutura de Arquivos

```
desafio4/
├── README.md                      # Este arquivo
├── docker-compose.yml             # Orquestração dos microsserviços
├── start.sh                       # Script para iniciar
├── stop.sh                        # Script para parar
├── test.sh                        # Script para testar
├── logs.sh                        # Script para ver logs
├── garage-service/                # Microsserviço A
│   ├── Dockerfile                 # Container do Garage Service
│   ├── app.py                     # API Flask (Inventory)
│   └── requirements.txt           # Dependências Python
└── analytics-service/             # Microsserviço B
    ├── Dockerfile                 # Container do Analytics Service
    ├── app.py                     # API Flask (Analytics)
    └── requirements.txt           # Dependências Python
```

## 🚀 Como Executar

### Iniciar os Microsserviços

```bash
./start.sh
```

Isso irá:
1. Construir as imagens Docker dos dois microsserviços
2. Criar a rede `garage-network`
3. Iniciar os containers em background
4. Exibir URLs e informações dos serviços

### Testar os Endpoints

```bash
./test.sh
```

Isso irá testar todos os endpoints de ambos os microsserviços:
- **Garage Service**: Operações CRUD e estatísticas
- **Analytics Service**: Relatórios e análises
- **Comunicação**: Verifica integração entre serviços

### Ver Logs em Tempo Real

```bash
./logs.sh
```

Exibe logs de ambos os microsserviços simultaneamente.

### Parar os Microsserviços

```bash
./stop.sh
```

Remove os containers e a rede Docker.

## 🎯 Demonstração da Comunicação Entre Microsserviços

Para demonstrar como o **Analytics Service** consome o **Garage Service**:

1. **Inicie os serviços**:
```bash
./start.sh
```

2. **Faça uma requisição ao Analytics Service**:
```bash
curl http://localhost:5101/summary
```

3. **Observe nos logs** (em outro terminal):
```bash
./logs.sh
```

Você verá:
- **Analytics Service**: Recebe requisição do cliente
- **Analytics Service**: Faz requisição HTTP ao Garage Service
- **Garage Service**: Processa e retorna dados
- **Analytics Service**: Processa dados e adiciona análises
- **Analytics Service**: Retorna resposta ao cliente

## 🔧 Detalhes de Implementação

### Docker Compose - Orquestração
```yaml
services:
  garage-service:
    build: ./garage-service
    ports: ["5100:5100"]
    networks: [garage-network]
  
  analytics-service:
    build: ./analytics-service
    ports: ["5101:5101"]
    networks: [garage-network]
    depends_on: [garage-service]
```

