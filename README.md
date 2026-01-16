# Contrato Realidad AI - Legal Assistant

A Streamlit-based legal assistant for Colombian labor law cases involving "contrato realidad" (reality contract) claims with advanced RAG (Retrieval-Augmented Generation) capabilities.

## Features

- **AI-Powered Legal Analysis**: Uses OpenAI GPT models for legal document generation
- **Advanced RAG System**: 
  - **RAG Básico**: Keyword-based legal information retrieval
  - **RAG Vectorial**: Semantic search with embeddings for precise legal references
- **Knowledge Management**: Add, edit, and manage legal knowledge base
- **Multi-Phase Workflow**: 
  - Phase 1: Case analysis and technical summary
  - Phase 2: Legal viability assessment
  - Phase 3: Guided legal document drafting
- **Document Export**: Generate Word documents (.docx) for legal documents
- **Interactive Interface**: User-friendly Streamlit interface with navigation

## RAG System Benefits

### **RAG Básico (Basic RAG)**
- **Keyword-based search** in legal knowledge base
- **Fast retrieval** of relevant legal information
- **References to Colombian labor law** and jurisprudence
- **Lower computational cost**

### **RAG Vectorial (Vector RAG)**
- **Semantic search** using OpenAI embeddings
- **Higher precision** in legal information retrieval
- **Advanced similarity matching** for complex legal queries
- **Better context understanding** for nuanced legal cases

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LlamaIndex Cloud API (Optional - for OCR functionality)
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
```

**Note:** To use OCR functionality with LlamaCloud API:
1. Register at https://www.llamaindex.ai/ to get an API key
2. Add `LLAMA_CLOUD_API_KEY` to your `.env` file
3. If not provided, the app will fall back to local OCR (pytesseract)

### 3. Run the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Deployment / Publicación

### Opción 1: Streamlit Cloud (Recomendado - Gratis)

1. **Preparar el repositorio:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Subir a GitHub:**
   - Crea un repositorio en GitHub
   - Conecta tu repositorio local:
     ```bash
     git remote add origin https://github.com/tu-usuario/tu-repo.git
     git push -u origin main
     ```

3. **Desplegar en Streamlit Cloud:**
   - Ve a https://share.streamlit.io/
   - Conecta tu cuenta de GitHub
   - Selecciona el repositorio
   - Configura las variables de entorno:
     - `OPENAI_API_KEY`: Tu clave de OpenAI
     - `LLAMA_CLOUD_API_KEY`: Tu clave de LlamaCloud (opcional)
   - Click en "Deploy"

4. **Notas importantes:**
   - El archivo `.env` NO se sube (está en .gitignore)
   - Las variables de entorno se configuran en Streamlit Cloud
   - El logo debe estar en `assets/logo_conde_abogados.png`

### Opción 2: Docker

1. **Crear Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Construir y ejecutar:**
   ```bash
   docker build -t contrato-realidad-ai .
   docker run -p 8501:8501 -e OPENAI_API_KEY=tu_key contrato-realidad-ai
   ```

### Opción 3: Servidor propio

1. **Instalar dependencias del sistema:**
   ```bash
   # Para OCR (Tesseract)
   sudo apt-get install tesseract-ocr tesseract-ocr-spa poppler-utils
   
   # O en macOS
   brew install tesseract tesseract-lang poppler
   ```

2. **Configurar variables de entorno:**
   ```bash
   export OPENAI_API_KEY=tu_key
   export LLAMA_CLOUD_API_KEY=tu_key
   ```

3. **Ejecutar con systemd o supervisor:**
   ```bash
   streamlit run app.py --server.port=8501
   ```

### Variables de Entorno Requeridas

- `OPENAI_API_KEY`: **Requerida** - Para generación de texto con GPT
- `LLAMA_CLOUD_API_KEY`: **Opcional** - Para OCR con LlamaCloud API

### Limitaciones en Cloud

- **Whisper (Transcripción)**: Requiere descargar modelos grandes, puede ser lento en la primera ejecución
- **OCR local (pytesseract)**: No funciona en Streamlit Cloud (requiere Tesseract instalado)
- **OCR con LlamaCloud**: Funciona perfectamente en cloud
- **Archivos grandes**: Los PDFs grandes pueden tardar más en procesarse

## File Structure

```
contrato_realidad_ai/
├── app.py                 # Main Streamlit application
├── extraer_patrones.py    # Script para extraer patrones de documentos de referencia
├── requirements.txt       # Python dependencies
├── README.md            # This file
└── utils/
    ├── rag.py           # Basic RAG implementation
    ├── vector_rag.py    # Advanced vector-based RAG
    ├── knowledge_manager.py # Knowledge base management
    ├── documento_referencia.py # Reference document patterns
    ├── exportar.py      # Document export functionality
    ├── resumen.py       # Legal summary generation
    ├── viabilidad.py    # Legal viability assessment
    └── por_secciones.py # Section-by-section document generation
```

## Usage

### **Extraer Patrones de Documento de Referencia**

Antes de usar la aplicación, puedes extraer patrones de redacción de un documento de referencia:

```bash
# Extraer patrones de un PDF
python extraer_patrones.py documento_referencia.pdf

# Especificar archivo de salida
python extraer_patrones.py documento_referencia.pdf --output mis_patrones.json

# Usar OCR si el PDF está escaneado
python extraer_patrones.py documento_referencia.pdf --ocr
```

Esto generará un archivo JSON con los patrones que puedes cargar en la aplicación.

### **Asistente Jurídico (Legal Assistant)**
1. **Select RAG Mode**: Choose between "Sin RAG", "RAG Básico", or "RAG Vectorial"
2. **Phase 1**: Enter case facts and generate technical summary
3. **Phase 2**: Get legal viability assessment with legal references
4. **Phase 3**: Draft legal documents section by section
5. **Phase 4**: Load reference patterns (optional) and draft demand section by section
6. **Export**: Download generated documents in Word format

### **Gestor de Conocimiento (Knowledge Manager)**
1. **View Knowledge Base**: Browse existing legal information
2. **Add Documents**: Add new legal documents, jurisprudence, or regulations
3. **Search**: Search through the knowledge base
4. **Export/Import**: Backup or restore knowledge base

## RAG System Architecture

### **Knowledge Base Components**
- **Contrato Realidad**: Legal concepts, elements, jurisprudence, and regulations
- **Derecho Laboral Colombiano**: Labor law principles and worker rights
- **Demanda Laboral**: Legal process requirements and deadlines

### **Retrieval Methods**
1. **Keyword Matching**: Basic RAG uses keyword-based search
2. **Semantic Search**: Vector RAG uses cosine similarity with embeddings
3. **Context Enhancement**: Combines retrieved information with user queries

### **Generation Process**
1. **Query Processing**: Analyze user input and context
2. **Information Retrieval**: Find relevant legal documents
3. **Context Building**: Combine retrieved information with query
4. **Response Generation**: Generate informed legal responses

## Development Notes

- **Embeddings Cache**: Vector RAG caches embeddings for performance
- **Similarity Threshold**: 0.3 minimum similarity for relevant documents
- **Knowledge Persistence**: Legal knowledge stored in JSON format
- **Session Management**: Streamlit session state for workflow continuity

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Verify OPENAI_API_KEY is set in `.env`
   - Check that the `.env` file is in the project root

2. **OpenAI API Errors**
   - Check that OPENAI_API_KEY is valid and has sufficient credits
   - Verify the API key has access to the required models (GPT-4o-mini, text-embedding-3-small)

3. **RAG Performance Issues**
   - Vector RAG requires more API calls for embeddings
   - Consider using Basic RAG for faster responses
   - Check OpenAI rate limits and quotas

4. **Knowledge Base Issues**
   - Verify JSON format in knowledge base files
   - Check file permissions for knowledge base operations
   - Ensure proper encoding (UTF-8) for Spanish text

## Advanced Features

### **Knowledge Base Management**
- **Add Custom Legal Documents**: Include firm-specific legal knowledge
- **Update Jurisprudence**: Keep knowledge base current with new rulings
- **Export/Import**: Share knowledge bases between teams
- **Search Functionality**: Find specific legal information quickly

### **RAG Configuration**
- **Mode Selection**: Choose appropriate RAG mode for your use case
- **Performance Optimization**: Balance speed vs. accuracy
- **Custom Knowledge**: Integrate your own legal expertise

## License

This project is for educational and legal professional use. Ensure compliance with local data protection and legal requirements. 