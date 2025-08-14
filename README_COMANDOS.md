# Comandos de Población de Datos de Prueba

Este proyecto incluye varios comandos de Django para poblar las tablas con datos de prueba para desarrollo y testing.

## Comandos Disponibles

### 1. `poblar_datos_prueba` - Banco de Sangre
Puebla datos de donantes, médicos y unidades de muestra.

**Ubicación:** `banco_sangre/management/commands/`

**Uso:**
```bash
python manage.py poblar_datos_prueba
python manage.py poblar_datos_prueba --donantes 100 --medicos 30 --unidades 200
```

### 2. `poblar_examenes_prueba` - Exámenes y Laboratorio
Puebla datos de exámenes, donantes, órdenes y resultados.

**Ubicación:** `examenes/management/commands/`

**Uso:**
```bash
python manage.py poblar_examenes_prueba
python manage.py poblar_examenes_prueba --examenes 50 --donantes 100 --ordenes 200 --resultados 150
```

### 3. `poblar_todo` - Comando Completo
Ejecuta ambos comandos para poblar todos los datos de prueba.

**Ubicación:** `banco_sangre/management/commands/`

**Uso:**
```bash
python manage.py poblar_todo
python manage.py poblar_todo --donantes 100 --medicos 30 --examenes 50 --pacientes 100 --ordenes 200 --resultados 150
```

## Datos Generados

### Usuario Administrador
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Email:** `admin@labclinic.com`

### Localización
- País: Guatemala
- Departamentos: Guatemala, Quetzaltenango, Petén, Alta Verapaz, Baja Verapaz
- Municipios: Varios municipios por departamento

### Banco de Sangre
- **Donantes:** Con CUIs únicos, edades 18-65 años, 75% aptos
- **Médicos:** Con especialidades variadas, datos de contacto completos
- **Unidades de Muestra:** Plasma, Paquete Globular, Plaquetas, Crio Precipitado

### Laboratorio Clínico
- **Exámenes:** 15 tipos diferentes en 5 categorías (Hematología, Bioquímica, Inmunología, Microbiología, Endocrinología)
- **Donantes:** Con datos completos, edades 18-65 años, CUIs únicos
- **Órdenes:** Con códigos únicos, 1-3 exámenes por orden
- **Resultados:** Con valores realistas según el tipo de examen

## Ejemplos de Uso

### Población Rápida (Recomendado para desarrollo)
```bash
python manage.py poblar_todo
```

### Población Personalizada
```bash
# Solo banco de sangre
python manage.py poblar_datos_prueba --donantes 100 --medicos 20 --unidades 150

# Solo laboratorio
python manage.py poblar_examenes_prueba --examenes 40 --donantes 75 --ordenes 120 --resultados 100

# Población completa personalizada
python manage.py poblar_todo --donantes 200 --medicos 50 --examenes 60 --donantes 150 --ordenes 300 --resultados 250
```

### Población Mínima para Testing
```bash
python manage.py poblar_todo --donantes 10 --medicos 5 --examenes 15 --donantes 20 --ordenes 30 --resultados 25
```

## Estructura de Archivos

```
banco_sangre/management/commands/
├── poblar_datos_prueba.py    # Comando para banco de sangre
├── poblar_todo.py            # Comando completo
└── README.md                 # Documentación

examenes/management/commands/
├── poblar_examenes_prueba.py # Comando para laboratorio
└── README.md                 # Documentación
```

## Características

- **Idempotente:** Puede ejecutarse múltiples veces sin duplicar datos
- **Realista:** Los datos generados son realistas pero ficticios
- **Configurable:** Parámetros para controlar la cantidad de datos
- **Completo:** Cubre todos los módulos principales del sistema
- **Documentado:** Cada comando incluye documentación detallada

## Notas Importantes

1. **Ejecutar migraciones primero:**
   ```bash
   python manage.py migrate
   ```

2. **Crear superusuario si es necesario:**
   ```bash
   python manage.py createsuperuser
   ```

3. **Los comandos crean automáticamente:**
   - Usuario administrador si no existe
   - Datos de localización básicos
   - Médicos si no existen

4. **Para desarrollo local:**
   - Usar `poblar_todo` para datos completos
   - Usar parámetros menores para testing rápido

5. **Para producción:**
   - NO ejecutar estos comandos en producción
   - Solo usar para desarrollo y testing 