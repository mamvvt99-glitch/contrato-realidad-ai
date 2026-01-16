# utils/expediente.py

import streamlit as st
import io
import tempfile
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def extraer_texto_pdf(pdf_file) -> Optional[str]:
    """
    Extrae texto de un archivo PDF.
    
    Args:
        pdf_file: Archivo PDF subido en Streamlit
        
    Returns:
        Texto extraído del PDF o None si hay error
    """
    try:
        # Intentar importar PyPDF2 (compatible con versiones 3.0+)
        try:
            import PyPDF2
            # Verificar si es versión 3.0+ (usa PdfReader) o anterior (usa PdfFileReader)
            if hasattr(PyPDF2, 'PdfReader'):
                pdf_reader = PyPDF2.PdfReader(pdf_file)
            else:
                # Versión antigua de PyPDF2
                pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                # Adaptar para versión antigua
                texto_completo = ""
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    texto_completo += page.extractText() + "\n\n"
                return texto_completo.strip()
        except ImportError:
            st.error("❌ PyPDF2 no está instalado.")
            st.info("💡 Para instalar, ejecuta: `pip install PyPDF2` o `pip install -r requirements.txt`")
            return None
        
        texto_completo = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            texto_completo += page.extract_text() + "\n\n"
        
        return texto_completo.strip()
    except Exception as e:
        st.error(f"❌ Error al extraer texto del PDF: {str(e)}")
        st.info("💡 Asegúrate de que el PDF contenga texto (no sea una imagen escaneada)")
        return None

def extraer_texto_pdf_ocr(pdf_file, usar_ocr: bool = True) -> Optional[str]:
    """
    Extrae texto de un archivo PDF usando OCR con la API de LlamaIndex (LlamaCloud).
    Útil para PDFs escaneados o con imágenes.
    
    Args:
        pdf_file: Archivo PDF subido en Streamlit
        usar_ocr: Si True, usa OCR para extraer texto de imágenes
        
    Returns:
        Texto extraído del PDF o None si hay error
    """
    # Obtener API key de LlamaCloud
    llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    
    if not llama_cloud_api_key:
        st.warning("⚠️ No se encontró LLAMA_CLOUD_API_KEY en las variables de entorno.")
        st.info("""
        💡 **Para usar la API de LlamaIndex:**
        1. Regístrate en https://www.llamaindex.ai/ para obtener una API key
        2. Agrega la clave a tu archivo `.env`:
           ```
           LLAMA_CLOUD_API_KEY=tu_clave_aqui
           ```
        3. O configúrala como variable de entorno del sistema
        """)
        st.info("🔄 Intentando método alternativo de OCR (pytesseract)...")
        # Intentar método alternativo
        if hasattr(pdf_file, 'seek'):
            pdf_file.seek(0)
        return extraer_texto_pdf_ocr_alternativo(pdf_file)
    
    # Guardar posición inicial del archivo
    if hasattr(pdf_file, 'seek'):
        posicion_inicial = pdf_file.tell()
        pdf_file.seek(0)
        pdf_content = pdf_file.read()
        pdf_file.seek(posicion_inicial)
    else:
        pdf_content = pdf_file.read() if hasattr(pdf_file, 'read') else pdf_file
    
    # Intentar primero con LlamaParse API
    try:
        from llama_index.readers.llama_parse import LlamaParse
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            if isinstance(pdf_content, bytes):
                tmp_file.write(pdf_content)
            else:
                tmp_file.write(pdf_content.read() if hasattr(pdf_content, 'read') else bytes(pdf_content))
            tmp_path = tmp_file.name
        
        try:
            # Usar LlamaParse con la API de LlamaCloud
            # Configuración para español y OCR habilitado
            from llama_parse import ResultType
            
            parser = LlamaParse(
                api_key=llama_cloud_api_key,
                language="es",  # Español
                result_type=ResultType.TXT,  # Obtener solo texto
                verbose=True
            )
            
            # Cargar documento usando la API
            with st.spinner("🔍 Procesando con LlamaCloud API (esto puede tomar varios minutos)..."):
                try:
                    # LlamaParse puede aceptar file_path o file
                    documents = parser.load_data(file=tmp_path)
                except Exception as load_error:
                    st.warning(f"⚠️ La API de LlamaIndex no pudo procesar el archivo: {str(load_error)}")
                    # Limpiar archivo temporal
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    # Intentar método alternativo
                    from io import BytesIO
                    pdf_file_obj = BytesIO(pdf_content) if isinstance(pdf_content, bytes) else pdf_content
                    return extraer_texto_pdf_ocr_alternativo(pdf_file_obj)
            
            # Extraer texto de los documentos
            texto_completo = ""
            for doc in documents:
                if hasattr(doc, 'text'):
                    texto_completo += doc.text + "\n\n"
                elif hasattr(doc, 'get_content'):
                    texto_completo += doc.get_content() + "\n\n"
                elif isinstance(doc, str):
                    texto_completo += doc + "\n\n"
            
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
            texto_final = texto_completo.strip()
            
            # Si no se extrajo suficiente texto, intentar método alternativo
            if texto_final and len(texto_final) > 50:
                return texto_final
            else:
                st.info("ℹ️ La API de LlamaIndex extrajo poco o ningún texto. Intentando método alternativo de OCR (pytesseract)...")
                # Resetear el archivo para el método alternativo
                from io import BytesIO
                pdf_file_obj = BytesIO(pdf_content) if isinstance(pdf_content, bytes) else pdf_content
                return extraer_texto_pdf_ocr_alternativo(pdf_file_obj)
            
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            st.warning(f"⚠️ Error con LlamaIndex: {str(e)}")
            st.info("ℹ️ Intentando método alternativo de OCR...")
            # Si falla con LlamaIndex, intentar método alternativo con pytesseract
            from io import BytesIO
            pdf_file_obj = BytesIO(pdf_content) if isinstance(pdf_content, bytes) else pdf_content
            return extraer_texto_pdf_ocr_alternativo(pdf_file_obj)
            
    except ImportError:
        st.warning("⚠️ LlamaParse no está disponible. Usando método alternativo de OCR...")
        st.info("💡 Instala: `pip install llama-index-readers-llama-parse`")
        from io import BytesIO
        pdf_file_obj = BytesIO(pdf_content) if isinstance(pdf_content, bytes) else pdf_content
        return extraer_texto_pdf_ocr_alternativo(pdf_file_obj)
    except Exception as e:
        error_msg = str(e)
        st.warning(f"⚠️ Error con la API de LlamaIndex: {error_msg}")
        
        # Mensajes de ayuda específicos
        if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            st.error("❌ Error de autenticación con la API de LlamaIndex")
            st.info("💡 Verifica que tu LLAMA_CLOUD_API_KEY sea válida y esté correctamente configurada")
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            st.warning("⚠️ Has alcanzado el límite de la API. Intentando método alternativo...")
        else:
            st.info("ℹ️ Intentando método alternativo de OCR...")
        
        from io import BytesIO
        pdf_file_obj = BytesIO(pdf_content) if isinstance(pdf_content, bytes) else pdf_content
        return extraer_texto_pdf_ocr_alternativo(pdf_file_obj)

def extraer_texto_pdf_ocr_alternativo(pdf_file) -> Optional[str]:
    """
    Método alternativo de OCR usando pytesseract y pdf2image.
    Útil cuando LlamaIndex no está disponible o falla.
    
    Args:
        pdf_file: Archivo PDF subido en Streamlit (puede ser BytesIO o file object)
        
    Returns:
        Texto extraído del PDF o None si hay error
    """
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
        from PIL import Image
        import os
        
        # Configurar TESSDATA_PREFIX si no está configurado
        if 'TESSDATA_PREFIX' not in os.environ:
            # Intentar ubicaciones comunes de tessdata
            posibles_rutas = [
                '/opt/homebrew/share/tessdata',
                '/usr/local/share/tessdata',
                '/usr/share/tessdata'
            ]
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    os.environ['TESSDATA_PREFIX'] = ruta
                    break
        
        # Leer el contenido del archivo
        if hasattr(pdf_file, 'read'):
            pdf_content = pdf_file.read()
            # Resetear posición si es posible
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
        else:
            pdf_content = pdf_file
        
        # Convertir PDF a imágenes
        with st.spinner("🖼️ Convirtiendo PDF a imágenes..."):
            try:
                images = convert_from_bytes(pdf_content)
            except Exception as e:
                st.error(f"❌ Error al convertir PDF a imágenes: {str(e)}")
                st.info("💡 Asegúrate de tener poppler instalado:\n- macOS: `brew install poppler`\n- Linux: `sudo apt-get install poppler-utils`")
                return None
        
        if not images:
            st.error("❌ No se pudieron extraer imágenes del PDF")
            return None
        
        texto_completo = ""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_pages = len(images)
        for i, image in enumerate(images):
            status_text.text(f"📄 Procesando página {i+1} de {total_pages} con OCR...")
            
            # Aplicar OCR a cada página
            try:
                # Intentar primero con español, si falla usar inglés
                try:
                    texto_pagina = pytesseract.image_to_string(image, lang='spa')  # español
                except Exception as lang_error:
                    # Si falla con español, intentar con inglés
                    if 'spa' in str(lang_error).lower() or 'language' in str(lang_error).lower():
                        st.info(f"ℹ️ Español no disponible en página {i+1}, usando inglés...")
                        texto_pagina = pytesseract.image_to_string(image, lang='eng')
                    else:
                        raise lang_error
                
                texto_completo += texto_pagina + "\n\n"
            except Exception as e:
                st.warning(f"⚠️ Error en página {i+1}: {str(e)}")
                # Continuar con las demás páginas
                continue
            
            # Actualizar progreso
            progress_bar.progress((i + 1) / total_pages)
        
        progress_bar.empty()
        status_text.empty()
        
        texto_final = texto_completo.strip()
        
        if texto_final and len(texto_final) > 50:
            st.success(f"✅ OCR completado: {len(texto_final)} caracteres extraídos de {total_pages} página(s)")
            return texto_final
        else:
            st.warning("⚠️ El OCR no pudo extraer suficiente texto. El PDF puede tener imágenes de baja calidad o estar corrupto.")
            return None
        
    except ImportError as e:
        st.error("❌ Librerías de OCR no están instaladas.")
        st.info("""
        💡 Para instalar las dependencias de OCR:
        - `pip install pytesseract pillow pdf2image`
        - También necesitas instalar Tesseract OCR:
          - macOS: `brew install tesseract tesseract-lang`
          - Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-spa`
          - Windows: Descargar desde https://github.com/UB-Mannheim/tesseract/wiki
        """)
        return None
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Error en OCR alternativo: {error_msg}")
        
        # Mensajes de ayuda específicos según el error
        if "tesseract" in error_msg.lower() or "TesseractNotFoundError" in error_msg:
            st.info("💡 Tesseract OCR no está instalado o no está en el PATH. Instálalo según tu sistema operativo.")
        elif "poppler" in error_msg.lower() or "convert_from_bytes" in error_msg:
            st.info("💡 Poppler no está instalado. Necesario para convertir PDF a imágenes:\n- macOS: `brew install poppler`\n- Linux: `sudo apt-get install poppler-utils`")
        
        return None

def procesar_expediente_texto(texto: str) -> str:
    """
    Procesa y limpia el texto del expediente.
    
    Args:
        texto: Texto crudo del expediente
        
    Returns:
        Texto procesado y limpio
    """
    # Limpiar espacios múltiples
    texto = " ".join(texto.split())
    
    # Limpiar saltos de línea excesivos
    lineas = texto.split('\n')
    lineas_limpias = []
    for linea in lineas:
        linea = linea.strip()
        if linea:
            lineas_limpias.append(linea)
    
    return "\n".join(lineas_limpias)

def render_cargar_expediente():
    """
    Renderiza la interfaz para cargar un expediente.
    
    Returns:
        Texto del expediente procesado o None
    """
    st.markdown("### 📄 Cargar Expediente")
    
    st.info("""
    **Formatos soportados:**
    - **PDF**: Archivos PDF con texto o escaneados (con OCR)
    - **TXT**: Archivos de texto plano
    
    **Tamaño máximo:** 10 MB
    
    **OCR disponible:** 
    - **API de LlamaCloud** (recomendado): Usa la API de LlamaIndex para OCR de alta calidad
      - Requiere `LLAMA_CLOUD_API_KEY` en el archivo `.env`
      - Regístrate en https://www.llamaindex.ai/
    - **Método alternativo**: Si no hay API key, usa pytesseract local
    """)
    
    # Opción 1: Subir archivo
    opcion = st.radio(
        "Selecciona el método de carga:",
        ["📁 Subir archivo (PDF/TXT)", "✍️ Pegar texto directamente"],
        horizontal=True
    )
    
    texto_expediente = None
    
    if opcion == "📁 Subir archivo (PDF/TXT)":
        uploaded_file = st.file_uploader(
            "Selecciona el archivo del expediente:",
            type=['pdf', 'txt'],
            help="Formatos soportados: PDF, TXT"
        )
        
        if uploaded_file is not None:
            # Mostrar información del archivo
            file_details = {
                "Nombre": uploaded_file.name,
                "Tipo": uploaded_file.type,
                "Tamaño": f"{uploaded_file.size / 1024 / 1024:.2f} MB"
            }
            
            col1, col2, col3 = st.columns(3)
            for idx, (key, value) in enumerate(file_details.items()):
                with [col1, col2, col3][idx]:
                    st.metric(key, value)
            
            # Procesar según el tipo de archivo
            if uploaded_file.type == "application/pdf":
                # Opción para usar OCR
                usar_ocr = st.checkbox(
                    "🔍 Usar OCR (para PDFs escaneados o con imágenes)",
                    value=False,
                    help="Activa esta opción si el PDF es una imagen escaneada o no se puede extraer texto normalmente"
                )
                
                if usar_ocr:
                    # Guardar el contenido del archivo en memoria para poder leerlo múltiples veces
                    pdf_content = uploaded_file.read()
                    uploaded_file.seek(0)
                    
                    # Crear un objeto similar a file desde el contenido
                    from io import BytesIO
                    pdf_file_obj = BytesIO(pdf_content)
                    
                    # Intentar extraer con OCR (intentará LlamaIndex primero, luego pytesseract si falla)
                    texto_expediente = extraer_texto_pdf_ocr(pdf_file_obj, usar_ocr=True)
                    
                    if texto_expediente and len(texto_expediente.strip()) > 50:
                        texto_expediente = procesar_expediente_texto(texto_expediente)
                        st.success(f"✅ Texto extraído con OCR: {len(texto_expediente)} caracteres, {len(texto_expediente.split())} palabras")
                    else:
                        st.error("❌ No se pudo extraer texto con OCR.")
                        st.info("""
                        💡 **Posibles soluciones:**
                        - Verifica que el PDF contenga imágenes legibles y de buena calidad
                        - Asegúrate de que las imágenes no estén rotadas o distorsionadas
                        - Intenta mejorar la calidad del escaneo del documento original
                        - Verifica que Tesseract OCR esté correctamente instalado
                        """)
                else:
                    with st.spinner("📄 Extrayendo texto del PDF..."):
                        # Guardar el contenido para poder reintentar con OCR si es necesario
                        pdf_content = uploaded_file.read()
                        uploaded_file.seek(0)
                        
                        from io import BytesIO
                        pdf_file_obj = BytesIO(pdf_content)
                        texto_expediente = extraer_texto_pdf(pdf_file_obj)
                        
                        if texto_expediente and len(texto_expediente.strip()) > 50:
                            texto_expediente = procesar_expediente_texto(texto_expediente)
                            st.success(f"✅ Texto extraído: {len(texto_expediente)} caracteres, {len(texto_expediente.split())} palabras")
                        else:
                            st.warning("⚠️ No se pudo extraer texto del PDF. Puede ser un PDF escaneado.")
                            st.info("💡 Activa la opción 'Usar OCR' arriba para procesar PDFs escaneados o con imágenes.")
                            
                            # Ofrecer usar OCR automáticamente
                            if st.button("🔍 Intentar con OCR automáticamente"):
                                pdf_file_obj = BytesIO(pdf_content)
                                with st.spinner("🔍 Extrayendo texto con OCR (esto puede tomar varios minutos)..."):
                                    texto_expediente = extraer_texto_pdf_ocr(pdf_file_obj, usar_ocr=True)
                                    if texto_expediente:
                                        texto_expediente = procesar_expediente_texto(texto_expediente)
                                        st.success(f"✅ Texto extraído con OCR: {len(texto_expediente)} caracteres, {len(texto_expediente.split())} palabras")
                                    else:
                                        st.error("❌ No se pudo extraer texto. Verifica que el PDF contenga imágenes legibles.")
            elif uploaded_file.type == "text/plain":
                texto_expediente = uploaded_file.read().decode('utf-8')
                texto_expediente = procesar_expediente_texto(texto_expediente)
                st.success(f"✅ Texto cargado: {len(texto_expediente)} caracteres")
    
    else:  # Pegar texto directamente
        texto_pegado = st.text_area(
            "Pega el texto del expediente aquí:",
            height=300,
            placeholder="Pega aquí el contenido del expediente..."
        )
        
        if texto_pegado.strip():
            texto_expediente = procesar_expediente_texto(texto_pegado)
            st.success(f"✅ Texto procesado: {len(texto_expediente)} caracteres")
    
    # Mostrar vista previa del texto
    if texto_expediente:
        with st.expander("👁️ Vista previa del expediente", expanded=False):
            st.text_area(
                "Contenido del expediente:",
                value=texto_expediente[:2000] + ("..." if len(texto_expediente) > 2000 else ""),
                height=200,
                disabled=True
            )
            st.caption(f"Total: {len(texto_expediente)} caracteres, {len(texto_expediente.split())} palabras")
    
    return texto_expediente

