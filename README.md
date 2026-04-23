# 🌱 CemaPlant - IA para Identificacao de Doencas em Plantas

Projeto com backend em FastAPI e frontend web multipaginas para cadastro de usuarios, upload de imagens, deteccao de doencas em plantas com IA e geracao de recomendacoes.

## Sumario

- [Visao geral](#visao-geral)
- [Stack do projeto](#stack-do-projeto)
- [Estrutura principal](#estrutura-principal)
- [Pre-requisitos](#pre-requisitos)
- [Configuracao de ambiente (.env)](#configuracao-de-ambiente-env)
- [Rodando com Docker (recomendado)](#rodando-com-docker-recomendado)
- [Rodando localmente sem Docker](#rodando-localmente-sem-docker)
- [Como validar se esta funcionando](#como-validar-se-esta-funcionando)
- [Fluxo basico da API](#fluxo-basico-da-api)
- [Frontend (paginas e fluxo)](#frontend-paginas-e-fluxo)
- [Como rodar o frontend](#como-rodar-o-frontend)
- [Troubleshooting](#troubleshooting)

## Visao geral

O CemaPlant recebe imagens de folhas, identifica a planta/doenca e persiste os dados no PostgreSQL. A API tambem gera recomendacoes para cada deteccao.

## 🧠 Stack do projeto

- Python 3.11
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- PostgreSQL 15
- Docker / Docker Compose
- HTML5
- CSS3
- JavaScript (vanilla)

## Estrutura principal

```text
.
|-- docker-compose.yml
|-- backend/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- alembic.ini
|   |-- migrations/
|   `-- app/
|       |-- main.py
|       |-- database.py
|       |-- routes/
|       |-- services/
|       |-- models/
|       |-- auth/
|       `-- IA/
`-- frontend/
	|-- index.html
	|-- login.html
	|-- cadastro.html
	|-- pages/
	|   |-- dashboard.html
	|   |-- detectar.html
	|   `-- historico.html
	|-- js/
	|   |-- api.js
	|   |-- auth.js
	|   |-- dashboard.js
	|   |-- detectar.js
	|   `-- historico.js
	`-- css/
		`-- style.css
```

## Pre-requisitos

### Para Docker

- Docker Desktop instalado e em execucao
- Docker Compose v2 (`docker compose`)

### Para execucao local (sem Docker)

- Python 3.11
- PostgreSQL 15 (ou compativel)

## Configuracao de ambiente (.env)

No diretorio `backend/`, crie um arquivo `.env` com base no `.env.example`:

```bash
cd backend
copy .env.example .env
```

Preencha os valores. Exemplo para execucao local (Postgres fora do Docker):

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cemaplant
OPENROUTER_API_KEY=sua_chave_aqui
```

Observacao:
- Em Docker, o hostname do banco deve ser `db` (na rede do compose).
- Localmente, normalmente sera `localhost`.

## ⚙️Rodando com Docker (recomendado)

No diretorio raiz do projeto:

```bash
docker compose down
docker compose up --build
```

Se quiser rodar em background:

```bash
docker compose up --build -d
```

Ver status:

```bash
docker compose ps
```

Ver logs do backend:

```bash
docker compose logs -f backend
```

Parar tudo:

```bash
docker compose down
```

Depois para roda em modo normal:

```bash
docker compose up
```

## ⚙️Rodando localmente sem Docker
### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
```
### 2. Entrar no backend

```bash
cd backend
```

### 3. Criar e ativar ambiente virtual

Terminal (Windows):

```terminal
py -3.11 -m venv venv
venv\Scripts\activate
```
PowerShell (Windows):

```powershell
py -3.11 -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configurar `.env`

Garanta que `DATABASE_URL` aponta para o seu PostgreSQL local.

### 6. Rodar migrations

```bash
alembic upgrade head
```

### 7. Iniciar API

```bash
uvicorn app.main:app --reload
```

## 🌐 Como validar se esta funcionando

Com a API no ar, acesse:

- Home: `http://127.0.0.1:8000/` ou `http://localhost:8000/`
- Swagger: `http://127.0.0.1:8000/docs` ou `http://localhost:8000/docs`

## Fluxo basico da API

Muitas rotas exigem usuario autenticado via cookie `access_token`.

Passo a passo sugerido:

1. Registrar usuario: `POST /usuarios/registrar`
2. Fazer login: `POST /usuarios/login` (define cookie)
3. Enviar imagem para deteccao: `POST /deteccoes/`
4. Consultar resultados:
	- `GET /deteccoes/usuario`
	- `GET /doencas/usuario`
	- `GET /recomendacoes/usuario`

## 🖥️ Frontend (paginas e fluxo)

1. `login.html`
	- autentica o usuario via `POST /usuarios/login`
2. `cadastro.html`
	- cria conta via `POST /usuarios/registrar`
3. `pages/dashboard.html`
	- mostra resumo do usuario (deteccoes, plantas, doencas, recomendacoes e imagens)
	- exibe miniaturas JPG/PNG das imagens detectadas
4. `pages/detectar.html`
	- envia imagem (JPG/PNG) para `POST /deteccoes/`
	- apresenta resultado da deteccao com confianca
5. `pages/historico.html`
	- lista historico do usuario usando endpoints `/usuario`

Arquivos JS principais:

- `frontend/js/api.js`: camada de requisicoes HTTP e resolucao de URL de imagens
- `frontend/js/auth.js`: sessao/login/logout e protecao de paginas
- `frontend/js/dashboard.js`: logica da pagina inicial
- `frontend/js/detectar.js`: upload, validacao e resultado de deteccao
- `frontend/js/historico.js`: carregamento do historico

## Como rodar o frontend

Com o backend no ar (`http://localhost:8000`), rode o frontend em um servidor local.

Opcao 1 (simples, com Python):

```bash
cd frontend
python -m http.server 5500
```

Depois abra:

- `http://localhost:5500/login.html`

## Troubleshooting

### Erro: `sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:driver`

Esse erro acontece quando a URL do banco esta invalida (placeholder `driver://...`).

Checklist:

1. Confirme se `backend/.env` existe.
2. Confirme se `DATABASE_URL` esta completa e valida.
3. Em Docker, use host `db`:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/cemaplant
```

4. Reconstrua os containers:

```bash
docker compose down
docker compose up --build
```

### Build Docker muito lento (contexto muito grande)

Se o build estiver transferindo centenas de MB, revise `backend/.dockerignore` para excluir:

- `venv/`
- `app/uploads/`
- datasets/modelos grandes
- `__pycache__/`

### Erro de instalacao via `requirements.txt` no Windows

Se o arquivo foi gerado com `pip freeze > requirements.txt` no PowerShell, ele pode ficar em UTF-16 e quebrar o build.

Para gerar em UTF-8:

```powershell
pip freeze | Out-File -Encoding utf8 requirements.txt
```
