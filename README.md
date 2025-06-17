# 🧪 Sistema de Gestión para Laboratorio Clínico

Este proyecto es una plataforma web desarrollada con **Django** para el backend y **React (Next.js)** para el frontend. Su propósito es automatizar y facilitar el flujo completo de un laboratorio clínico: desde la recepción del paciente hasta la entrega e interpretación de resultados.

---

## 🚀 Características principales

- 🔐 Autenticación y gestión de usuarios con roles
- ✅ Permisos personalizados para vistas y acciones específicas
- 🧬 Registro y validación de pruebas de laboratorio
- 📋 Administración de pacientes, médicos y órdenes clínicas
- 📊 Módulo de reportes y estadísticas
- 🔔 Notificaciones en el dashboard

---

## ⚙️ Tecnologías utilizadas

### Backend:
- Python 3.11+
- Django 5.x
- Django REST Framework
- PostgreSQL (o SQLite en desarrollo)

### Frontend (repositorio separado):
- React con Next.js
- Tailwind CSS
- Axios

---

## 📦 Instalación del backend (Django)

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sistema-laboratorio.git
cd sistema-laboratorio


//CREAR ENTORNO VIRTUAL Y ACTIVARLO:
  python -m venv env
  # Activar en Windows
  env\Scripts\activate
  # En macOS/Linux
  source env/bin/activate

//INSTALAR DEPENDENCIAS:
pip install -r requirements.txt

//APLICAR MIGRACIONES:
python manage.py makemigrations
python manage.py migrate

 Crear superusuario (opcional pero recomendado):
python manage.py createsuperuser

Crear Permisos:
python manage.py cargar_permisos

Crear Roles:
python manage.py cargar_roles

Asignar Permisos:
python manage.py asignar_permisos_roles
python manage.py runserver

Estructura de Carpetas:
backend_lab/
├── usuarios/               # App de usuarios, roles y permisos
├── config/                 # Configuración general del proyecto
├── manage.py               # Utilidad de comandos Django
├── requirements.txt        # Lista de dependencias
└── README.md



---


```text
Se agrego la BD y el POSTMAN Collection en archivo
```markdown
USAR WINRAR PARA DESCOMPRIMIR


