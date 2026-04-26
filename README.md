# 🌱 CemaPlant - IA para Identificação de Doencas em Plantas

Projeto com backend em FastAPI e frontend web multipaginas para cadastro de usuarios, upload de imagens, deteccao de doencas em plantas com IA e geracao de recomendacoes.

## Sumario

- [Visao geral](#visao-geral)
- [Stack do projeto](#-stack-do-projeto)
- [Estrutura principal](#estrutura-principal)
- [Pre-requisitos](#pre-requisitos)
- [Configuracao de ambiente (.env)](#configuracao-de-ambiente-env)
- [Rodando com Docker (recomendado)](#️rodando-com-docker-recomendado)
- [Rodando localmente sem Docker](#️rodando-localmente-sem-docker)
- [Como validar se esta funcionando](#-como-validar-se-esta-funcionando)
- [Fluxo basico da API](#fluxo-basico-da-api)
- [Frontend (paginas e fluxo)](#️-frontend-paginas-e-fluxo)
- [Como rodar o frontend](#como-rodar-o-frontend)
- [Troubleshooting](#troubleshooting)
- [Treinamento da IA no Google Colab e métodos](#-treinamento-da-ia-no-google-colab-e-métodos)

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
|       `-- uploads/imagens (imagens de plantas e doenças que a IA identifica sem errar)
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

Limpar cache do Docker:

```bash
docker builder prune -a
```

Limpar imagens e volumes:

```bash
docker system prune -a --volumes
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
3. Enviar imagem para deteccao: `POST /deteccoes/` (Em backend/app/uploads/imagens tem imagens de plantas e doenças que a IA identifica sem errar)
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
	- Em backend/app/uploads/imagens tem imagens de plantas e doenças que a IA identifica sem errar.
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

## 🤖 Treinamento da IA no Google Colab e métodos
- O treinamento da IA não é obrigatório para roda a aplicação, tudo o que está escrito abaixo serve apenas para documentar os métodos utilizados.
- Usei o Google Colab gratuito (T4) para um treinamento mais eficiente e rápido da IA.
- Economizei cerca de 7 horas no treinamento da IA.
- Utilizei o Google Drive para salvar as pastas da base de dados.

### Fonte da Base de Dados utilizada:
- https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset

### Ordem geral:
- Troque os caminhos e os nomes de acordo com a organização do seu Google Drive.
- Treine primeiro a base dataset_plantas, que é o dataset organizado por pastas com os nomes das plantas.
- Rode cada célula por vez, em blocos diferentes.
- Depois de acabar a parte 1, pare o processamento, rode a parte 2 em outro arquivo do Colab e ative o T4.
- Em seguida, treine com a base dataset_doencas, que possui a mesma estrutura do dataset, apenas com nomes mais claros para o treinamento.
- Ao treinar a dataset_doencas, repita todos os comandos e substitua, em cada um deles, a palavra "plantas" por "doenças".
- Ao final dos treinamentos, serão gerados os arquivos que serão utilizados pela IA para fazer a detecção: class_names_plantas.json, modelo_plantas.keras, class_names_doencas.json e modelo_doencas.keras.

### Passo a passo:

#### PARTE 1 - Treino do topo (base congelada)

CÉLULA 1 — Verificar GPU
```bash
import tensorflow as tf
print("GPU:", tf.config.list_physical_devices('GPU'))

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

CÉLULA 2 — Montar Drive e extrair dataset
```bash
from google.colab import drive
drive.mount('/content/drive')

import zipfile, os

zip_path    = "/content/drive/MyDrive/Colab Notebooks/dataset_plantas.zip"
extract_path = "/content/dataset"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

print(os.listdir("/content/dataset"))
```

CÉLULA 3 — Configurações
```bash
IMG_SIZE   = 224
BATCH_SIZE = 16   

TRAIN_PATH = "/content/dataset/dataset_plantas/train"
VAL_PATH   = "/content/dataset/dataset_plantas/valid"
```

CÉLULA 4 — Carregar dados e salvar class_names
```bash
train_data = tf.keras.preprocessing.image_dataset_from_directory(
    TRAIN_PATH,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=42
)

val_data = tf.keras.preprocessing.image_dataset_from_directory(
    VAL_PATH,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    seed=42
)

class_names = train_data.class_names
print(f"Classes: {len(class_names)} → {class_names}")

import json
with open("/content/drive/MyDrive/Colab Notebooks/class_names_plantas_v2.json", "w") as f:
    json.dump(class_names, f)
print("class_names salvo!")
```

CÉLULA 5 — Pipeline de dados com augmentation
```bash
AUTOTUNE = tf.data.AUTOTUNE

data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.2),
], name="augmentation")

def prepare(ds, augment=False):
    if augment:
        ds = ds.map(
            lambda x, y: (data_augmentation(x, training=True), y),
            num_parallel_calls=AUTOTUNE
        )
    ds = ds.map(
        lambda x, y: (tf.keras.applications.efficientnet.preprocess_input(x), y),
        num_parallel_calls=AUTOTUNE
    )
    return ds.prefetch(AUTOTUNE)

train_ds = prepare(train_data, augment=True)
val_ds   = prepare(val_data,   augment=False)
```

CÉLULA 6 — Construir modelo (base congelada)
```bash
base_model = tf.keras.applications.EfficientNetB0(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

inputs  = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x       = base_model(inputs, training=False)
x       = tf.keras.layers.GlobalAveragePooling2D()(x)
x       = tf.keras.layers.BatchNormalization()(x)
x       = tf.keras.layers.Dense(256, activation='relu')(x)
x       = tf.keras.layers.Dropout(0.4)(x)
outputs = tf.keras.layers.Dense(len(class_names), activation='softmax')(x)

model = tf.keras.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
```

CÉLULA 7 — Treinar fase 1
```bash
import math

total_treino = sum(1 for _ in train_data.unbatch())
print(f"Total imagens treino: {total_treino}")

STEPS_POR_EPOCH = min(1500, math.ceil(total_treino / BATCH_SIZE))
STEPS_VAL = min(300, math.ceil(total_treino / BATCH_SIZE / 4))

print(f"Steps por epoch: {STEPS_POR_EPOCH} (~{STEPS_POR_EPOCH * BATCH_SIZE} imagens)")
print(f"Steps validação: {STEPS_VAL}")

callbacks_fase1 = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy', patience=4,
        restore_best_weights=True, verbose=1
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.3,
        patience=2, min_lr=1e-7, verbose=1
    ),
    tf.keras.callbacks.ModelCheckpoint(
        "/content/drive/MyDrive/Colab Notebooks/ckpt_plantas_fase1.keras",
        monitor='val_accuracy', save_best_only=True, verbose=1
    )
]

print("=== FASE 1: Treinando topo ===")
history1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=12,
    steps_per_epoch=STEPS_POR_EPOCH,     
    validation_steps=STEPS_VAL,           
    callbacks=callbacks_fase1
)
print(f"Melhor val_accuracy fase 1: {max(history1.history['val_accuracy']):.4f}")
```

#### FASE 2 - Fine-tuning (abrir em novo arquivo Colab com T4 ativo)

CÉLULA 9 — Setup
```bash
import tensorflow as tf
import json, os, math

print("GPU:", tf.config.list_physical_devices('GPU'))

IMG_SIZE   = 224
BATCH_SIZE = 16
DRIVE = "/content/drive/MyDrive/Colab Notebooks"
```

CÉLULA 2 — Montar Drive e carregar class_names
```bash
from google.colab import drive
drive.mount('/content/drive')

DRIVE = "/content/drive/MyDrive/Colab Notebooks"

with open(f"{DRIVE}/class_names_plantas_v2.json") as f:
    class_names = json.load(f)
print(f"Classes: {len(class_names)} → {class_names}")
```

CÉLULA 3 — Extrair dataset
```bash
import zipfile

zip_path     = f"{DRIVE}/dataset_plantas.zip"
extract_path = "/content/dataset"

if not os.path.exists("/content/dataset/dataset_plantas/train"):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_path)
    print("Extraído!")
else:
    print("Dataset já extraído.")

TRAIN_PATH = "/content/dataset/dataset_plantas/train"
VAL_PATH   = "/content/dataset/dataset_plantas/valid"
```

CÉLULA 4 — Pipeline otimizado para fine-tuning
```bash
AUTOTUNE = tf.data.AUTOTUNE

def preprocess_only(x, y):
    x = tf.cast(x, tf.float32)
    return tf.keras.applications.efficientnet.preprocess_input(x), y

train_data = tf.keras.preprocessing.image_dataset_from_directory(
    TRAIN_PATH,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=42
)
val_data = tf.keras.preprocessing.image_dataset_from_directory(
    VAL_PATH,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    seed=42
)

train_ds = (
    train_data
    .map(preprocess_only, num_parallel_calls=AUTOTUNE)
    .repeat()         
    .prefetch(AUTOTUNE)
)
val_ds = (
    val_data
    .map(preprocess_only, num_parallel_calls=AUTOTUNE)
    .repeat()
    .prefetch(AUTOTUNE)
)

total_treino = len(train_data)
STEPS_POR_EPOCH = min(1500, total_treino)
STEPS_VAL       = min(300,  len(val_data))
print(f"Steps treino: {STEPS_POR_EPOCH} | Steps val: {STEPS_VAL}")
```

CÉLULA 5 — Carregar modelo da fase 1 e preparar fine-tuning
```bash
import tensorflow as tf

model = tf.keras.models.load_model(f"{DRIVE}/ckpt_plantas_fase1.keras")
print("Modelo fase 1 carregado!")

base_model = model.layers[1]  
print(f"Base model: {base_model.name}")

base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

print(f"Camadas treináveis base_model: {sum(1 for l in base_model.layers if l.trainable)}")
print(f"Variáveis treináveis total: {len(model.trainable_variables)}")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

loss, acc = model.evaluate(val_ds, steps=50, verbose=1)
print(f"\nAcurácia inicial: {acc*100:.2f}%  ← deve ser próxima do final da fase 1")
```

CÉLULA 6 — Treinar fase 2
```bash
callbacks_fase2 = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy', patience=5,
        restore_best_weights=True, verbose=1
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.2,
        patience=3, min_lr=1e-8, verbose=1
    ),
    tf.keras.callbacks.ModelCheckpoint(
        f"{DRIVE}/ckpt_plantas_fase2.keras",
        monitor='val_accuracy', save_best_only=True, verbose=1
    )
]

print("=== FASE 2: Fine-tuning ===")
history2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=15,
    steps_per_epoch=STEPS_POR_EPOCH,
    validation_steps=STEPS_VAL,
    callbacks=callbacks_fase2
)
print(f"Melhor val_accuracy fase 2: {max(history2.history['val_accuracy']):.4f}")
```

CÉLULA 7 — Salvar e baixar modelo final
```bash
import shutil
from google.colab import files

model.save(f"{DRIVE}/modelo_plantas.keras")
print("Salvo no Drive!")

shutil.copy(f"{DRIVE}/modelo_plantas.keras", "/content/modelo_plantas.keras")
files.download("/content/modelo_plantas.keras")
files.download(f"{DRIVE}/class_names_plantas.json")
```