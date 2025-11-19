# Projeto 2

Este repositório contém as soluções para os 5 desafios propostos.

## 📋 Estrutura do Projeto

```
/
├── README.md                    # Este arquivo
├── desafio1/                    # ✅ Containers em Rede
│   ├── README.md
│   ├── docker-compose.yml
│   ├── server/
│   └── client/
├── desafio2/                    # ✅ Volumes e Persistência
│   ├── README.md
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── Dockerfile.reader
│   └── app/
├── desafio3/                    # 🚧 Docker Compose Orquestrando Serviços
├── desafio4/                    # 🚧 Microsserviços Independentes
└── desafio5/                    # 🚧 Microsserviços com API Gateway
```

## 🎯 Desafios

### ✅ Desafio 1 — Containers em Rede (20 pts)
**Status**: Concluído

Implementação de dois containers que se comunicam através de uma rede Docker customizada:
- Servidor web Flask na porta 8080
- Cliente fazendo requisições HTTP periódicas
- Rede bridge customizada com DNS interno

[📖 Ver documentação completa](./desafio1/README.md)

**Como executar**:
```bash
cd desafio1
./start.sh
./test.sh
```

---

### ✅ Desafio 2 — Volumes e Persistência (20 pts)
**Status**: Concluído

Catálogo profissional de fones de ouvido para audiófilos com persistência de dados:
- PostgreSQL 15 Alpine com volume persistente
- Catalog Manager para popular dados
- Catalog Reader para verificar persistência
- Volume Docker garantindo dados após remoção de containers

[📖 Ver documentação completa](./desafio2/README.md)

**Como executar**:
```bash
cd desafio2
./start.sh
./test-persistence.sh
```

---

### 🚧 Desafio 3 — Docker Compose Orquestrando Serviços (25 pts)
**Status**: Em desenvolvimento

Orquestração de múltiplos serviços dependentes usando Docker Compose.

---

### 🚧 Desafio 4 — Microsserviços Independentes (20 pts)
**Status**: Em desenvolvimento

Criação de microsserviços independentes com comunicação HTTP.

---

### 🚧 Desafio 5 — Microsserviços com API Gateway (25 pts)
**Status**: Em desenvolvimento

Arquitetura com API Gateway centralizando acesso aos microsserviços.

---

## 🛠️ Tecnologias Utilizadas

- **Docker** & **Docker Compose**
- **Python** (Flask, psycopg2)
- **PostgreSQL** (15 Alpine)
- **Shell Script**
- **Alpine Linux**
- **Networking** (Bridge networks)
- **Volumes** (Persistência de dados)

## 🚀 Como Usar Este Repositório

1. **Clone o repositório**:
```bash
git clone <url-do-repositorio>
cd projeto2
```

2. **Acesse o desafio desejado**:
```bash
cd desafio1
```

3. **Siga as instruções no README específico**

Cada desafio possui seu próprio README.md com:
- Descrição detalhada da solução
- Explicação da arquitetura
- Instruções de execução passo a passo
- Exemplos de uso e saídas esperadas
