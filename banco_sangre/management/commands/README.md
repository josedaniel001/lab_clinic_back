# Comando de Población de Datos de Prueba

Este comando permite poblar las tablas del sistema con datos de prueba para desarrollo y testing.

## Uso

```bash
# Poblar con valores por defecto
python manage.py poblar_datos_prueba

# Poblar con cantidades específicas
python manage.py poblar_datos_prueba --donantes 100 --medicos 30 --unidades 200

# Solo médicos
python manage.py poblar_datos_prueba --medicos 50

# Solo donantes
python manage.py poblar_datos_prueba --donantes 75
```

## Parámetros

- `--donantes`: Número de donantes a crear (default: 50)
- `--medicos`: Número de médicos a crear (default: 20)
- `--unidades`: Número de unidades de muestra a crear (default: 100)

## Datos Generados

### Usuario Administrador
- Usuario: `admin`
- Contraseña: `admin123`
- Email: `admin@labclinic.com`

### Localización
- País: Guatemala
- Departamentos: Guatemala, Quetzaltenango, Petén, Alta Verapaz, Baja Verapaz
- Municipios: Varios municipios por departamento

### Médicos
- Nombres y apellidos realistas
- Especialidades médicas variadas
- Datos de contacto completos
- 75% activos por defecto

### Donantes
- CUIs únicos
- Edades entre 18 y 65 años
- Ocupaciones variadas
- 75% aptos para donación por defecto

### Unidades de Muestra
- Diferentes tipos: Plasma, Paquete Globular, Plaquetas, Crio Precipitado
- Tipos de sangre: A+, A-, B+, B-, AB+, AB-, O+, O-
- Fechas de extracción recientes
- Estados variados: Disponible, Reservado, Vencido

## Notas

- El comando es idempotente: puede ejecutarse múltiples veces sin duplicar datos
- Los datos generados son realistas pero ficticios
- Se crean automáticamente los lotes necesarios para las unidades de muestra 