# 📊 Módulo de Catálogos

## 🎯 **Descripción**

Módulo independiente para gestionar catálogos del sistema, específicamente el catálogo de unidades de parámetros de laboratorio.

## 📋 **Funcionalidades**

### **Catálogo de Unidades de Parámetros**
- ✅ CRUD completo para unidades de medida
- ✅ Categorización por tipo de laboratorio
- ✅ Búsqueda y filtrado avanzado
- ✅ Interface de administración Django
- ✅ API REST completa

## 🏗️ **Estructura del Módulo**

```
catalogos/
├── models.py              # Modelo CatalogoUnidadParametro
├── serializers.py         # Serializers para API
├── views.py              # ViewSets y endpoints
├── admin.py              # Configuración del admin
├── urls.py               # Rutas del módulo
├── management/
│   └── commands/
│       └── poblar_unidades_parametros.py
└── README.md             # Esta documentación
```

## 🚀 **Endpoints Disponibles**

### **Base URL:** `/api/catalogos/`

#### **CRUD Básico:**
- `GET /api/catalogos/unidades-parametros/` - Listar todas las unidades
- `POST /api/catalogos/unidades-parametros/` - Crear nueva unidad
- `GET /api/catalogos/unidades-parametros/{id}/` - Obtener unidad específica
- `PUT /api/catalogos/unidades-parametros/{id}/` - Actualizar unidad
- `DELETE /api/catalogos/unidades-parametros/{id}/` - Eliminar unidad

#### **Endpoints Especiales:**
- `GET /api/catalogos/unidades-parametros/categorias/` - Listar categorías
- `GET /api/catalogos/unidades-parametros/por-categoria/` - Agrupar por categoría
- `GET /api/catalogos/unidades-parametros/buscar/?q=termino` - Buscar unidades

## 🔍 **Filtros Disponibles**

### **Query Parameters:**
- `categoria` - Filtrar por categoría (ej: "Hematología")
- `activo` - Filtrar por estado activo (true/false)

### **Ejemplos:**
```
GET /api/catalogos/unidades-parametros/?categoria=Hematología
GET /api/catalogos/unidades-parametros/?activo=true
GET /api/catalogos/unidades-parametros/buscar/?q=g/dL
```

## 📊 **Modelo de Datos**

### **CatalogoUnidadParametro:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | AutoField | ID único |
| `codigo` | CharField(20) | Código único (ej: "GDL") |
| `nombre` | CharField(100) | Nombre completo |
| `simbolo` | CharField(20) | Símbolo (ej: "g/dL") |
| `categoria` | CharField(50) | Categoría (ej: "Hematología") |
| `descripcion` | TextField | Descripción detallada |
| `activo` | BooleanField | Estado activo |
| `fecha_creacion` | DateTimeField | Fecha de creación |

## 🎨 **Interface de Administración**

### **Características del Admin:**
- ✅ Lista con filtros por categoría y estado
- ✅ Búsqueda por código, nombre, símbolo
- ✅ Edición inline de campos activos
- ✅ Agrupación por fieldsets
- ✅ Ordenamiento por categoría y nombre

### **Acceso:**
- URL: `/admin/`
- Sección: "Unidades de Parámetros"

## 🛠️ **Comandos de Gestión**

### **Poblar Datos Iniciales:**
```bash
python manage.py poblar_unidades_parametros
```

**Incluye 20 unidades predefinidas:**
- **Hematología:** g/dL, M/μL, K/μL, %
- **Química Clínica:** mg/dL, μmol/L, mmol/L, UI/L
- **Endocrinología:** μUI/mL, ng/mL, pg/mL
- **Microbiología:** UFC/mL, Negativo, Positivo
- **Inmunología:** Reactivo, No Reactivo, Indeterminado
- **Otros:** mmHg, °C, L/min

## 📝 **Ejemplos de Uso**

### **Crear Nueva Unidad:**
```json
POST /api/catalogos/unidades-parametros/
{
    "codigo": "NGDL",
    "nombre": "Nanogramos por decilitro",
    "simbolo": "ng/dL",
    "categoria": "Endocrinología",
    "descripcion": "Unidad para hormonas de baja concentración",
    "activo": true
}
```

### **Buscar Unidades:**
```json
GET /api/catalogos/unidades-parametros/buscar/?q=hemoglobina

Response:
{
    "termino": "hemoglobina",
    "resultados": [
        {
            "id": 1,
            "codigo": "GDL",
            "nombre": "Gramos por decilitro",
            "simbolo": "g/dL",
            "categoria": "Hematología",
            "activo": true
        }
    ],
    "total": 1
}
```

### **Obtener Categorías:**
```json
GET /api/catalogos/unidades-parametros/categorias/

Response:
{
    "categorias": [
        "Endocrinología",
        "Hematología",
        "Inmunología",
        "Microbiología",
        "Otros",
        "Química Clínica"
    ]
}
```

## 🔧 **Configuración**

### **1. App Registrada:**
```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'catalogos',
]
```

### **2. URLs Configuradas:**
```python
# config/urls.py
urlpatterns = [
    # ...
    path('api/catalogos/', include('catalogos.urls')),
]
```

### **3. Migraciones:**
```bash
python manage.py makemigrations catalogos
python manage.py migrate
```

## ✅ **Ventajas del Módulo**

1. **🎯 Independiente:** No sobrecarga otros módulos
2. **📊 Especializado:** Enfocado en catálogos
3. **🔧 Extensible:** Fácil agregar nuevos catálogos
4. **🎨 Admin Completo:** Interface de administración optimizada
5. **🚀 API Robusta:** Endpoints especializados y filtros
6. **📝 Documentado:** Código bien documentado

## 🎉 **Resultado Final**

**Módulo completamente funcional con:**
- ✅ Modelo de datos optimizado
- ✅ API REST completa
- ✅ Interface de administración
- ✅ Comando de población de datos
- ✅ Documentación completa
- ✅ URLs configuradas
- ✅ App registrada en settings

**¡Listo para usar!** 🚀
