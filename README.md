# AgendaLite

Un proyecto Django para gestionar citas/agendamientos de manera simple y eficiente.

## 📋 Descripción del Proyecto

AgendaLite es una aplicación web construida con Django que permite gestionar citas y agendamientos. El proyecto utiliza:

- **Framework**: Django 6.0.1
- **Base de datos**: SQLite3
- **Python**: 3.x
- **Gestión de dependencias**: pip

## 🏗️ Estructura del Proyecto

```
agendalite/
├── manage.py                 # Script de administración de Django
├── requirements.txt          # Dependencias del proyecto
├── db.sqlite3               # Base de datos SQLite
├── .env                     # Variables de entorno
├── .gitignore              # Archivos ignorados por git
│
├── config/                  # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py         # Configuración de Django
│   ├── urls.py             # Rutas URL principales
│   ├── wsgi.py             # Configuración WSGI
│   └── asgi.py             # Configuración ASGI
│
└── apps/                    # Aplicaciones Django
    ├── __init__.py
    └── appointments/        # App para gestionar citas
        ├── __init__.py
        ├── admin.py        # Configuración del admin
        ├── apps.py         # Configuración de la app
        ├── models.py       # Modelos de datos
        ├── views.py        # Vistas/lógica
        ├── tests.py        # Pruebas unitarias
        └── migrations/     # Migraciones de BD
```

## 🚀 Cómo Levantar el Proyecto

### 1. **Clonar el repositorio**

```bash
git clone <url-del-repositorio>
cd agendalite
```

### 2. **Crear y activar el entorno virtual**

**En Windows (PowerShell/CMD):**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

### 4. **Configurar variables de entorno**

Crear un archivo `.env` en la raíz del proyecto (ya existe en este caso):

```env
DEBUG=True
SECRET_KEY=django-insecure-4yvifotrn5ryr5d*r&@9qocq(x7z-2(a-df5$$3va*+prl_kwl
```

### 5. **Ejecutar migraciones**

```bash
python manage.py migrate
```

### 6. **Crear un superusuario (opcional)**

```bash
python manage.py createsuperuser
```

Ingresa los datos cuando se solicite:
- Usuario
- Email
- Contraseña

### 7. **Ejecutar el servidor de desarrollo**

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## 📦 Dependencias Instaladas

- **Django** (6.0.1): Framework web principal
- **django-environ** (0.12.0): Gestión de variables de entorno
- **psycopg** (3.3.2): Adaptador PostgreSQL (incluido pero usando SQLite)
- **requests** (2.32.5): Librería HTTP para peticiones
- **sqlparse** (0.5.5): Parseador SQL
- **tzdata** (2025.3): Base de datos de zonas horarias
- **asgiref** (3.11.0): Utilidades ASGI

## 🗄️ Base de Datos

El proyecto utiliza **SQLite3** como base de datos predeterminada, almacenada en `db.sqlite3`.

### Migrar cambios en modelos

Después de modificar los modelos en `apps/appointments/models.py`:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 🔧 Aplicaciones Django Instaladas

- `django.contrib.admin`: Panel administrativo
- `django.contrib.auth`: Autenticación
- `django.contrib.contenttypes`: Sistema de tipos de contenido
- `django.contrib.sessions`: Manejo de sesiones
- `django.contrib.messages`: Sistema de mensajes
- `django.contrib.staticfiles`: Gestión de archivos estáticos
- `apps.appointments.apps.AppointmentsConfig`: App de citas

## 📝 Próximos Pasos

1. **Definir modelos** en `apps/appointments/models.py`
   - Crear modelo `Appointment` con campos necesarios
   - Considerar modelo `User` si es necesario

2. **Crear vistas** en `apps/appointments/views.py`
   - Listar citas
   - Crear nueva cita
   - Editar cita
   - Eliminar cita

3. **Configurar URLs** en `config/urls.py`
   - Añadir rutas de la app appointments

4. **Registrar modelos en admin** en `apps/appointments/admin.py`
   - Esto permitirá gestionar citas desde el panel admin

5. **Crear templates** (si es necesario)
   - Crear carpeta `templates/appointments/` con archivos HTML

## 💾 Comandos Útiles

```bash
# Ver todas las migraciones
python manage.py showmigrations

# Hacer migraciones específicas
python manage.py migrate appointments

# Crear aplicación nueva
python manage.py startapp nombre_app

# Ver shell interactivo
python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic

# Ejecutar tests
python manage.py test

# Crear superusuario
python manage.py createsuperuser
```

## 🔒 Notas de Seguridad

⚠️ **Para producción:**
- Cambiar `SECRET_KEY` por uno seguro
- Poner `DEBUG=False`
- Definir `ALLOWED_HOSTS` apropiadamente
- Usar variables de entorno reales
- Configurar HTTPS
- Usar una base de datos más robusta (PostgreSQL recomendado)

## 📚 Recursos Útiles

- [Documentación Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/) (si necesitas API)
- [Guía de Mejores Prácticas](https://docs.djangoproject.com/en/6.0/topics/db/models/)

## 👨‍💻 Autor

AgendaLite - Proyecto de Gestión de Citas

---

**Última actualización**: 20 de enero de 2026
