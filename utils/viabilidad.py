# utils/viabilidad.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluar_viabilidad(hechos: str):
    prompt = f"""
Eres un abogado especializado en derecho laboral colombiano.

A continuación se presentan los hechos de un trabajador que considera haber tenido una relación laboral encubierta bajo un contrato de prestación de servicios u otra figura no laboral. Evalúa si existe una **relación laboral real (contrato realidad)** y emite un concepto técnico, claro y fundamentado sobre la **viabilidad jurídica** de presentar una demanda.

HECHOS DEL CASO:
{hechos}

Evalúa:

- Si hubo subordinación (órdenes, control, supervisión directa).
- Si prestó el servicio de forma personal y continua.
- Si recibió remuneración periódica.
- Si hubo ausencia de contrato laboral escrito o uso de figuras contractuales simuladas.
- Aplica doctrina y jurisprudencia laboral colombiana reciente.

Concluye si hay **viabilidad alta, media o baja** para presentar demanda, con argumentos técnicos.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Eres un abogado litigante con experiencia en demandas laborales por contrato realidad. Redactas conceptos técnicos, argumentativos y estructurados."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1200
    )

    return response.choices[0].message.content.strip()