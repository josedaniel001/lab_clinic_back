# 🔧 Solución para Errores SSL en el Navegador

## ❌ Problema Actual
El navegador muestra errores `net::ERR_CERT_AUTHORITY_INVALID` para `https://bioanalisisadmin.com`

## ✅ Soluciones

### **Opción 1: Configurar Chrome/Edge (Recomendado)**

1. **Abrir Chrome/Edge** y ir a `chrome://flags/` (o `edge://flags/`)

2. **Buscar** "Insecure origins treated as secure"

3. **Agregar** estos dominios:
   ```
   https://bioanalisisadmin.com
   https://bioanalisis.com
   https://www.bioanalisisadmin.com
   https://www.bioanalisis.com
   ```

4. **Reiniciar** el navegador

### **Opción 2: Configurar Firefox**

1. **Abrir Firefox** y ir a `about:config`

2. **Buscar** `security.enterprise_roots.enabled`

3. **Cambiar** a `true`

4. **Buscar** `security.cert_verification.require_trusted_anchor`

5. **Cambiar** a `false`

6. **Reiniciar** Firefox

### **Opción 3: Configurar manualmente en el navegador**

#### **Chrome/Edge:**
1. Ir a `https://bioanalisisadmin.com`
2. Hacer clic en "Avanzado"
3. Hacer clic en "Continuar a bioanalisisadmin.com (no seguro)"
4. Hacer clic en el candado en la barra de direcciones
5. Hacer clic en "Certificado"
6. Hacer clic en "Instalar certificado"
7. Seguir el asistente

#### **Firefox:**
1. Ir a `https://bioanalisisadmin.com`
2. Hacer clic en "Avanzado"
3. Hacer clic en "Aceptar el riesgo y continuar"
4. Hacer clic en el candado en la barra de direcciones
5. Hacer clic en "Ver certificado"
6. Hacer clic en "Ver certificado" en la nueva ventana
7. Ir a la pestaña "Detalles"
8. Hacer clic en "Exportar"
9. Guardar el certificado
10. Ir a Preferencias > Privacidad y Seguridad > Certificados
11. Hacer clic en "Ver certificados"
12. Importar el certificado guardado

### **Opción 4: Usar modo de desarrollo (Temporal)**

#### **Chrome/Edge:**
1. Abrir DevTools (F12)
2. Ir a la pestaña "Console"
3. Hacer clic en el ícono de configuración (⚙️)
4. Marcar "Ignore certificate errors"

#### **Firefox:**
1. Abrir DevTools (F12)
2. Ir a la pestaña "Console"
3. Hacer clic en el ícono de configuración (⚙️)
4. Marcar "Ignore certificate errors"

## 🚀 **Solución Rápida (Recomendada)**

### **Para Chrome/Edge:**
1. Abrir `chrome://flags/`
2. Buscar "Insecure origins treated as secure"
3. Agregar: `https://bioanalisisadmin.com,https://bioanalisis.com`
4. Reiniciar navegador

### **Para Firefox:**
1. Abrir `about:config`
2. Buscar `security.enterprise_roots.enabled`
3. Cambiar a `true`
4. Reiniciar Firefox

## 📝 **Verificación**

Después de aplicar cualquiera de las soluciones:

1. **Abrir** `https://bioanalisisadmin.com`
2. **Verificar** que no aparezcan errores SSL
3. **Probar** el endpoint `/api/health`
4. **Verificar** que el frontend pueda hacer peticiones al backend

## ⚠️ **Notas Importantes**

- Estas soluciones son para **desarrollo local**
- En producción, usar certificados válidos (Let's Encrypt, etc.)
- Los certificados autofirmados son normales en desarrollo
- El navegador debe confiar en los certificados para que funcione CORS

---
**Última actualización**: 9 de Agosto, 2025
