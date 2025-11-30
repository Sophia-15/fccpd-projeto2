# Projeto 2 - Fundamentos de Computação Concorrente, Paralela e Distribuída

Este repositório é uma coleção de **5 desafios técnicos** desenvolvidos para a disciplina de **Fundamentos de Computação Concorrente, Paralela e Distribuída**, utilizando Docker como plataforma principal para demonstrar princípios de sistemas distribuídos modernos.

## 📖 Visão Geral dos Desafios

### 🔵 Desafio 1: Rede de Comunicação Cliente-Servidor

**Propósito:** Estabelecer comunicação básica entre dois containers através de redes Docker customizadas.

**Tecnologias Exploradas:**
- Criação de redes bridge customizadas
- Resolução DNS interna entre containers
- Servidor Flask respondendo requisições HTTP
- Cliente automatizado consumindo API REST
- Monitoramento de tráfego via logs

**Cenário Prático:** Sistema de cashback onde servidor Flask processa requisições de um cliente Shell, demonstrando comunicação container-to-container via DNS interno Docker.
- PostgreSQL 15 Alpine com volume persistente
- Catalog Manager para popular dados
- Catalog Reader para verificar persistência
- Volume Docker garantindo dados após remoção de containers

**🔗 Acesse:** [`desafio1/`](./desafio1/)

---

### 🟢 Desafio 2: Persistência com PostgreSQL

**Propósito:** Implementar persistência de dados usando volumes Docker nomeados.

**Tecnologias Exploradas:**
- Volumes Docker para persistência além do ciclo de vida dos containers
- PostgreSQL como sistema de gerenciamento de banco relacional
- Scripts Python para popular e consultar dados persistidos
- Sobrevivência de dados após `docker-compose down`
- Manipulação de schemas SQL via containers efêmeros

**Cenário Prático:** Catálogo de fones de ouvido com banco PostgreSQL persistente, onde dados sobrevivem à destruição dos containers.

**🔗 Acesse:** [`desafio2/`](./desafio2/)

---

### 🟡 Desafio 3: Orquestração Multi-Serviço

**Propósito:** Coordenar três serviços interdependentes usando Docker Compose.

**Tecnologias Exploradas:**
- Docker Compose para orquestração declarativa
- API Flask conectada a PostgreSQL e Redis
- Health checks garantindo inicialização ordenada
- Cache com TTL para otimização de performance
- Dependências explícitas entre serviços (`depends_on`)
- Rede privada isolando comunicação interna

**Cenário Prático:** Sistema de músicas com API REST, banco PostgreSQL para persistência e Redis para cache de consultas frequentes.

**🔗 Acesse:** [`desafio3/`](./desafio3/)

---

### 🟠 Desafio 4: Arquitetura de Microsserviços Independentes

**Propósito:** Construir dois microsserviços autônomos que colaboram via comunicação HTTP.

**Tecnologias Exploradas:**
- Separação de responsabilidades (SoC) em microsserviços
- Comunicação síncrona REST entre serviços independentes
- Service discovery via DNS interno Docker
- Tratamento de falhas de comunicação (timeout, retry)
- Enriquecimento de dados cross-service
- Ambos serviços expostos externamente

**Cenário Prático:** Garage Service gerencia inventário de carros, enquanto Analytics Service consome esses dados e gera relatórios enriquecidos com análises de performance e valor.

**🔗 Acesse:** [`desafio4/`](./desafio4/)

---

### 🔴 Desafio 5: API Gateway Centralizado

**Propósito:** Implementar padrão API Gateway como ponto único de entrada para microsserviços backend.

**Tecnologias Exploradas:**
- Gateway como Backend For Frontend (BFF)
- Proxy pattern para roteamento de requisições
- Orquestração multi-service com agregação de dados
- Isolamento de microsserviços backend (sem exposição externa)
- Health monitoring centralizado
- Resiliência com tratamento de falhas parciais

**Cenário Prático:** Central Perk Cafeteria com gateway centralizando acesso a Users Service e Orders Service, oferecendo endpoints de proxy simples e orquestração complexa que combina dados de múltiplos backends.

**🔗 Acesse:** [`desafio5/`](./desafio5/)

---

## 🛠️ Instruções de Execução

Cada desafio é **totalmente independente** e autocontido. Para executar qualquer um deles:

### Preparação Inicial

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd projeto2

# 2. Navegue para o desafio desejado
cd desafio1  # ou desafio2, desafio3, desafio4, desafio5
```

### Execução Rápida

```bash
# 3. Torne os scripts executáveis
chmod +x *.sh

# 4. Inicie o desafio
./start.sh

# 5. Visualize logs em tempo real
./logs.sh

# 6. Execute testes automatizados
./test.sh

# 7. Pare os serviços
./stop.sh
```

### Execução Manual

Se preferir controle total, cada desafio também pode ser executado com comandos Docker Compose diretos:

```bash
# Build das imagens
docker-compose build

# Subir serviços em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar e remover containers
docker-compose down
```

### Documentação Detalhada

**Cada desafio possui um README.md completo** contendo:
- ✅ Explicação arquitetural detalhada
- ✅ Justificativas técnicas para cada decisão de design
- ✅ Diagramas de componentes e fluxo de dados
- ✅ Instruções passo a passo com exemplos
- ✅ Comandos de teste com saídas esperadas
- ✅ Seção de troubleshooting com problemas comuns

## ⚙️ Requisitos do Sistema

### Software Obrigatório

| Software | Versão Mínima | Verificação |
|----------|---------------|-------------|
| Docker Engine | 20.10+ | `docker --version` |
| Docker Compose | 1.29+ | `docker-compose --version` |

### Portas Necessárias

Verifique que as seguintes portas estejam **livres** antes de executar os desafios:

- **Desafio 1:** 5000 (servidor Flask)
- **Desafio 2:** 5432 (PostgreSQL)
- **Desafio 3:** 5000 (API Flask), 5432 (PostgreSQL), 6379 (Redis)
- **Desafio 4:** 5100 (Garage Service), 5101 (Analytics Service)
- **Desafio 5:** 8000 (API Gateway)

```bash
# Verificar se portas estão livres
lsof -i :5000
lsof -i :5432
lsof -i :6379
lsof -i :5100
lsof -i :5101
lsof -i :8000
```

## 📂 Estrutura do Repositório

```
projeto2/
│
├── README.md                    # Este arquivo
│
├── desafio1/                    # Cliente-Servidor com Docker Networking
│   ├── README.md                # Documentação completa
│   ├── docker-compose.yml       # Orquestração (2 serviços)
│   ├── start.sh, stop.sh, logs.sh, test.sh
│   ├── server/                  # Flask API
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   └── requirements.txt
│   └── client/                  # Shell client
│       ├── Dockerfile
│       └── client.sh
│
├── desafio2/                    # Persistência com Volumes
│   ├── README.md
│   ├── docker-compose.yml       # PostgreSQL + 2 scripts Python
│   ├── Dockerfile
│   ├── Dockerfile.reader
│   ├── start.sh, stop.sh, logs.sh, test-persistence.sh
│   └── app/
│       ├── headphones_catalog.py
│       └── reader.py
│
├── desafio3/                    # Orquestração Multi-Serviço
│   ├── README.md
│   ├── docker-compose.yml       # API + PostgreSQL + Redis
│   ├── Dockerfile
│   ├── start.sh, stop.sh, logs.sh, test.sh
│   └── api/
│       ├── app.py
│       └── requirements.txt
│
├── desafio4/                    # Microsserviços Independentes
│   ├── README.md
│   ├── docker-compose.yml       # 2 microsserviços independentes
│   ├── start.sh, stop.sh, logs.sh, test.sh
│   ├── garage-service/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   └── requirements.txt
│   └── analytics-service/
│       ├── Dockerfile
│       ├── app.py
│       └── requirements.txt
│
└── desafio5/                    # API Gateway
    ├── README.md
    ├── docker-compose.yml       # Gateway + 2 backends isolados
    ├── start.sh, stop.sh, logs.sh, test.sh
    ├── gateway/
    │   ├── Dockerfile
    │   ├── app.py
    │   └── requirements.txt
    ├── users-service/
    │   ├── Dockerfile
    │   ├── app.py
    │   └── requirements.txt
    └── orders-service/
        ├── Dockerfile
        ├── app.py
        └── requirements.txt
```

## 🎓 Conceitos de Sistemas Distribuídos Abordados

### Desafio 1: Fundamentos
- Isolamento de processos via containers
- Comunicação inter-processo (IPC) através de rede
- DNS como mecanismo de service discovery básico

### Desafio 2: Estado e Persistência
- Separação entre estado e computação
- Volumes como abstração de storage persistente
- Ciclo de vida independente de dados e containers

### Desafio 3: Coordenação
- Orquestração declarativa via Compose
- Dependências explícitas entre serviços
- Health checks para verificação de prontidão
- Cache distribuído para otimização

### Desafio 4: Microsserviços
- Single Responsibility Principle em serviços
- Comunicação síncrona REST
- Tratamento de falhas parciais
- Independência de deploy e escalabilidade

### Desafio 5: Gateway Pattern
- Backend For Frontend (BFF)
- Agregação de dados cross-service
- Isolamento de backend
- Ponto único de entrada (Single Entry Point)
- Monitoramento centralizado

## Comandos Úteis

```bash
# Ver todos os containers rodando
docker ps

# Ver logs de um container específico
docker logs <container-name> -f

# Executar comando dentro de container
docker exec -it <container-name> /bin/bash

# Limpar sistema Docker completamente
docker system prune -a --volumes
```
