#!/usr/bin/env python3
"""
Script para extraer patrones de redacción de un documento de referencia de demanda laboral.

Uso:
    python extraer_patrones.py <archivo_referencia.pdf> [--output patrones.json]
"""

import sys
import json
import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from utils.expediente import extraer_texto_pdf, extraer_texto_pdf_ocr
import io

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extraer_texto_documento(ruta_archivo: str, usar_ocr: bool = False) -> str:
    """
    Extrae texto de un archivo PDF o TXT.
    
    Args:
        ruta_archivo: Ruta al archivo
        usar_ocr: Si True, usa OCR para PDFs escaneados
        
    Returns:
        Texto extraído
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo {ruta_archivo} no existe")
    
    extension = os.path.splitext(ruta_archivo)[1].lower()
    
    if extension == '.pdf':
        with open(ruta_archivo, 'rb') as f:
            contenido = f.read()
            pdf_file = io.BytesIO(contenido)
            
            if usar_ocr:
                print("🔍 Extrayendo texto con OCR...")
                texto = extraer_texto_pdf_ocr(pdf_file, usar_ocr=True)
            else:
                print("📄 Extrayendo texto del PDF...")
                pdf_file.seek(0)
                texto = extraer_texto_pdf(pdf_file)
                
            if not texto or len(texto.strip()) < 100:
                print("⚠️ No se pudo extraer suficiente texto. Intentando con OCR...")
                pdf_file.seek(0)
                texto = extraer_texto_pdf_ocr(pdf_file, usar_ocr=True)
                
        return texto
    elif extension == '.txt':
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError(f"Formato no soportado: {extension}. Use PDF o TXT")

def extraer_patrones_documento(texto_documento: str) -> dict:
    """
    Extrae patrones de redacción de cada sección del documento de referencia usando IA.
    
    Args:
        texto_documento: Texto completo del documento de referencia
        
    Returns:
        Diccionario con patrones de redacción por sección
    """
    print("🤖 Analizando documento con IA...")
    
    # Limitar tamaño del texto para el prompt
    texto_limite = texto_documento[:20000] if len(texto_documento) > 20000 else texto_documento
    
    prompt = f"""
Eres un experto en análisis de documentos legales colombianos. Analiza el siguiente documento de referencia de una demanda laboral y extrae para cada una de las siguientes secciones:

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
{texto_limite}

Para cada sección que encuentres en el documento, identifica y extrae:
- La estructura y formato de redacción (cómo está organizada)
- El estilo y tono utilizado (formal, técnico, etc.)
- Los elementos que típicamente incluye (qué información contiene)
- Frases o fórmulas legales recurrentes (expresiones comunes)
- Un extracto representativo del documento (ejemplo real de la sección)

Responde ÚNICAMENTE en formato JSON válido con la siguiente estructura:
{{
    "I. Hechos": {{
        "estructura": "descripción detallada de cómo está estructurada esta sección",
        "estilo": "descripción del estilo de redacción utilizado",
        "elementos": ["elemento1 que incluye", "elemento2 que incluye", "elemento3"],
        "formulas_legales": ["fórmula legal 1", "fórmula legal 2", "fórmula legal 3"],
        "ejemplo_extracto": "extracto real del documento que muestra cómo está redactada"
    }},
    "II. Peticiones": {{
        ...
    }},
    ...
}}

IMPORTANTE:
- Solo incluye las secciones que realmente encuentres en el documento
- Si una sección no está en el documento, no la incluyas en el JSON
- Los extractos deben ser reales del documento, no inventados
- El JSON debe ser válido y parseable
- Responde solo con el JSON, sin texto adicional antes o después
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un experto en análisis de documentos legales colombianos. Extraes patrones de redacción de manera precisa y estructurada. Siempre respondes en formato JSON válido."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=6000
        )
        
        contenido = response.choices[0].message.content.strip()
        
        # Limpiar el contenido si tiene markdown
        if contenido.startswith("```json"):
            contenido = contenido[7:]
        elif contenido.startswith("```"):
            contenido = contenido[3:]
        if contenido.endswith("```"):
            contenido = contenido[:-3]
        contenido = contenido.strip()
        
        # Parsear JSON
        patrones = json.loads(contenido)
        
        print(f"✅ Patrones extraídos de {len(patrones)} secciones")
        return patrones
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {str(e)}")
        print("Respuesta recibida:")
        print(contenido[:500])
        return {}
    except Exception as e:
        print(f"❌ Error al extraer patrones: {str(e)}")
        return {}

def main():
    parser = argparse.ArgumentParser(
        description='Extrae patrones de redacción de un documento de referencia de demanda laboral'
    )
    parser.add_argument(
        'archivo',
        help='Ruta al archivo de referencia (PDF o TXT)'
    )
    parser.add_argument(
        '--output', '-o',
        default='patrones_referencia.json',
        help='Archivo de salida para los patrones (default: patrones_referencia.json)'
    )
    parser.add_argument(
        '--ocr',
        action='store_true',
        help='Usar OCR para extraer texto de PDFs escaneados'
    )
    
    args = parser.parse_args()
    
    print(f"📄 Procesando archivo: {args.archivo}")
    print(f"💾 Archivo de salida: {args.output}")
    print("-" * 60)
    
    try:
        # Extraer texto del documento
        texto = extraer_texto_documento(args.archivo, usar_ocr=args.ocr)
        
        if not texto or len(texto.strip()) < 100:
            print("❌ Error: No se pudo extraer suficiente texto del documento")
            sys.exit(1)
        
        print(f"✅ Texto extraído: {len(texto)} caracteres")
        print("-" * 60)
        
        # Extraer patrones
        patrones = extraer_patrones_documento(texto)
        
        if not patrones:
            print("❌ Error: No se pudieron extraer patrones del documento")
            sys.exit(1)
        
        # Guardar patrones en archivo JSON
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(patrones, f, ensure_ascii=False, indent=2)
        
        print("-" * 60)
        print(f"✅ Patrones guardados en: {args.output}")
        print(f"📊 Secciones encontradas: {', '.join(patrones.keys())}")
        print("\n💡 Ahora puedes usar este archivo en la aplicación Streamlit")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

