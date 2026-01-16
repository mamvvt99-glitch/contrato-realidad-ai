# utils/documento_referencia.py

import streamlit as st
import os
import tempfile
from typing import Dict, Optional
from utils.expediente import extraer_texto_pdf, extraer_texto_pdf_ocr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Estructura de secciones estándar
SECCIONES_ESTANDAR = {
    "I. Hechos": {
        "descripcion": "Narración detallada y cronológica de los hechos que dan origen a la demanda",
        "contenido_tipico": "Debe incluir: fechas, lugares, personas involucradas, acciones realizadas, documentos relevantes"
    },
    "II. Peticiones": {
        "descripcion": "Solicitudes específicas que se hacen al juez",
        "contenido_tipico": "Debe incluir: peticiones principales y subsidiarias, de forma clara y numerada"
    },
    "III. Petición Final": {
        "descripcion": "Resumen final de lo que se solicita al tribunal",
        "contenido_tipico": "Debe incluir: síntesis de todas las peticiones, forma de notificación"
    },
    "IV. Fundamentos de derecho": {
        "descripcion": "Bases legales que sustentan las peticiones",
        "contenido_tipico": "Debe incluir: artículos de ley, principios jurídicos aplicables, argumentación legal"
    },
    "V. Normatividad y jurisprudencia aplicable al caso": {
        "descripcion": "Leyes, decretos, sentencias y jurisprudencia relevante",
        "contenido_tipico": "Debe incluir: citas específicas de normas, sentencias de cortes, precedentes"
    },
    "VI. Relación de medios probatorios": {
        "descripcion": "Lista de pruebas que se aportan al proceso",
        "contenido_tipico": "Debe incluir: documentos, testigos, peritos, inspecciones, etc."
    },
    "VII. Cuantía": {
        "descripcion": "Valor económico de las pretensiones",
        "contenido_tipico": "Debe incluir: cálculo detallado de montos, conceptos, intereses"
    },
    "VIII. Propuesta de fórmula de conciliación": {
        "descripcion": "Propuesta para resolver el conflicto mediante conciliación",
        "contenido_tipico": "Debe incluir: términos de la propuesta, condiciones, plazos"
    },
    "IX. Competencia": {
        "descripcion": "Justificación de la competencia del juez o tribunal",
        "contenido_tipico": "Debe incluir: fundamento legal de la competencia, territorio, materia"
    },
    "X. Manifestación": {
        "descripcion": "Declaraciones adicionales del demandante",
        "contenido_tipico": "Debe incluir: reservas, aclaraciones, manifestaciones especiales"
    },
    "XI. Anexos": {
        "descripcion": "Lista de documentos que acompañan la demanda",
        "contenido_tipico": "Debe incluir: numeración y descripción de cada anexo"
    },
    "XII. Notificaciones": {
        "descripcion": "Datos para notificaciones procesales",
        "contenido_tipico": "Debe incluir: dirección, correo electrónico, teléfono, forma de notificación preferida"
    }
}

def extraer_patrones_documento(texto_documento: str) -> Dict[str, str]:
    """
    Extrae patrones de redacción de cada sección del documento de referencia usando IA.
    
    Args:
        texto_documento: Texto completo del documento de referencia
        
    Returns:
        Diccionario con patrones de redacción por sección
    """
    prompt = f"""
Eres un experto en análisis de documentos legales. Analiza el siguiente documento de referencia de una demanda laboral y extrae para cada una de las siguientes secciones:

1. I. Hechos
2. II. Peticiones
3. III. Petición Final
4. IV. Fundamentos de derecho
5. V. Normatividad y jurisprudencia aplicable al caso
6. VI. Relación de medios probatorios
7. VII. Cuantía
8. VIII. Propuesta de fórmula de conciliación
9. IX. Competencia
10. X. Manifestación
11. XI. Anexos
12. XII. Notificaciones

DOCUMENTO DE REFERENCIA:
{texto_documento[:15000]}  # Limitar tamaño para el prompt

Para cada sección, identifica:
- La estructura y formato de redacción
- El estilo y tono utilizado
- Los elementos que típicamente incluye
- Frases o fórmulas legales recurrentes
- La extensión aproximada

Responde en formato JSON con la siguiente estructura:
{{
    "I. Hechos": {{
        "estructura": "descripción de cómo está estructurada",
        "estilo": "descripción del estilo de redacción",
        "elementos": ["elemento1", "elemento2", ...],
        "formulas_legales": ["fórmula1", "fórmula2", ...],
        "ejemplo_extracto": "extracto del documento de ejemplo"
    }},
    ...
}}

Solo incluye las secciones que encuentres en el documento.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de documentos legales colombianos. Extraes patrones de redacción de manera precisa y estructurada."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000
        )
        
        import json
        # Intentar parsear el JSON de la respuesta
        contenido = response.choices[0].message.content.strip()
        
        # Limpiar el contenido si tiene markdown
        if contenido.startswith("```json"):
            contenido = contenido[7:]
        if contenido.startswith("```"):
            contenido = contenido[3:]
        if contenido.endswith("```"):
            contenido = contenido[:-3]
        contenido = contenido.strip()
        
        patrones = json.loads(contenido)
        return patrones
        
    except Exception as e:
        st.error(f"Error al extraer patrones: {str(e)}")
        return {}

def cargar_patrones_desde_json(ruta_archivo: str) -> Dict[str, Dict]:
    """
    Carga patrones desde un archivo JSON generado por el script extraer_patrones.py
    
    Args:
        ruta_archivo: Ruta al archivo JSON con los patrones
        
    Returns:
        Diccionario con los patrones cargados
    """
    import json
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            patrones = json.load(f)
        return patrones
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo: {ruta_archivo}")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"❌ Error al leer el archivo JSON: {str(e)}")
        return {}

def cargar_documento_referencia() -> Optional[str]:
    """
    Interfaz para cargar un documento de referencia.
    
    Returns:
        Texto del documento o None
    """
    st.markdown("### 📋 Cargar Documento de Referencia")
    
    st.info("""
    **¿Qué es un documento de referencia?**
    
    Es un documento de demanda laboral existente que sirve como modelo para la redacción.
    El sistema analizará este documento para extraer:
    - Estructura y formato de cada sección
    - Estilo de redacción
    - Elementos típicos incluidos
    - Fórmulas legales utilizadas
    
    **Formatos soportados:** PDF, TXT
    """)
    
    uploaded_file = st.file_uploader(
        "Selecciona el documento de referencia:",
        type=['pdf', 'txt'],
        help="Sube un documento de demanda laboral como referencia"
    )
    
    texto_documento = None
    
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
            # Intentar extracción normal primero
            uploaded_file.seek(0)
            texto_documento = extraer_texto_pdf(uploaded_file)
            
            # Si no hay suficiente texto, ofrecer OCR
            if not texto_documento or len(texto_documento.strip()) < 100:
                st.warning("⚠️ No se pudo extraer suficiente texto. ¿Es un PDF escaneado?")
                if st.button("🔍 Intentar con OCR"):
                    uploaded_file.seek(0)
                    texto_documento = extraer_texto_pdf_ocr(uploaded_file, usar_ocr=True)
        elif uploaded_file.type == "text/plain":
            texto_documento = uploaded_file.read().decode('utf-8')
        
        if texto_documento and len(texto_documento.strip()) > 100:
            st.success(f"✅ Documento cargado: {len(texto_documento)} caracteres")
            
            with st.expander("👁️ Vista previa del documento", expanded=False):
                st.text_area(
                    "Contenido:",
                    value=texto_documento[:2000] + ("..." if len(texto_documento) > 2000 else ""),
                    height=200,
                    disabled=True
                )
        else:
            st.error("❌ No se pudo extraer texto del documento")
    
    return texto_documento

def generar_seccion_con_referencia(
    seccion: str, 
    hechos: str, 
    resumen: str, 
    concepto: str, 
    patrones_referencia: Dict[str, Dict] = None,
    comentario_usuario: str = ""
) -> str:
    """
    Genera una sección usando patrones extraídos del documento de referencia.
    
    Args:
        seccion: Nombre de la sección a generar
        hechos: Hechos del caso
        resumen: Resumen técnico
        concepto: Concepto de viabilidad
        patrones_referencia: Patrones extraídos del documento de referencia
        comentario_usuario: Comentarios adicionales del usuario
        
    Returns:
        Texto generado para la sección
    """
    # Obtener información de la sección estándar
    info_seccion = SECCIONES_ESTANDAR.get(seccion, {})
    
    # Construir contexto de referencia si está disponible
    contexto_referencia = ""
    if patrones_referencia and seccion in patrones_referencia:
        patron = patrones_referencia[seccion]
        contexto_referencia = f"""
PATRÓN DE REFERENCIA PARA ESTA SECCIÓN:
- Estructura: {patron.get('estructura', 'No especificada')}
- Estilo: {patron.get('estilo', 'No especificado')}
- Elementos típicos: {', '.join(patron.get('elementos', []))}
- Fórmulas legales: {', '.join(patron.get('formulas_legales', []))}
- Ejemplo: {patron.get('ejemplo_extracto', 'No disponible')}
"""
    elif info_seccion:
        contexto_referencia = f"""
GUÍA PARA ESTA SECCIÓN:
- Descripción: {info_seccion.get('descripcion', '')}
- Contenido típico: {info_seccion.get('contenido_tipico', '')}
"""
    
    prompt = f"""
Eres un abogado litigante colombiano experto en derecho laboral. Redacta SOLO la sección "{seccion}" de una demanda laboral por contrato realidad.

HECHOS DEL CASO:
{hechos}

RESUMEN TÉCNICO:
{resumen}

CONCEPTO DE VIABILIDAD:
{concepto}

{contexto_referencia}

{f"COMENTARIOS ADICIONALES DEL USUARIO:\n{comentario_usuario}" if comentario_usuario else ""}

INSTRUCCIONES:
- Sigue la estructura y estilo del patrón de referencia si está disponible
- Usa las fórmulas legales apropiadas
- Incluye todos los elementos típicos de esta sección
- Mantén un tono profesional y jurídico
- Redacta de forma clara, estructurada y lista para usarse en la demanda
- Si no hay patrón de referencia, usa las mejores prácticas legales colombianas
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Actúas como abogado litigante experto en demandas laborales por contrato realidad. Redactas secciones siguiendo patrones de referencia cuando están disponibles."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=5000
    )

    return response.choices[0].message.content.strip()

