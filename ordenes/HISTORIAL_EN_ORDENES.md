# 📋 Historial de Denegaciones en Órdenes

El historial de denegaciones ahora viene **automáticamente incluido** en el endpoint de órdenes.

## 🎯 ¿Cómo Funciona?

Cuando consultas una orden, el campo `historial_denegaciones` trae automáticamente todas las denegaciones asociadas a esa orden.

## 📊 Endpoints

### **1. Listar Órdenes (con historial)**

```
GET /api/ordenes/
```

### **2. Ver Detalle de Orden (con historial)**

```
GET /api/ordenes/{id}/
```

## 📝 Ejemplo de Respuesta

```json
{
    "id": 123,
    "codigo": "ORD-20251021-0123",
    "paciente": null,
    "paciente_nombre": null,
    "donante": 45,
    "donante_nombre": "Juan Carlos Pérez López (1234567890123)",
    "codigo_donante": "DON-045-0123",
    "genero_entrevista": true,
    "continuar_entrevista": false,
    "medico": 10,
    "medico_nombre": "Dr. Carlos Martínez",
    "fecha": "2025-10-21",
    "hora": "10:30:00",
    "estado": "VALIDADO",
    "prioridad": "NORMAL",
    "total_examenes": 1,
    "detalles": [
        {
            "id": 456,
            "examen": {
                "id": 15,
                "nombre": "Perfil Serológico Completo",
                "codigo": "SER-001"
            },
            "estado": "VALIDADO",
            "observaciones": "",
            "resultado": null
        }
    ],
    "historial_denegaciones": [
        {
            "id": 1,
            "donante": 45,
            "donante_nombre": "Juan Carlos Pérez López (1234567890123)",
            "resultado": 175,
            "orden": 123,
            "orden_codigo": "ORD-20251021-0123",
            "motivo_denegacion": 3,
            "motivo_detalle": {
                "id": 3,
                "codigo": "DENE-003",
                "nombre": "VIH Reactivo (HIV Ab/Ag)",
                "descripcion": "Resultado positivo para anticuerpos y/o antígenos del VIH",
                "activo": true,
                "fecha_creacion": "2025-10-21T10:00:00Z"
            },
            "observaciones": "Resultado confirmado HIV positivo. Se refiere a unidad de infectología.",
            "usuario_deniego": "DR001",
            "fecha_denegacion": "2025-10-21T14:30:00Z",
            "resultado_examen": "Perfil Serológico Completo",
            "valores_criticos": {
                "HIV Ab/Ag": {
                    "valor": "Reactivo",
                    "unidad": "",
                    "rango_normal": "No Reactivo",
                    "estado": "anormal"
                }
            }
        }
    ]
}
```

## 🔍 Interpretación del Campo `historial_denegaciones`

### **Si está vacío `[]`:**
```json
"historial_denegaciones": []
```
✅ **Significa:** Esta orden NO tiene denegaciones. El donante fue apto o aún no se ha validado.

### **Si tiene registros:**
```json
"historial_denegaciones": [
    {
        "motivo_detalle": {
            "codigo": "DENE-003",
            "nombre": "VIH Reactivo"
        },
        "fecha_denegacion": "2025-10-21T14:30:00Z",
        "valores_criticos": {...}
    }
]
```
❌ **Significa:** El donante fue denegado. Muestra motivo, fecha y valores críticos.

## 🎨 Uso en el Frontend

### **Mostrar historial en la tabla de órdenes:**

```javascript
// Listar órdenes con indicador visual
ordenes.forEach(orden => {
    const tieneDenegaciones = orden.historial_denegaciones.length > 0;
    
    if (tieneDenegaciones) {
        console.log(`⚠️ Orden ${orden.codigo} - DONANTE DENEGADO`);
        console.log(`   Motivo: ${orden.historial_denegaciones[0].motivo_detalle.nombre}`);
    } else {
        console.log(`✅ Orden ${orden.codigo} - Sin denegaciones`);
    }
});
```

### **Mostrar alerta si hay denegaciones:**

```javascript
const verDetalleOrden = async (ordenId) => {
    const response = await fetch(`/api/ordenes/${ordenId}/`);
    const orden = await response.json();
    
    // Verificar si hay denegaciones
    if (orden.historial_denegaciones.length > 0) {
        const ultimaDenegacion = orden.historial_denegaciones[0];
        
        alert(`
            ⚠️ DONANTE DENEGADO
            
            Motivo: ${ultimaDenegacion.motivo_detalle.nombre}
            Fecha: ${new Date(ultimaDenegacion.fecha_denegacion).toLocaleDateString()}
            Por: ${ultimaDenegacion.usuario_deniego}
            
            Observaciones: ${ultimaDenegacion.observaciones}
        `);
        
        // Mostrar valores críticos
        console.log('Valores críticos:', ultimaDenegacion.valores_criticos);
    }
};
```

### **Mostrar badge en listado:**

```jsx
// React/Vue ejemplo
<tr v-for="orden in ordenes" :key="orden.id">
    <td>{{ orden.codigo }}</td>
    <td>{{ orden.donante_nombre }}</td>
    <td>{{ orden.estado }}</td>
    <td>
        <span v-if="orden.historial_denegaciones.length > 0" 
              class="badge badge-danger">
            🚫 DENEGADO: {{ orden.historial_denegaciones[0].motivo_detalle.codigo }}
        </span>
        <span v-else class="badge badge-success">
            ✅ Sin denegaciones
        </span>
    </td>
</tr>
```

### **Tooltip con detalles:**

```javascript
function generarTooltip(orden) {
    if (orden.historial_denegaciones.length === 0) {
        return 'Donante apto - Sin denegaciones';
    }
    
    const denegaciones = orden.historial_denegaciones;
    let tooltip = `🚫 Donante con ${denegaciones.length} denegación(es):\n\n`;
    
    denegaciones.forEach((denegacion, index) => {
        tooltip += `${index + 1}. ${denegacion.motivo_detalle.nombre}\n`;
        tooltip += `   Fecha: ${new Date(denegacion.fecha_denegacion).toLocaleDateString()}\n`;
        tooltip += `   Por: ${denegacion.usuario_deniego}\n\n`;
    });
    
    return tooltip;
}
```

## 📊 Casos de Uso

### **1. Dashboard de Órdenes**
Mostrar indicador visual en cada orden si tiene denegaciones.

### **2. Detalle de Orden**
Mostrar sección expandible con historial completo de denegaciones.

### **3. Búsqueda de Órdenes Denegadas**
Filtrar órdenes que tengan `historial_denegaciones.length > 0`.

### **4. Reportes**
Generar reportes de denegaciones directamente desde las órdenes.

## ⚡ Ventajas

1. ✅ **Un solo request**: No necesitas hacer llamadas adicionales
2. ✅ **Datos completos**: Incluye motivo detallado y valores críticos
3. ✅ **Mejor performance**: Optimizado con `select_related`
4. ✅ **Más simple**: Menos complejidad en el frontend

## 🔄 Flujo Completo

```
1. Crear Orden
   GET /api/ordenes/123/
   └─> historial_denegaciones: []  (vacío, sin denegaciones)

2. Validar Resultado (denegar)
   PUT /api/resultados/resultados/175/validar/
   {
       "donante_apto": false,
       "motivo_denegacion_id": 3
   }

3. Consultar Orden de Nuevo
   GET /api/ordenes/123/
   └─> historial_denegaciones: [{...}]  (ahora tiene el registro)
```

## 📝 Notas Importantes

- ✅ El historial se actualiza **automáticamente** al validar resultados
- ✅ Incluye **todas las denegaciones** de la orden (puede haber múltiples)
- ✅ Ordenado por fecha (más reciente primero)
- ✅ Si no hay denegaciones, retorna array vacío `[]`
- ✅ Incluye información completa del motivo y valores críticos

## 🎯 Ejemplo Completo Frontend

```javascript
// Componente de Orden con Historial
class OrdenConHistorial {
    async cargarOrden(ordenId) {
        const response = await fetch(`/api/ordenes/${ordenId}/`);
        const orden = await response.json();
        
        // Renderizar orden básica
        this.renderOrden(orden);
        
        // Renderizar historial de denegaciones
        if (orden.historial_denegaciones.length > 0) {
            this.mostrarAlertaDenegacion();
            this.renderHistorialDenegaciones(orden.historial_denegaciones);
        }
    }
    
    renderHistorialDenegaciones(historial) {
        historial.forEach(denegacion => {
            console.log(`
                🚫 Denegación:
                   Motivo: ${denegacion.motivo_detalle.nombre}
                   Código: ${denegacion.motivo_detalle.codigo}
                   Fecha: ${denegacion.fecha_denegacion}
                   Usuario: ${denegacion.usuario_deniego}
                   Examen: ${denegacion.resultado_examen}
                   Observaciones: ${denegacion.observaciones}
            `);
            
            // Mostrar valores críticos
            Object.entries(denegacion.valores_criticos).forEach(([parametro, datos]) => {
                console.log(`   ⚠️ ${parametro}: ${datos.valor} ${datos.unidad} (${datos.estado})`);
            });
        });
    }
    
    mostrarAlertaDenegacion() {
        // Mostrar banner/alerta visual en la UI
        document.getElementById('alert-denegacion').style.display = 'block';
    }
}
```

---

**Ventaja Principal:** Ya no necesitas hacer un request adicional a `/api/resultados/historial-denegaciones/`. Todo viene en la orden. 🚀

