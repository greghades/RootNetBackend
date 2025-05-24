# 🐳 Django REST Framework App (Dockerizado)

Este proyecto es una aplicación web desarrollada con **Django** y **Django REST Framework**, contenida completamente mediante **Docker** y **Docker Compose**. Incluye una base de datos **PostgreSQL**, un servidor **Redis** para caché y tareas asincrónicas, y una interfaz de administración **pgAdmin** para gestionar la base de datos.

---

## 📁 Estructura del Proyecto

```
.
├── core/                   # Código fuente de Django
├── Dockerfile              # Dockerfile del servicio web
├── docker-compose.yml      # Orquestador de servicios
├── .env                    # Variables de entorno (no versionar)
└── README.md               # Documentación del proyecto
```

---

## 🚀 Servicios incluidos

| Servicio   | Puerto Local | Descripción                           |
|------------|--------------|---------------------------------------|
| `web`      | `8001`       | Aplicación Django (DRF)               |
| `db`       | `5432`       | Base de datos PostgreSQL              |
| `pgadmin`  | `80`         | Interfaz gráfica de PostgreSQL        |
| `redis`    | `6379`       | Servidor de cacheo y mensajes         |

---

## ⚙️ Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/greghades/RootNetBackend.git
cd tu-carpeta
```

### 2. Crear archivo `.env`

Crea un archivo `.env` en la raíz del proyecto basado en el siguiente ejemplo:

#### .env.example

```env
# Entorno de la app
APP_ENV=development
DEBUG=1

# Configuración de Django
DJANGO_HOST=0.0.0.0
DJANGO_PORT=8001

# Base de datos PostgreSQL
POSTGRES_DB=nombre_de_tu_bd
POSTGRES_USER=usuario
POSTGRES_PASSWORD=contraseña

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin

# Redis
REDIS_URL=redis://redis:6379/0
```

---

## 🛠️ Comandos de uso

### Levantar los contenedores (modo desarrollo)

```bash
docker-compose up --build
```

### Detener todos los servicios

```bash
docker-compose down
```

### Acceder al contenedor de Django

```bash
docker-compose exec web bash
```

### Ejecutar migraciones

```bash
docker-compose exec web python core/manage.py migrate
```

### Crear superusuario de Django

```bash
docker-compose exec web python core/manage.py createsuperuser
```

---

## 🌐 Accesos por defecto

- **Django App**: http://localhost:8001/
- **pgAdmin**: http://localhost  
  - Usuario: `${PGADMIN_DEFAULT_EMAIL}`  
  - Contraseña: `${PGADMIN_DEFAULT_PASSWORD}`

Para conectar la base de datos en pgAdmin, usa los siguientes datos:
- Host: `db`
- Puerto: `5432`
- Usuario: `${POSTGRES_USER}`
- Contraseña: `${POSTGRES_PASSWORD}`
- Base de datos: `${POSTGRES_DB}`

---

## 🧹 Limpieza (opcional)

Para eliminar volúmenes y recursos asociados:

```bash
docker-compose down -v
```

---

## 📦 Requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Python ≥ 3.9 (solo si se usa localmente fuera de Docker)

--- 
## 🌐 Documentacion de Endpoints
- [URL Documentation Swagger](http://localhost:8001/doc/)
- [URL Documentation alternativo Swagger](http://localhost:8001/redoc/)

