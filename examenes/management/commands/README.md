# Comando de Población de Datos de Prueba - Exámenes

Este comando permite poblar las tablas del sistema con datos de prueba para exámenes, donantes, órdenes y resultados.

## Uso

```bash
# Poblar con valores por defecto
python manage.py poblar_examenes_prueba

# Poblar con cantidades específicas
python manage.py poblar_examenes_prueba --examenes 50 --donantes 100 --ordenes 200 --resultados 150

# Solo exámenes
python manage.py poblar_examenes_prueba --examenes 40

# Solo donantes
python manage.py poblar_examenes_prueba --donantes 75

# Solo órdenes
python manage.py poblar_examenes_prueba --ordenes 150

# Solo resultados
python manage.py poblar_examenes_prueba --resultados 100
```

## Parámetros

- `--examenes`: Número de exámenes a crear (default: 30)
- `--donantes`: Número de donantes a crear (default: 50)
- `--ordenes`: Número de órdenes a crear (default: 100)
- `--resultados`: Número de resultados a crear (default: 80)

## Datos Generados

### Usuario Administrador
- Usuario: `admin`
- Contraseña: `admin123`
- Email: `admin@labclinic.com`

### Localización
- País: Guatemala
- Departamentos: Guatemala, Quetzaltenango, Petén, Alta Verapaz, Baja Verapaz
- Municipios: Varios municipios por departamento

### Exámenes
Categorías y exámenes incluidos con valores de referencia en formato JSON:

#### Hematología
- Hemograma Completo (HEM001) - Q150.00
  - Hematíes, Hemoglobina, Leucocitos, Plaquetas, Hematocrito
- Recuento de Plaquetas (HEM002) - Q80.00
  - Plaquetas
- Velocidad de Sedimentación (HEM003) - Q60.00
  - VSG (hombres y mujeres)

#### Bioquímica
- Glucosa en Sangre (BIO001) - Q45.00
  - Glucosa en ayunas
- Perfil Lipídico (BIO002) - Q120.00
  - Colesterol Total, HDL, LDL, Triglicéridos
- Creatinina (BIO003) - Q50.00
  - Creatinina (hombres y mujeres)

#### Inmunología
- VIH 1/2 (INM001) - Q200.00
  - Resultado de VIH
- Hepatitis B (INM002) - Q180.00
  - HBsAg, Anti-HBs

#### Microbiología
- Cultivo de Orina (MIC001) - Q90.00
  - Cultivo bacteriano
- Antibiograma (MIC002) - Q150.00
  - Sensibilidad antibiótica

#### Endocrinología
- TSH (END001) - Q120.00
  - Hormona estimulante de tiroides
- T4 Libre (END002) - Q100.00
  - Tiroxina libre

### Donantes
- Nombres y apellidos realistas
- Edades entre 18 y 65 años
- CUIs únicos
- Datos de contacto completos
- 75% aptos para donación por defecto

### Órdenes
- Códigos únicos con formato ORD-YYYYMMDD-XXXX
- Fechas en los últimos 30 días
- 1-3 exámenes por orden
- Estados variados: Pendiente, Validado, En Proceso, Entregado, Cancelado
- Prioridades: Alta, Media, Normal

### Resultados
- Resultados realistas según el tipo de examen
- Valores dentro de rangos normales (con variaciones)
- Estados: Completado, Validado, En Proceso
- Detalles específicos por tipo de examen

## Ejemplos de Resultados

### Hemograma Completo
- Hematíes: 4.8 M/μL (normal)
- Hemoglobina: 14.2 g/dL (normal)
- Leucocitos: 7.5 K/μL (normal)
- Plaquetas: 250 K/μL (normal)

### Perfil Lipídico
- Colesterol Total: 180 mg/dL (normal)
- HDL: 45 mg/dL (normal)
- LDL: 110 mg/dL (alto)
- Triglicéridos: 150 mg/dL (normal)

## Formato de Valores de Referencia

Los valores de referencia se almacenan en formato JSON como un array de objetos con la siguiente estructura:

```json
[
  {
    "parametro": "nombre del parámetro",
    "rango": "rango o valor de referencia",
    "unidad": "unidad de medida"
  }
]
```

### Ejemplo para Hemograma Completo:
```json
[
  {"parametro": "Hematíes", "rango": "4.5-5.5", "unidad": "M/μL"},
  {"parametro": "Hemoglobina", "rango": "13-17", "unidad": "g/dL"},
  {"parametro": "Leucocitos", "rango": "4.5-11.0", "unidad": "K/μL"},
  {"parametro": "Plaquetas", "rango": "150-450", "unidad": "K/μL"},
  {"parametro": "Hematocrito", "rango": "40-50", "unidad": "%"}
]
```

## Notas

- El comando es idempotente: puede ejecutarse múltiples veces sin duplicar datos
- Los datos generados son realistas pero ficticios
- Se crean automáticamente médicos si no existen
- Los valores de referencia se almacenan en formato JSON
- Las órdenes se crean con donantes y médicos existentes 