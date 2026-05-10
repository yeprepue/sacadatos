# GitHub Data Pipeline

Pipeline automatizado de extracción de datos de repositorios GitHub con arquitectura hexagonal.

## 📋 Descripción

Pipeline ETL que extrae issues y commits de repositorios de GitHub, los almacena en PostgreSQL y genera reportes.

## 🏗️ Arquitectura

```txt
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER │ │ (main.py)                            │
└─────────────────────────────────────────────────────────────┘
│ ▼
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER                                           │
│ (Use Cases: Extract, Generate Report)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
│ ▼
┌─────────────────────────────────────────────────────────────┐
│ DOMAIN LAYER                                                │
│ (Models: Repository, Issue, Commit)                         │
│ (Ports: GitHubClient, Database, Drive)                      │
│ (Services: PipelineService)                                 │ 
│                                                             │
└─────────────────────────────────────────────────────────────┘
│ ▼
┌─────────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE LAYER                                        │
│ (Adapters: GitHub, Database, Drive)                         │
│ (Repositories: Issue, Commit, Repository)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Lenguaje | Python 3.11+ |
| ORM | SQLModel |
| Base de datos | PostgreSQL |
| API Externa | GitHub REST API |
| Cloud Storage | Google Drive API |
| Orquestación | Apache Airflow |
| Contenedores | Docker |

## 📁 Estructura del Proyecto

```txt
. ├── main.py # Punto de entrada
  ├── config.json # Configuración de repositorios
  ├── .env # Variables de entorno
  ├── src/
  │├── config/ # Configuración │
  │ ├── settings.py │ │
  └── logging_config.py
  │ ├── domain/ # Capa de dominio
  │ │ ├── models/ # Entidades
  │ │ ├── ports/ # Interfaces
  │ │ └── services/ # Lógica de negocio
  │ ├── infrastructure/ # Capa de infraestructura
  │ │ ├── adapters/ # Implementaciones externas
  │ │ └── repositories/ # Acceso a datos
  │ └── application/ # Casos de uso
  │ └── use_cases/ ├── docker/
  │ ├── Dockerfile
  │ └── requirements.txt
  └── dags/
  └── github_pipeline.py
```


## 🚀 Instalación

### 1. Clonar repositorio

```bash
git clone https://github.com/yeprepue/sacadatos.git
cd sacadatos
```
### 2. Configurar variables de entorno
Crear archivo .env:
```txt
GITHUB_TOKEN=ghp_tu_token_aqui
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=sacadatos
LOG_LEVEL=INFO

```
### 3. Instalar dependencias
```bash
pip install -r docker/requirements.txt
```
### 4. Configurar PostgreSQL
```bash
psql -U postgres -c "CREATE DATABASE sacadatos;"
```
### 5. Configurar Google Drive (opcional)
* Crear proyecto en Google Cloud Console
* Habilitar Google Drive API
* Descargar credentials.json
* Compartir carpeta con Service Account

####⚙️ Configuración
Editar config.json para especificar repositorios:
```bash
{
  "repositories": [
    {"owner": "pandas-dev", "name": "pandas"},
    {"owner": "microsoft", "name": "vscode"}
  ],
  "last_extraction": null
}
```
### ▶️ Uso
Ejecución local
```bash
python main.py
```
📊 Base de Datos
Esquema
```sql
-- Repositorios
CREATE TABLE repositories (
    id SERIAL PRIMARY KEY,
    owner VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    UNIQUE(owner, name)
);

-- Issues
CREATE TABLE issues (
    id BIGINT PRIMARY KEY,
    repo_id INTEGER REFERENCES repositories(id),
    number INTEGER,
    title TEXT,
    state VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    closed_at TIMESTAMP,
    user_login VARCHAR(255),
    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Commits
CREATE TABLE commits (
    sha VARCHAR(40) PRIMARY KEY,
    repo_id INTEGER REFERENCES repositories(id),
    message TEXT,
    author_login VARCHAR(255),
    author_date TIMESTAMP,
    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
## 🔧 Desarrollo
Con Docker
```bash
# Construir imagen
docker-compose build

# Ejecutar
docker-compose up extractor

```


## 📝 Licencia
MIT License

## 👤 Autor
Nombre: Yeison Esteban Pretel Puentes
GitHub: https://github.com/yeprepue
