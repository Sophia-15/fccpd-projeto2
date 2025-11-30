# Desafio 2 — Volumes e Persistência: AudioFile Vault 🎧

## 📋 Descrição da Solução

Este projeto implementa um **catálogo profissional de fones de ouvido para audiófilos**, utilizando três containers Docker e um volume persistente:

1. **Banco de Dados (PostgreSQL)**: Armazena especificações técnicas detalhadas de headphones premium
2. **Catalog Manager**: Popula e gerencia os dados do catálogo
3. **Catalog Reader**: Lê e verifica os dados persistidos
4. **Volume Docker**: Garante que os dados sobrevivam à remoção dos containers

### 🎵 Tema: Catálogo Audiófilo

O sistema mantém um inventário detalhado de fones de ouvido premium, com especificações técnicas reais como impedância, drivers, sensibilidade e assinatura sonora. Ideal para entusiastas de áudio que buscam informações precisas sobre equipamentos high-end.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│              Rede: desafio2-network (bridge)                    │
│                                                                 │
│  ┌────────────────────────┐       ┌────────────────────────┐  │
│  │   headphones-catalog   │       │   headphones-postgres  │  │
│  │   (Popula dados)       │──────▶│   🗄️ PostgreSQL 15    │  │
│  │   🐍 Python + psycopg2│       │   Port: 5432           │  │
│  └────────────────────────┘       │   DB: headphones_db    │  │
│                                   └──────────┬─────────────┘  │
│  ┌────────────────────────┐                 │                 │
│  │   headphones-reader    │                 │                 │
│  │   (Lê dados)           │─────────────────┘                 │
│  │   📖 Python + psycopg2│                                    │
│  └────────────────────────┘                                   │
│                                    │                           │
└────────────────────────────────────┼───────────────────────────┘
                                     │
                          💾 desafio2-postgres-data
                               (Docker Volume)
                        /var/lib/postgresql/data
                              ↓
                    Dados persistem após remoção
                        dos containers!
```

## 🔧 Componentes Técnicos

### 1. Banco de Dados - PostgreSQL (headphones-postgres)

**Tecnologia**: PostgreSQL 15 Alpine

**Funcionalidades**:
- **Volume Persistente**: Dados armazenados em volume Docker externo
- **Health Check**: Monitora disponibilidade do banco
- **Schema Completo**: 13 campos técnicos por headphone
- **Isolamento**: Rede privada para segurança

**Configuração**:
- Database: `headphones_db`
- User: `postgres`
- Password: `postgres`
- Port: `5432`

**Schema da Tabela**:
```sql
CREATE TABLE headphones (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    driver_size INTEGER,
    impedance INTEGER,
    sensitivity INTEGER,
    frequency_response VARCHAR(50),
    cable_type VARCHAR(100),
    weight INTEGER,
    price DECIMAL(10, 2),
    sound_signature VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Catalog Manager - Gerenciamento de Dados (headphones-catalog)

**Tecnologia**: Python 3.11 + psycopg2

**Funcionalidades**:
- Inicializa o banco de dados
- Popula com 8 fones premium
- Exibe catálogo completo
- Gera estatísticas
- Retry logic para aguardar banco

**Catálogo Inicial** (8 fones premium):

| Marca | Modelo | Preço | Impedância | Tipo |
|-------|--------|-------|------------|------|
| Sennheiser | HD 800 S | $1,699.99 | 300Ω | Open-back |
| Focal | Clear MG | $1,490.00 | 55Ω | Open-back |
| Audeze | LCD-X | $1,199.00 | 20Ω | Open-back (Planar) |
| Beyerdynamic | DT 1990 Pro | $599.00 | 250Ω | Open-back |
| HiFiMAN | Arya Stealth | $1,299.00 | 32Ω | Open-back (Planar) |
| AKG | K701 | $249.00 | 62Ω | Open-back |
| Audio-Technica | ATH-M50x | $149.00 | 38Ω | Closed-back |
| Sony | MDR-Z7M2 | $899.00 | 70Ω | Closed-back |

**Especificações Técnicas**:
- Driver Size: Tamanho do driver em mm
- Impedance: Impedância em Ohms (afeta amplificação necessária)
- Sensitivity: Sensibilidade em dB (eficiência)
- Frequency Response: Faixa de resposta (ex: 4Hz - 51kHz)
- Cable Type: Tipo de cabo (destacável, fixo, balanceado)
- Sound Signature: Perfil sonoro (Neutral, Bright, Warm, V-shaped)

### 3. Catalog Reader - Leitura de Dados (headphones-reader)

**Tecnologia**: Python 3.11 + psycopg2

**Funcionalidades**:
- Conecta ao mesmo banco de dados
- Lê todos os dados persistidos
- Exibe resumo estatístico
- Verifica integridade dos dados
- Comprova persistência

**Estatísticas Geradas**:
- Total de fones cadastrados
- Preço médio do catálogo
- Fone mais barato / mais caro
- Listagem completa com specs

### 4. Volume Docker - Persistência

**Nome**: `desafio2-postgres-data`  
**Driver**: local  
**Montagem**: `/var/lib/postgresql/data`  
**Características**:
- Dados independentes dos containers
- Sobrevive a `docker compose down`
- Apenas removido com flag `-v`
- Isolado do filesystem do container

## 🎮 Como Funciona

### Fluxo de Dados

1. **Inicialização**:
   - PostgreSQL inicia e cria volume persistente
   - Health check garante que banco está pronto
   - Catalog Manager aguarda disponibilidade (retry logic)

2. **População**:
   - Catalog Manager conecta ao banco
   - Cria tabela `headphones` se não existir
   - Verifica se dados já existem
   - Popula com 8 fones premium (se vazio)
   - Exibe catálogo completo

3. **Leitura**:
   - Catalog Reader conecta ao banco
   - Lê todos os registros
   - Calcula estatísticas (média, min, max)
   - Exibe dados formatados

4. **Persistência**:
   - Dados ficam no volume Docker
   - Containers podem ser removidos
   - Volume permanece intacto
   - Ao recriar containers, dados continuam lá

### Sistema de Persistência

- **Volume Nomeado**: `desafio2-postgres-data` facilita identificação
- **Localização Host**: `/var/lib/docker/volumes/desafio2-postgres-data`
- **Lifecycle**: Independente dos containers
- **Compartilhamento**: Múltiplos containers podem montar o mesmo volume
- **Backup**: Pode ser copiado/exportado do host

## 📦 Estrutura de Arquivos

```
desafio2/
├── docker compose .yml          # Orquestração dos serviços + volume
├── README.md                   # Esta documentação
├── start.sh                    # Inicia o catálogo
├── stop.sh                     # Para os containers (mantém volume)
├── logs.sh                     # Visualiza logs dos containers
├── test-persistence.sh         # Testa persistência dos dados
├── app/
│   ├── headphones_catalog.py  # Script de gerenciamento
│   └── reader.py              # Script de leitura
├── Dockerfile                  # Imagem do Catalog Manager
└── Dockerfile.reader          # Imagem do Catalog Reader
```

## 🚀 Instruções de Execução

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Sistema: Linux, macOS ou Windows com WSL2

### Passo 1: Acessar o Projeto

```bash
cd desafio2
```

### Passo 2: Dar Permissões aos Scripts

```bash
chmod +x *.sh
```

### Passo 3: Iniciar o Catálogo

```bash
./start.sh
```

**Saída esperada**:
```
Iniciando Desafio 2 - Docker Volumes e Persistencia
==================================================
Construindo imagens Docker...
[+] Building 8.3s

Iniciando containers...
[+] Running 4/4
 ✔ Network desafio2-network          Created
 ✔ Volume desafio2-postgres-data     Created
 ✔ Container headphones-postgres     Started
 ✔ Container headphones-catalog      Started
 ✔ Container headphones-reader       Started

Containers iniciados!

Status dos containers:
NAME                   IMAGE              STATUS
headphones-postgres    postgres:15-alpine healthy
headphones-catalog     desafio2-catalog   exited
headphones-reader      desafio2-reader    exited

Volume criado:
desafio2-postgres-data

==================================================
Desafio 2 rodando!
==================================================
```

### Passo 4: Ver Logs dos Containers

```bash
./logs.sh
```

**Exemplo de logs**:
```
Container: postgres
---------------------------------
PostgreSQL init process complete; ready for start up.
LOG: database system is ready to accept connections

Container: headphones-catalog
---------------------------------
================================================================================
SISTEMA DE CATALOGO DE FONES DE OUVIDO AUDIOFILO
================================================================================
Banco de dados: postgres:5432/headphones_db

Banco de dados inicializado: postgres:5432/headphones_db

Fones no catalogo: 0

Catalogo vazio. Adicionando dados de exemplo...
Fone adicionado: Sennheiser HD 800 S (ID: 1)
Fone adicionado: Focal Clear MG (ID: 2)
...

Container: headphones-reader
--------------------------------
================================================================================
LENDO CATALOGO DE FONES DE OUVIDO (CONTAINER LEITOR)
================================================================================
Conectando a: postgres:5432/headphones_db

Total de fones encontrados: 8

01 | Sennheiser HD 800 S
   Open-back Over-ear
   56mm | 300ohms | 102dB
   $1699.99 | Neutral/Analytical
...
```

### Passo 5: Testar Persistência

```bash
./test-persistence.sh
```

Este script **demonstra a persistência** através dos seguintes passos:

1. Cria dados iniciais no banco
2. **Remove os containers da aplicação** (catalog e reader)
3. Verifica que o volume ainda existe
4. Recria os containers
5. **Comprova que os mesmos dados continuam lá!**

**Saída esperada**:
```
TESTE DE PERSISTENCIA - Desafio 2
==================================================

PASSO 1: Criando dados iniciais...
(8 fones adicionados)

Pressione Enter para continuar...

PASSO 2: Removendo containers da aplicacao...
headphones-catalog
headphones-reader
Containers da aplicacao removidos!

Pressione Enter para continuar...

PASSO 3: Verificando que o volume ainda existe...
local     desafio2-postgres-data

Pressione Enter para continuar...

PASSO 4: Recriando os containers da aplicacao...
Container headphones-catalog  Started
Container headphones-reader   Started

PASSO 5: Verificando que os dados PERSISTIRAM...
==================================================
Total de fones encontrados: 8
(mesmos 8 fones aparecem!)
==================================================

SUCESSO! Os dados sobreviveram a remocao dos containers!
```

### Passo 6: Parar os Containers

```bash
./stop.sh
```

**Importante**: Este comando para os containers mas **mantém o volume**. Os dados permanecem salvos.

Para remover também o volume (apagar dados):
```bash
docker compose down -v
```

## 🧪 Exemplos de Saída

### Exemplo 1: Catalog Manager (População)

```
================================================================================
SISTEMA DE CATALOGO DE FONES DE OUVIDO AUDIOFILO
================================================================================
Banco de dados: postgres:5432/headphones_db

Banco de dados inicializado: postgres:5432/headphones_db

Fones no catalogo: 0

Catalogo vazio. Adicionando dados de exemplo...

Adicionando fones de exemplo ao catalogo...
Fone adicionado: Sennheiser HD 800 S (ID: 1)
Fone adicionado: Focal Clear MG (ID: 2)
Fone adicionado: Audeze LCD-X (ID: 3)
Fone adicionado: Beyerdynamic DT 1990 Pro (ID: 4)
Fone adicionado: HiFiMAN Arya Stealth (ID: 5)
Fone adicionado: AKG K701 (ID: 6)
Fone adicionado: Audio-Technica ATH-M50x (ID: 7)
Fone adicionado: Sony MDR-Z7M2 (ID: 8)

Dados de exemplo adicionados com sucesso!

====================================================================================================
CATALOGO DE FONES DE OUVIDO AUDIOFILO
====================================================================================================

ID: 1
Marca/Modelo: Sennheiser HD 800 S
Tipo: Open-back Over-ear
Driver: 56mm | Impedancia: 300ohms | Sensibilidade: 102dB
Resposta de Frequencia: 4Hz - 51kHz
Cabo: Detachable 6.3mm
Peso: 330g
Preco: $1699.99
Assinatura Sonora: Neutral/Analytical
Notas: Flagship open-back
Adicionado em: 2025-11-18 10:30:15.123456
----------------------------------------------------------------------------------------------------

ID: 2
Marca/Modelo: Focal Clear MG
Tipo: Open-back Over-ear
Driver: 40mm | Impedancia: 55ohms | Sensibilidade: 104dB
Resposta de Frequencia: 5Hz - 28kHz
Cabo: Detachable 3.5mm/6.3mm
Peso: 450g
Preco: $1490.00
Assinatura Sonora: Balanced/Slightly Warm
Notas: Magnesium drivers
Adicionado em: 2025-11-18 10:30:15.234567
----------------------------------------------------------------------------------------------------

================================================================================
ESTATISTICAS DO CATALOGO
================================================================================
Total de fones: 8
Preco medio: $1035.62
Impedancia media: 103ohms

Tipos:
   Open-back Over-ear: 6
   Closed-back Over-ear: 2

Marcas:
   Sennheiser: 1
   Focal: 1
   Audeze: 1
   Beyerdynamic: 1
   HiFiMAN: 1
   AKG: 1
   Audio-Technica: 1
   Sony: 1
================================================================================

Sistema executado com sucesso!
Os dados foram salvos no PostgreSQL: postgres/headphones_db
Mesmo removendo o container da aplicacao, os dados permanecerao no volume Docker
================================================================================
```

### Exemplo 2: Catalog Reader (Leitura)

```
================================================================================
LENDO CATALOGO DE FONES DE OUVIDO (CONTAINER LEITOR)
================================================================================
Conectando a: postgres:5432/headphones_db

Total de fones encontrados: 8

================================================================================
LISTA DE FONES PERSISTIDOS
================================================================================

01 | Sennheiser HD 800 S
   Open-back Over-ear
   56mm | 300ohms | 102dB
   $1699.99 | Neutral/Analytical

02 | Focal Clear MG
   Open-back Over-ear
   40mm | 55ohms | 104dB
   $1490.00 | Balanced/Slightly Warm

03 | Audeze LCD-X
   Open-back Over-ear
   106mm | 20ohms | 103dB
   $1199.00 | Neutral

04 | Beyerdynamic DT 1990 Pro
   Open-back Over-ear
   45mm | 250ohms | 102dB
   $599.00 | Bright/Analytical

05 | HiFiMAN Arya Stealth
   Open-back Over-ear
   0mm | 32ohms | 94dB
   $1299.00 | Neutral/Natural

06 | AKG K701
   Open-back Over-ear
   44mm | 62ohms | 105dB
   $249.00 | Neutral

07 | Audio-Technica ATH-M50x
   Closed-back Over-ear
   45mm | 38ohms | 99dB
   $149.00 | V-Shaped

08 | Sony MDR-Z7M2
   Closed-back Over-ear
   70mm | 70ohms | 98dB
   $899.00 | Warm

================================================================================
RESUMO ESTATISTICO
================================================================================
Preco medio: $1035.62
Mais barato: $149.00
Mais caro: $1699.99
================================================================================

Dados lidos com sucesso do banco persistente!
Estes dados sobrevivem a remocao dos containers da aplicacao
================================================================================
```

## 🔧 Explicação Técnica

### Docker Compose - Orquestração dos Serviços

O arquivo `docker compose .yml` define toda a infraestrutura:

**Pontos-chave**:
- `volumes` define o volume persistente que sobrevive aos containers
- `healthcheck` garante que o banco está pronto antes dos apps rodarem
- `depends_on` com `condition` aguarda health check
- DNS interno resolve `postgres` para o IP do container
- Variáveis de ambiente passam credenciais de forma segura

### Dockerfile do Catalog Manager


**Funcionamento**: Container executa script Python que conecta ao PostgreSQL, cria tabela, popula dados e exibe estatísticas.

### Dockerfile do Catalog Reader

**Funcionamento**: Container executa script Python que conecta ao PostgreSQL, lê todos os dados e exibe estatísticas.

### Comunicação entre Containers

```
┌─────────────────────┐                          ┌─────────────────────┐
│  headphones-catalog │ ─── psycopg2 connect ──▶ │ headphones-postgres │
│  (Python)           │                          │ (PostgreSQL)        │
│  172.20.0.3         │ ◀── Query Results ────── │ 172.20.0.2:5432    │
└─────────────────────┘                          └──────────┬──────────┘
                                                            │
┌─────────────────────┐                                     │
│  headphones-reader  │ ─── psycopg2 connect ──────────────┘
│  (Python)           │                          
│  172.20.0.4         │ ◀── Query Results ──────────────────┘
└─────────────────────┘

                            Volume persistente
                      desafio2-postgres-data
                   /var/lib/postgresql/data
                            ↓
                   Dados permanecem mesmo
                   removendo containers!
```

1. PostgreSQL inicia e monta o volume
2. Catalog Manager aguarda health check
3. Manager conecta, cria tabela e popula dados
4. Reader conecta e lê dados persistidos
5. Dados ficam no volume, não nos containers

### Retry Logic - Conexão Resiliente

**Funcionamento**: Tenta conectar até 30 vezes com intervalo de 1 segundo. Garante que o banco esteja pronto antes de processar dados.

