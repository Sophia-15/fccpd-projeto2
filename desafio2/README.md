# Desafio 2 — Volumes e Persistência: AudioFile Vault 🎧

## 1. Descrição Geral da Solução

### 1.1 Proposta do Desafio

Este desafio demonstra o uso de **volumes Docker para persistência de dados**. O objetivo é criar um sistema onde dados gravados em um banco de dados PostgreSQL sobrevivem à remoção e recriação dos containers, garantindo que informações não sejam perdidas mesmo após `docker-compose down`.

A implementação explora conceitos essenciais de Docker: volumes nomeados, ciclo de vida de dados independente dos containers, e a diferença crucial entre armazenamento efêmero (dentro do container) e persistente (volumes externos).

### 1.2 Arquitetura Utilizada

A solução é composta por **quatro componentes principais**:

**1. Container PostgreSQL (headphones-postgres)**
- **Imagem base**: postgres:15-alpine
- **Função**: Banco de dados relacional que armazena catálogo de fones de ouvido
- **Porta interna**: 5432 (NÃO exposta ao host - comunicação apenas interna)
- **Armazenamento**: Volume Docker montado em `/var/lib/postgresql/data`
- **Health Check**: Verifica disponibilidade com `pg_isready`

**2. Container Catalog Manager (headphones-catalog)**
- **Imagem base**: Python 3.11-slim
- **Framework**: psycopg2 (driver PostgreSQL para Python)
- **Função**: Inicializa banco, popula com 8 fones premium, exibe catálogo e estatísticas
- **Comportamento**: Executa uma vez e encerra (não fica em loop)
- **Retry Logic**: Aguarda até 30 segundos para PostgreSQL ficar pronto

**3. Container Catalog Reader (headphones-reader)**
- **Imagem base**: Python 3.11-slim
- **Função**: Lê e verifica dados persistidos no banco
- **Objetivo**: Demonstrar que dados ainda existem após reinicialização

**4. Volume Docker (postgres-data)**
- **Tipo**: Volume nomeado (gerenciado pelo Docker)
- **Montagem**: `/var/lib/postgresql/data` (diretório padrão do PostgreSQL)
- **Característica chave**: **Sobrevive a `docker-compose down`**
- **Localização física**: `/var/lib/docker/volumes/postgres-data/_data` (no host)

### 1.3 Decisões Técnicas e Justificativas

**Por que PostgreSQL?**
PostgreSQL é um banco de dados robusto, open-source e amplamente usado em produção. A versão Alpine (15-alpine) foi escolhida por ser mínima (~80MB vs ~350MB da versão padrão), demonstrando boas práticas de otimização de imagens Docker.

**Por que psycopg2?**
Psycopg2 é o driver PostgreSQL mais usado em Python, maduro e eficiente. Possui suporte completo a tipos PostgreSQL e é mais rápido que alternativas asyncpg para casos síncronos simples.

**Por que um volume nomeado (não bind mount)?**
Volumes nomeados são gerenciados pelo Docker e funcionam consistentemente em Linux, macOS e Windows. Bind mounts dependem de caminhos do host e podem ter problemas de permissão. Para dados de banco, volumes nomeados são best practice.

**Por que a porta 5432 NÃO está mapeada para o host?**
Não há necessidade de acesso externo ao PostgreSQL neste desafio. Manter a porta apenas na rede interna é uma **boa prática de segurança**: reduz a superfície de ataque e evita conflitos de porta no host.

**Por que retry logic no Catalog Manager?**
`depends_on` garante apenas que o container PostgreSQL **iniciou**, não que o servidor está pronto para aceitar conexões. O retry loop aguarda até o banco estar realmente operacional antes de tentar a conexão.

**Organização do projeto:**
```
desafio2/
├── docker-compose.yml          # Orquestração (3 containers + 1 volume)
├── Dockerfile                  # Build do Catalog Manager
├── Dockerfile.reader           # Build do Catalog Reader
├── start.sh, stop.sh, logs.sh  # Scripts de gerenciamento
├── test-persistence.sh         # Testa persistência de dados
└── app/
    ├── headphones_catalog.py   # Popula banco com catálogo
    └── reader.py               # Lê dados do banco
```

### 1.4 Tema: AudioFile Vault

O sistema gerencia um **catálogo profissional de fones de ouvido para audiófilos**, com especificações técnicas reais:

**8 Fones Premium Cadastrados:**
- Sennheiser HD 800 S ($1,699.99) - 300Ω - Open-back
- Focal Clear MG ($1,490.00) - 55Ω - Open-back
- Audeze LCD-X ($1,199.00) - 20Ω - Planar Magnetic
- Beyerdynamic DT 1990 Pro ($599.00) - 250Ω - Open-back
- Hifiman Arya ($1,299.00) - 35Ω - Planar Magnetic
- Audio-Technica ATH-R70x ($349.00) - 470Ω - Open-back
- AKG K702 ($199.00) - 62Ω - Open-back
- Shure SRH1840 ($699.00) - 65Ω - Open-back

**13 Campos Técnicos por Headphone:**
- Marca, modelo, tipo (open-back/closed-back/planar)
- Tamanho do driver (mm), impedância (Ω), sensibilidade (dB)
- Resposta de frequência, tipo de cabo
- Peso (gramas), preço, assinatura sonora
- Notas adicionais, timestamp de criação

## 2. Explicação Detalhada do Funcionamento

### 2.1 Fluxo Completo de Inicialização

**1. Docker Compose Sobe os Serviços:**
```bash
docker-compose up -d
```

**Ordem de inicialização (definida por `depends_on` e `condition`):**
```
postgres (com healthcheck)
    ↓ (aguarda status healthy)
headphones-catalog
    ↓ (aguarda término da execução)
headphones-reader
```

**2. PostgreSQL Inicializa:**
- Container `headphones-postgres` inicia
- PostgreSQL cria diretórios em `/var/lib/postgresql/data`
- Estes dados são gravados no volume `postgres-data` (não no container)
- Health check executa `pg_isready -U postgres` a cada 5s
- Após 5 verificações bem-sucedidas, status = `healthy`

**3. Catalog Manager Executa:**
- Aguarda PostgreSQL ficar `healthy`
- Conecta ao banco: `host=postgres, port=5432, database=headphones_db`
- Executa `init_database()`: cria tabela `headphones` se não existir
- Verifica se tabela está vazia (`SELECT COUNT(*)`)
- Se vazia: popula com 8 fones premium
- Se já tem dados: exibe mensagem "Database already populated"
- Imprime catálogo completo formatado
- Gera estatísticas (preço médio, impedância média, etc.)
- Container encerra (exit code 0)

**4. Catalog Reader Executa:**
- Conecta ao mesmo banco
- Lê todos os registros: `SELECT * FROM headphones ORDER BY price DESC`
- Exibe catálogo ordenado por preço (mais caro primeiro)
- Mostra total de registros
- Container encerra

### 2.2 PostgreSQL Container - Detalhes Técnicos

**Variáveis de Ambiente:**
```yaml
environment:
  POSTGRES_DB: headphones_db      # Cria database automaticamente
  POSTGRES_USER: postgres         # Usuário superadmin
  POSTGRES_PASSWORD: postgres     # Senha (não usar em produção!)
```

**Volume Mount:**
```yaml
volumes:
  - postgres-data:/var/lib/postgresql/data
```

**O que isso faz:**
- Docker cria volume nomeado `postgres-data` (se não existir)
- Monta volume dentro do container em `/var/lib/postgresql/data`
- PostgreSQL grava todos os dados (tabelas, índices, WAL) neste diretório
- Quando container é removido, dados **permanecem no volume**

**Health Check:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 5s
  timeout: 5s
  retries: 5
```

**Como funciona:**
- A cada 5 segundos, executa `pg_isready`
- Se retornar exit code 0: incrementa contador de sucesso
- Após 5 sucessos consecutivos: status = `healthy`
- Outros containers com `depends_on: condition: service_healthy` aguardam este status

### 2.3 Catalog Manager - Lógica de População

**Conexão com Retry Logic:**
```python
def get_db_connection():
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host="postgres",  # DNS interno Docker
                port="5432",
                database="headphones_db",
                user="postgres",
                password="postgres"
            )
            return conn
        except psycopg2.OperationalError:
            retry_count += 1
            time.sleep(1)  # Aguarda 1 segundo antes de tentar novamente
    
    raise Exception("Could not connect after 30 attempts")
```

**Por que isso é necessário:**
- Health check marca PostgreSQL como `healthy` assim que aceita conexões
- Mas o banco pode ainda estar finalizando inicialização interna
- Retry logic adiciona margem de segurança

**Criação da Tabela:**
```sql
CREATE TABLE IF NOT EXISTS headphones (
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

**Verificação de População:**
```python
cursor.execute("SELECT COUNT(*) FROM headphones")
count = cursor.fetchone()[0]

if count == 0:
    # Insere 8 fones premium
    sample_headphones = [ ... ]
    for hp in sample_headphones:
        cursor.execute("INSERT INTO headphones (...) VALUES (...)", hp)
    conn.commit()
    print("✅ 8 headphones added successfully!")
else:
    print(f"ℹ️  Database already has {count} headphones")
```

**Saída Formatada:**
```
🎧 AUDIOFILE VAULT - Premium Headphones Catalog
==============================================

📋 CATALOG (8 headphones):

1. Sennheiser HD 800 S
   Type: Open-back | Driver: 56mm | Impedance: 300Ω
   Frequency: 4-51000 Hz | Weight: 330g
   💰 Price: $1,699.99 | Sound: Analytical, Neutral

2. Focal Clear MG
   ...

📊 STATISTICS:
   Total Headphones: 8
   Average Price: $879.87
   Average Impedance: 158Ω
   Price Range: $199.00 - $1,699.99
```

### 2.4 Catalog Reader - Verificação de Persistência

**Função do Reader:**
```python
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT brand, model, price, impedance, type 
    FROM headphones 
    ORDER BY price DESC
""")

headphones = cursor.fetchall()

for hp in headphones:
    print(f"  {hp[0]} {hp[1]} - ${hp[2]} - {hp[3]}Ω - {hp[4]}")

print(f"\n✅ Total: {len(headphones)} headphones found in database")
```

**Saída Esperada:**
```
📖 READING AUDIOFILE VAULT DATABASE
====================================

Headphones (ordered by price):
  Sennheiser HD 800 S - $1699.99 - 300Ω - Open-back
  Focal Clear MG - $1490.00 - 55Ω - Open-back
  Hifiman Arya - $1299.00 - 35Ω - Planar Magnetic
  ...

✅ Total: 8 headphones found in database
```

### 2.5 Persistência de Dados - Como Funciona na Prática

**Cenário 1: Primeira Execução**
```bash
./start.sh
```
```
1. Volume `postgres-data` não existe → Docker cria
2. PostgreSQL inicializa banco vazio
3. Catalog Manager popula com 8 fones
4. Dados são gravados no volume
5. Reader lê os dados
```

**Cenário 2: Parar e Reiniciar Containers**
```bash
docker-compose down  # Remove containers
docker-compose up -d # Recria containers
```
```
1. Containers são deletados
2. Volume `postgres-data` PERMANECE intacto
3. PostgreSQL monta volume existente
4. Dados já estão lá!
5. Catalog Manager detecta 8 fones existentes → não reinsere
6. Reader lê os mesmos 8 fones
```

**Cenário 3: Verificar Persistência (script automático)**
```bash
./test-persistence.sh
```
```
Etapas do script:
1. Para containers: docker-compose down
2. Remove containers: docker rm -f ...
3. Verifica volume existe: docker volume inspect postgres-data
4. Sobe novamente: docker-compose up -d
5. Aguarda inicialização
6. Verifica logs do reader (deve mostrar 8 headphones)
7. ✅ Se encontrou dados = persistência funciona!
```

### 2.6 Rede Docker e Comunicação Interna

**Rede Criada:**
```yaml
networks:
  desafio2-network:
    name: desafio2-network
    driver: bridge
```

**Containers na Rede:**
- `headphones-postgres` (IP: 172.19.0.2)
- `headphones-catalog` (IP: 172.19.0.3)
- `headphones-reader` (IP: 172.19.0.4)

**Resolução de DNS:**
```python
# No código Python:
conn = psycopg2.connect(host="postgres", ...)
```
- DNS interno Docker resolve "postgres" → IP do container `headphones-postgres`
- Conexão é roteada internamente pela bridge
- Porta 5432 está acessível dentro da rede (não exposta ao host)

**Por que não há port mapping:**
```yaml
postgres:
  ports: []  # NENHUMA porta mapeada!
```
- PostgreSQL só precisa ser acessado pelos containers Python
- Não há necessidade de acesso externo
- **Segurança**: banco não fica exposto no host

### 2.7 Logs e Observabilidade

**Logs Esperados - PostgreSQL:**
```
PostgreSQL Database directory appears to contain a database; Skipping initialization
LOG:  database system was shut down at 2025-11-30 14:20:00 UTC
LOG:  database system is ready to accept connections
```

**Logs Esperados - Catalog Manager:**
```
Connecting to PostgreSQL...
✅ Connected successfully!
ℹ️  Database already has 8 headphones
📋 CATALOG (8 headphones):
...
📊 STATISTICS:
   Average Price: $879.87
```

**Logs Esperados - Catalog Reader:**
```
📖 READING AUDIOFILE VAULT DATABASE
====================================
Headphones (ordered by price):
  Sennheiser HD 800 S - $1699.99 - 300Ω - Open-back
  ...
✅ Total: 8 headphones found in database
```

**Comandos para visualizar logs:**
```bash
# Todos os logs
docker-compose logs

# Apenas PostgreSQL
docker-compose logs postgres

# Apenas Catalog Manager
docker-compose logs headphones-catalog

# Logs em tempo real
docker-compose logs -f
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

**1. Navegar até o diretório do desafio:**
```bash
cd /caminho/para/desafio2
```

**2. Verificar estrutura:**
```bash
ls -la
# Deve conter: docker-compose.yml, Dockerfile, Dockerfile.reader, app/
```

**3. Tornar scripts executáveis:**
```bash
chmod +x *.sh
```

### 3.3 Primeira Execução - Inicializar Sistema

**Subir containers:**
```bash
./start.sh
# OU manualmente:
docker-compose up -d
```

**Saída esperada:**
```
Creating network "desafio2-network" with driver "bridge"
Creating volume "postgres-data" with default driver
Creating headphones-postgres ... done
Creating headphones-catalog ... done
Creating headphones-reader ... done

🎧 AudioFile Vault iniciado com sucesso!
💾 Volume postgres-data criado
📊 Verificando logs...
```

**Verificar containers:**
```bash
docker-compose ps
```

**Saída esperada:**
```
NAME                    STATUS                    PORTS
headphones-postgres     Up (healthy)              5432/tcp
headphones-catalog      Exited (0)                
headphones-reader       Exited (0)                
```

**Importante:**
- `postgres`: fica rodando (banco de dados)
- `catalog` e `reader`: executam e encerram (exit 0 = sucesso)

### 3.4 Verificar Logs de População

**Ver logs do Catalog Manager:**
```bash
docker-compose logs headphones-catalog
```

**Deve mostrar:**
```
✅ Connected to PostgreSQL successfully!
✅ Database initialized
✅ 8 headphones added successfully!

🎧 AUDIOFILE VAULT - Premium Headphones Catalog
================================================

📋 CATALOG (8 headphones):

1. Sennheiser HD 800 S
   Type: Open-back | Driver: 56mm | Impedance: 300Ω
   💰 Price: $1,699.99

[... outros 7 fones ...]

📊 STATISTICS:
   Total Headphones: 8
   Average Price: $879.87
   Average Impedance: 158Ω
```

**Ver logs do Reader:**
```bash
docker-compose logs headphones-reader
```

**Deve mostrar:**
```
📖 READING AUDIOFILE VAULT DATABASE
====================================

Headphones (ordered by price):
  Sennheiser HD 800 S - $1699.99 - 300Ω - Open-back
  Focal Clear MG - $1490.00 - 55Ω - Open-back
  [... outros 6 ...]

✅ Total: 8 headphones found in database
```

### 3.5 Testar Persistência de Dados

**Executar teste automatizado:**
```bash
./test-persistence.sh
```

**O script faz:**
1. Para todos os containers
2. Remove containers
3. Verifica que o volume ainda existe
4. Sobe os containers novamente
5. Verifica logs do reader
6. Confirma que os 8 headphones ainda estão lá

**Saída esperada:**
```
🧪 TESTE DE PERSISTÊNCIA
=======================

1️⃣  Parando containers...
✅ Containers parados

2️⃣  Removendo containers...
✅ Containers removidos

3️⃣  Verificando volume...
✅ Volume postgres-data ainda existe!

4️⃣  Recriando containers...
✅ Containers recriados

5️⃣  Aguardando inicialização... (10s)

6️⃣  Verificando dados no banco...
✅ Total: 8 headphones found in database

✅ ✅ ✅ PERSISTÊNCIA FUNCIONANDO! ✅ ✅ ✅
Os dados sobreviveram à remoção dos containers!
```

### 3.6 Teste Manual de Persistência

**1. Verificar dados atuais:**
```bash
docker-compose logs headphones-reader | grep "Total:"
# ✅ Total: 8 headphones found in database
```

**2. Parar e remover containers:**
```bash
docker-compose down
# Stopping headphones-postgres ... done
# Removing headphones-postgres ... done
# Removing headphones-catalog ... done
# Removing headphones-reader ... done
# Removing network desafio2-network
```

**3. Verificar que volume AINDA EXISTE:**
```bash
docker volume ls | grep postgres-data
# local     postgres-data
```

**4. Inspecionar volume:**
```bash
docker volume inspect postgres-data
```

**Saída:**
```json
[
    {
        "Name": "postgres-data",
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/postgres-data/_data",
        "CreatedAt": "2025-11-30T14:20:00Z"
    }
]
```

**5. Subir containers novamente:**
```bash
docker-compose up -d
```

**6. Verificar logs - deve mostrar dados existentes:**
```bash
docker-compose logs headphones-catalog
# ℹ️  Database already has 8 headphones
```

**7. Verificar reader - dados estão intactos:**
```bash
docker-compose logs headphones-reader
# ✅ Total: 8 headphones found in database
```

### 3.7 Acessar PostgreSQL Diretamente (Debug)

**Entrar no container PostgreSQL:**
```bash
docker exec -it headphones-postgres psql -U postgres -d headphones_db
```

**Comandos úteis no psql:**
```sql
-- Listar tabelas
\dt

-- Ver estrutura da tabela
\d headphones

-- Contar registros
SELECT COUNT(*) FROM headphones;

-- Listar todos os fones
SELECT brand, model, price FROM headphones ORDER BY price DESC;

-- Ver estatísticas
SELECT 
    COUNT(*) as total,
    AVG(price) as avg_price,
    AVG(impedance) as avg_impedance,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM headphones;

-- Sair
\q
```

### 3.8 Limpar Dados e Recomeçar

**Opção 1: Remover apenas containers (mantém dados):**
```bash
docker-compose down
```

**Opção 2: Remover containers E volume (limpa tudo):**
```bash
docker-compose down -v
# OU manualmente:
docker-compose down
docker volume rm postgres-data
```

**Opção 3: Limpeza completa + rebuild:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### 3.9 Recriar do Zero

**Para garantir estado limpo:**
```bash
# 1. Parar tudo
docker-compose down -v

# 2. Remover imagens antigas
docker rmi desafio2-headphones-catalog desafio2-headphones-reader

# 3. Rebuild sem cache
docker-compose build --no-cache

# 4. Subir novamente
docker-compose up -d

# 5. Verificar logs
docker-compose logs headphones-catalog
# Deve mostrar: "✅ 8 headphones added successfully!"
```

### 3.10 Parar Aplicação

**Manter dados (volume permanece):**
```bash
./stop.sh
# OU:
docker-compose down
```

**Apagar tudo (incluindo dados):**
```bash
docker-compose down -v
```

---

## Observações Finais

**✅ Persistência Garantida:**
O volume `postgres-data` é independente do ciclo de vida dos containers. Dados sobrevivem a `docker-compose down` e permanecem até remoção explícita com `docker volume rm` ou `docker-compose down -v`.

**✅ Idempotência:**
O script `headphones_catalog.py` verifica se dados já existem antes de popular. Executar múltiplas vezes não cria duplicatas.

**✅ Segurança:**
A porta PostgreSQL (5432) NÃO está exposta ao host. Apenas containers na mesma rede conseguem acessar o banco.

**✅ Health Checks:**
O `depends_on: condition: service_healthy` garante que o PostgreSQL está realmente pronto antes de executar scripts que dependem dele.

**✅ Retry Logic:**
Conexões ao banco implementam retry logic (30 tentativas) para lidar com delays de inicialização.

**✅ Localização do Volume:**
No Linux: `/var/lib/docker/volumes/postgres-data/_data`  
No macOS/Windows: Dentro da VM do Docker Desktop

**✅ Teste de Persistência:**
Execute `./test-persistence.sh` para validar que dados realmente persistem após remoção de containers.
