# Guía de Despliegue - Asistente Jurídico Contrato Realidad

## 🚀 Despliegue en Streamlit Cloud (Recomendado)

### Paso 1: Preparar el Repositorio

```bash
# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer commit inicial
git commit -m "Initial commit: Asistente Jurídico Contrato Realidad"
```

### Paso 2: Subir a GitHub

1. Crea un nuevo repositorio en GitHub (https://github.com/new)
2. **NO** inicialices con README, .gitignore o licencia
3. Conecta tu repositorio local:

```bash
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
git branch -M main
git push -u origin main
```

### Paso 3: Desplegar en Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Inicia sesión con tu cuenta de GitHub
3. Click en "New app"
4. Selecciona:
   - **Repository**: Tu repositorio
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click en "Advanced settings"
6. Agrega las variables de entorno:
   - `OPENAI_API_KEY`: Tu clave de OpenAI (requerida)
   - `LLAMA_CLOUD_API_KEY`: Tu clave de LlamaCloud (opcional)
7. Click en "Deploy"

### Paso 4: Verificar el Despliegue

- La app estará disponible en: `https://tu-app.streamlit.app`
- Puede tardar 2-5 minutos en desplegarse la primera vez
- Revisa los logs si hay errores

## 📝 Notas Importantes

### Archivos que NO se suben (están en .gitignore):
- `.env` - Variables de entorno (configúralas en Streamlit Cloud)
- `venv/` - Entorno virtual
- `patrones_referencia.json` - Patrones generados localmente
- Archivos PDF/DOCX subidos por usuarios

### Funcionalidades en Cloud:

✅ **Funciona:**
- Generación de resúmenes y conceptos
- Generación de demandas por secciones
- RAG Básico y Vectorial
- OCR con LlamaCloud API
- Exportación a Word
- Gestor de conocimiento

⚠️ **Limitaciones:**
- Transcripción con Whisper: Funciona pero es lento (descarga modelos)
- OCR local (pytesseract): No funciona (requiere Tesseract instalado)
- Archivos muy grandes: Pueden tardar más

### Solución para OCR en Cloud:

Usa la API de LlamaCloud configurando `LLAMA_CLOUD_API_KEY` en Streamlit Cloud.

## 🔧 Troubleshooting

### Error: "Module not found"
- Verifica que `requirements.txt` incluya todas las dependencias
- Revisa los logs en Streamlit Cloud

### Error: "API key not found"
- Verifica que las variables de entorno estén configuradas en Streamlit Cloud
- Revisa que los nombres sean exactos: `OPENAI_API_KEY`, `LLAMA_CLOUD_API_KEY`

### Error: "Logo not found"
- El logo es opcional, la app funcionará sin él
- Si quieres el logo, asegúrate de que `assets/logo_conde_abogados.png` esté en el repo

### La app es lenta
- Primera carga puede ser lenta (descarga de modelos)
- Usa RAG Básico en lugar de Vectorial para más velocidad
- Considera usar modelos más pequeños si es necesario

## 🔐 Seguridad

- **NUNCA** subas el archivo `.env` al repositorio
- Usa variables de entorno en Streamlit Cloud
- Las API keys son sensibles, mantenlas seguras
- Revisa los permisos del repositorio (público vs privado)

## 📊 Monitoreo

- Revisa los logs en Streamlit Cloud dashboard
- Monitorea el uso de API keys (OpenAI, LlamaCloud)
- Verifica el rendimiento de la aplicación

