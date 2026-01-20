# Configuración de Variables de Entorno en Streamlit Cloud

## Variables de Entorno Requeridas

### 1. OPENAI_API_KEY (REQUERIDA)

**Nombre de la variable:** `OPENAI_API_KEY`

**Valor:** Tu clave de API de OpenAI

**Descripción:** Esta clave es necesaria para todas las funcionalidades de generación de texto con GPT (resúmenes, conceptos, redacción de demandas, etc.)

**Cómo obtenerla:**
1. Ve a https://platform.openai.com/api-keys
2. Inicia sesión en tu cuenta de OpenAI
3. Click en "Create new secret key"
4. Copia la clave generada (empieza con `sk-`)

**Ejemplo:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 2. LLAMA_CLOUD_API_KEY (OPCIONAL)

**Nombre de la variable:** `LLAMA_CLOUD_API_KEY`

**Valor:** `llx-ICTkT2ClPcIAJyTU5u70qiNg9WfrekiEVkZNcFCAMd8JJp1L`

**Descripción:** Esta clave permite usar la API de LlamaCloud para OCR de alta calidad en PDFs escaneados. Si no se configura, la app usará métodos alternativos (que pueden no funcionar en cloud).

**Nota:** Ya tienes esta clave configurada. Solo cópiala y pégala.

**Ejemplo:**
```
LLAMA_CLOUD_API_KEY=llx-ICTkT2ClPcIAJyTU5u70qiNg9WfrekiEVkZNcFCAMd8JJp1L
```

---

## Instrucciones Paso a Paso para Streamlit Cloud

### Paso 1: Acceder a Streamlit Cloud
1. Ve a https://share.streamlit.io/
2. Inicia sesión con tu cuenta de GitHub

### Paso 2: Crear Nueva App
1. Click en el botón **"New app"** o **"Deploy an app"**
2. Selecciona tu cuenta/organización si es necesario

### Paso 3: Configurar Repositorio
1. **Repository:** Selecciona `mamvvt99-glitch/contrato-realidad-ai`
2. **Branch:** `main`
3. **Main file path:** `app.py`

### Paso 4: Configurar Variables de Entorno (IMPORTANTE)
1. Click en **"Advanced settings"** o **"⚙️ Settings"**
2. Busca la sección **"Secrets"** o **"Environment variables"**
3. Agrega las siguientes variables:

#### Variable 1: OPENAI_API_KEY
- **Key:** `OPENAI_API_KEY`
- **Value:** `TU_CLAVE_DE_OPENAI_AQUI` (reemplaza con tu clave real que empieza con `sk-`)

#### Variable 2: LLAMA_CLOUD_API_KEY
- **Key:** `LLAMA_CLOUD_API_KEY`
- **Value:** `llx-ICTkT2ClPcIAJyTU5u70qiNg9WfrekiEVkZNcFCAMd8JJp1L`

### Paso 5: Desplegar
1. Click en el botón **"Deploy"** o **"Save"**
2. Espera 2-5 minutos mientras Streamlit Cloud:
   - Instala las dependencias
   - Configura el entorno
   - Inicia la aplicación

### Paso 6: Verificar
1. Una vez desplegado, verás la URL de tu app (ej: `https://contrato-realidad-ai.streamlit.app`)
2. Click en la URL para abrir la aplicación
3. Verifica que la app carga correctamente

---

## Formato TOML (Alternativa)

Si Streamlit Cloud te permite usar formato TOML para secrets, puedes usar:

```toml
OPENAI_API_KEY = "TU_CLAVE_DE_OPENAI_AQUI"
LLAMA_CLOUD_API_KEY = "llx-ICTkT2ClPcIAJyTU5u70qiNg9WfrekiEVkZNcFCAMd8JJp1L"
```

**Nota:** Reemplaza `TU_CLAVE_DE_OPENAI_AQUI` con tu clave real de OpenAI.

---

## Verificación Post-Despliegue

### ✅ Checklist de Verificación

- [ ] La app carga sin errores
- [ ] Puedes navegar entre las diferentes páginas
- [ ] El modo RAG se puede seleccionar
- [ ] Puedes cargar un expediente PDF
- [ ] La generación de resúmenes funciona
- [ ] La generación de conceptos funciona
- [ ] La redacción de demandas funciona

### 🔍 Si hay Errores

**Error: "OPENAI_API_KEY not found"**
- Verifica que la variable esté configurada correctamente
- Asegúrate de que el nombre sea exactamente `OPENAI_API_KEY`
- Verifica que no haya espacios extra

**Error: "Module not found"**
- Revisa los logs en Streamlit Cloud
- Verifica que `requirements.txt` incluya todas las dependencias

**Error: "OCR no funciona"**
- Verifica que `LLAMA_CLOUD_API_KEY` esté configurada
- Si no está configurada, algunas funcionalidades de OCR no estarán disponibles

---

## Notas Importantes

⚠️ **Seguridad:**
- Nunca compartas tus API keys públicamente
- Las keys en Streamlit Cloud están encriptadas y son seguras
- Si comprometes una key, revócarla inmediatamente en la plataforma correspondiente

💡 **Rendimiento:**
- La primera carga puede ser lenta (descarga de modelos)
- Usa "RAG Básico" para mejor rendimiento
- Los PDFs grandes pueden tardar más en procesarse

🔧 **Actualizaciones:**
- Cada vez que hagas push a `main`, Streamlit Cloud redeployará automáticamente
- Los cambios pueden tardar 1-2 minutos en reflejarse


