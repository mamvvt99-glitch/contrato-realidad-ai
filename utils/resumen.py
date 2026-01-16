# utils/resumen.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_resumen(hechos: str):
    prompt = f"""
Eres un abogado especializado en derecho laboral colombiano. A partir de los siguientes hechos narrados por un trabajador, redacta un resumen jurídico claro, técnico y estructurado, útil para evaluar la viabilidad de una demanda por contrato realidad.

HECHOS:
{hechos}

Resumen técnico (evita repetir hechos, prioriza elementos como subordinación, prestación personal del servicio, continuidad y ausencia de vínculo formal):
"""

    response = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {"role": "system", "content": "Actúas como un abogado litigante experto en derecho laboral colombiano."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()