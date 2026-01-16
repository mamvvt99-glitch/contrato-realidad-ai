# utils/por_secciones.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_seccion(seccion: str, hechos: str, resumen: str, concepto: str, comentario_usuario: str = ""):
    prompt = f"""
Eres un abogado litigante colombiano experto en derecho laboral. Redacta SOLO la sección "{seccion}" de una demanda laboral por contrato realidad.

HECHOS DEL CASO:
{hechos}

RESUMEN TÉCNICO:
{resumen}

CONCEPTO DE VIABILIDAD:
{concepto}

{f"COMENTARIOS ADICIONALES DEL USUARIO:\n{comentario_usuario}" if comentario_usuario else ""}

Redacta la sección {seccion} de forma clara, estructurada y jurídica, lista para usarse en la demanda.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Actúas como abogado litigante experto en demandas laborales por contrato realidad."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=5000
    )

    return response.choices[0].message.content.strip()