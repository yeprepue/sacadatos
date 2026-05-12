# 📦 Manual de Despliegue - SACADATOS v1.0

**Pipeline de extracción de datos de GitHub orquestado con Apache Airflow**

---

## 📋 Tabla de Contenidos

1. Requisitos Previos
2. Estructura del Proyecto
3. Configuración Inicial
4. Despliegue con Docker (Pipeline Base)
5. Despliegue con Airflow (Orquestación)
6. Verificación y Pruebas
7. Comandos Útiles
8. Solución de Problemas
9. Arquitectura
10. Variables de Entorno

---

## ✅ Requisitos Previos

### Hardware Mínimo
- **CPU:** 2 núcleos
- **RAM:** 4 GB
- **Disco:** 10 GB libres

### Software Necesario

| Software | Versión |
|---------|---------|
| Docker | 24.0+ |
| Docker Compose | 2.20+ |
| Git | 2.40+ |
| Navegador | Chrome / Firefox / Edge |

### Windows
- Ejecutar la terminal como **Administrador**
- Tener Docker Desktop instalado y en ejecución

### Linux
```bash
sudo apt update
sudo apt install docker.io docker-compose git -y
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

---

## 📁 Estructura del Proyecto

```text
SACADATOS/
├── reports/                          # Reportes CSV generados
│   └── reporte_github.csv
│
├── src/
│   ├── application/                  # Casos de uso (lógica de negocio)
│   │   └── use_cases/
│   │       ├── extract_github_data.py
│   │       └── generate_report.py
│   │
│   ├── config/                       # Configuración global
│   │   ├── logging_config.py
│   │   └── settings.py
│   │
│   ├── domain/                       # Núcleo del dominio
│   │   ├── models/
│   │   │   ├── commit.py
│   │   │   ├── issue.py
│   │   │   └── repository.py
│   │   │
│   │   ├── ports/                    # Interfaces (contratos)
│   │   │   ├── database.py
│   │   │   ├── drive_client.py
│   │   │   └── github_client.py
│   │   │
│   │   └── services/
│   │       └── pipeline_service.py
│   │
│   ├── infrastructure/               # Implementaciones concretas
│   │   ├── adapters/
│   │   │   ├── database_adapter.py
│   │   │   ├── drive_adapter.py
│   │   │   └── github_adapter.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── commit_repo.py
│   │   │   ├── issue_repo.py
│   │   │   └── repository_repo.py
│   │   │
│   │   └── database.py
│   │
│   └── tests/                        # Pruebas unitarias
│
├── .env                              # Variables de entorno
├── .gitignore
├── main.py                           # Punto de entrada principal
├── reporte-github.csv                # Reporte generado
├── start-airflow-admin.bat           # Inicio automático en Windows
└── test_imports.py                   # Validación de imports
```

---
## 🏗️ Arquitectura del Proyecto

* El proyecto sigue el patrón de Clean Architecture, garantizando:

- ✅ Separación clara de responsabilidades.
- ✅ Bajo acoplamiento entre capas.
- ✅ Alta mantenibilidad.
- ✅ Facilidad para realizar pruebas unitarias.
- ✅ Escalabilidad para nuevas fuentes de datos.
- 📌 Capas de la Arquitectura
- 🧠 Domain

- Contiene las entidades del negocio y las interfaces (ports).

- Models: Commit, Issue, Repository
- Ports: contratos para GitHub, Base de Datos y Google Drive
- Services: lógica de orquestación del pipeline
### ⚙️ Application

Contiene los casos de uso.

ExtractGithubDataUseCase
GenerateReportUseCase
#### 🔌 Infrastructure

Implementa los contratos definidos en Domain.

Adaptadores para GitHub API
Adaptadores para PostgreSQL
Adaptadores para Google Drive
Repositorios especializados
#### 🛠️ Config

Configuración del sistema y logging.

#### 📊 Reports

Salida de los archivos CSV generados.

#### 🚀 Main

Punto de entrada del sistema.

## ⚙️ Configuración Inicial

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sacadatos.git
cd sacadatos
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Contenido mínimo del archivo `.env`:

```env
GITHUB_TOKEN=ghp_tu_token_real_aqui
GOOGLE_DRIVE_CONFIG_FILE_ID=tu_config_id
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id
POSTGRES_HOST=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
POSTGRES_DB=sacadatos
LOG_LEVEL=INFO
```

---

## 🐳 Despliegue con Docker (Pipeline Base)

```bash
cd docker
docker-compose build
docker-compose up -d
docker-compose ps
docker-compose exec extractor python main.py
docker cp github_extractor:/app/reporte_github.csv ../reports/
docker-compose down
```

---

## 🚀 Despliegue con Airflow (Orquestación)

### Windows

```bat
cd C:\ruta\a\sacadatos
start-airflow-admin.bat
```

### Linux / macOS

```bash
cd docker
docker-compose -f docker-compose-airflow.yml up -d
docker-compose -f docker-compose-airflow.yml ps
```

### Manual (Todos los SO)

```bash
cd docker
docker-compose -f docker-compose-airflow.yml down -v
docker-compose -f docker-compose-airflow.yml up -d
sleep 30
docker-compose -f docker-compose-airflow.yml ps
```

---

## ✅ Verificación y Pruebas

### Interfaces Web

| Interfaz | URL | Credenciales |
|--------|-----|-------------|
| Airflow UI | http://localhost:8080 | airflow / airflow |
| Flower | http://localhost:5555 | No requiere |

### Ejecutar DAG manualmente

```bash
docker-compose -f docker-compose-airflow.yml exec -T airflow-webserver   airflow dags unpause github_pipeline_v2

docker-compose -f docker-compose-airflow.yml exec -T airflow-webserver   airflow dags trigger github_pipeline_v2

docker-compose -f docker-compose-airflow.yml exec -T airflow-webserver   airflow dags list-runs -d github_pipeline_v2
```

---

## 🛠️ Comandos Útiles

### Gestión de Servicios

| Acción | Comando |
|------|------|
| Levantar Airflow | `docker-compose -f docker-compose-airflow.yml up -d` |
| Detener Airflow | `docker-compose -f docker-compose-airflow.yml down` |
| Limpiar volúmenes | `docker-compose -f docker-compose-airflow.yml down -v` |
| Reiniciar | `docker-compose -f docker-compose-airflow.yml restart` |
| Ver estado | `docker-compose -f docker-compose-airflow.yml ps` |
| Ver logs | `docker-compose -f docker-compose-airflow.yml logs -f` |

### Gestión de DAGs

| Acción | Comando |
|------|------|
| Listar DAGs | `airflow dags list` |
| Pausar DAG | `airflow dags pause github_pipeline_v2` |
| Reanudar DAG | `airflow dags unpause github_pipeline_v2` |
| Ejecutar manualmente | `airflow dags trigger github_pipeline_v2` |
| Ver ejecuciones | `airflow dags list-runs -d github_pipeline_v2` |

---

## 🐛 Solución de Problemas

### Scheduler no está corriendo

```bash
docker-compose -f docker-compose-airflow.yml restart airflow-scheduler
docker-compose -f docker-compose-airflow.yml logs -f airflow-scheduler
```

### DAG no aparece en la UI

```bash
ls -la dags/github_pipeline_dag.py
docker-compose -f docker-compose-airflow.yml exec -T airflow-webserver   airflow dags list-import-errors
docker-compose -f docker-compose-airflow.yml exec -T airflow-webserver   airflow dags reserialize
```

### Puertos ocupados

Verifica que los puertos `8080`, `5433`, `5555` y `6380` estén libres.

---

## 📐 Arquitectura

```text
Google Drive (configuración)
        │
        ▼
Airflow Scheduler (2:00 AM UTC)
        │
        ▼
Docker Extractor Container
        │
        ├──► GitHub API
        │
        ▼
PostgreSQL (datos crudos)
        │
        ▼
Transformaciones SQL
        │
        ▼
GenerateReportUseCase (pandas)
        │
        ▼
CSV Report (reports/reporte_github.csv)
```

---

## 🔧 Variables de Entorno

### Obligatorias

| Variable | Descripción |
|--------|-------------|
| GITHUB_TOKEN | Token de acceso a GitHub API |
| POSTGRES_HOST | Host de PostgreSQL |
| POSTGRES_USER | Usuario de PostgreSQL |
| POSTGRES_PASSWORD | Contraseña |
| POSTGRES_DB | Nombre de la base de datos |

### Opcionales

| Variable | Descripción |
|--------|-------------|
| GOOGLE_DRIVE_CONFIG_FILE_ID | ID del archivo de configuración |
| GOOGLE_DRIVE_FOLDER_ID | ID de la carpeta de destino |
| LOG_LEVEL | Nivel de logging |

---

## 📝 Notas Importantes

- Nunca subas `.env` ni `credentials.json` a Git.
- En Windows, ejecuta siempre la terminal como administrador.
- Airflow requiere al menos 4 GB de RAM disponibles.
- El primer inicio puede tardar entre 30 y 60 segundos.

---

## 🆘 Soporte

```bash
docker-compose -f docker-compose-airflow.yml logs -f
docker-compose -f docker-compose-airflow.yml ps
docker-compose -f docker-compose-airflow.yml down -v && docker-compose -f docker-compose-airflow.yml up -d
```
