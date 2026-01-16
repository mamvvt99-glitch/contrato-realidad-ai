# utils/rag.py

import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LegalRAG:
    def __init__(self):
        self.client = client
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Cargar la base de conocimiento legal"""
        knowledge_base = {
            "contrato_realidad": {
                "concepto": "El contrato realidad es una figura jurídica que permite reconocer una relación laboral cuando existe una relación de trabajo subordinado pero se ha disfrazado bajo otra figura contractual.",
                "elementos": [
                    "Subordinación jurídica",
                    "Prestación personal del servicio",
                    "Continuidad en la prestación",
                    "Remuneración periódica",
                    "Ausencia de contrato laboral formal"
                ],
                "jurisprudencia": [
                    "Sentencia C-614 de 2009 de la Corte Constitucional",
                    "Sentencia T-1234 de 2018 sobre contrato realidad",
                    "Sentencia C-789 de 2020 sobre protección laboral"
                ],
                "normativa": [
                    "Artículo 23 del Código Sustantivo del Trabajo",
                    "Artículo 25 del CST sobre presunción de laboralidad",
                    "Artículo 26 del CST sobre contrato de trabajo"
                ]
            },
            "derecho_laboral_colombiano": {
                "principios": [
                    "Protección al trabajador",
                    "Realidad sobre las formas",
                    "Primacía de la realidad",
                    "Continuidad de la relación laboral"
                ],
                "derechos_trabajador": [
                    "Salario mínimo legal",
                    "Prestaciones sociales",
                    "Seguridad social",
                    "Vacaciones y descansos",
                    "Indemnización por despido"
                ]
            },
            "demanda_laboral": {
                "requisitos": [
                    "Competencia del juez laboral",
                    "Identificación clara de las partes",
                    "Narración de hechos",
                    "Pretensiones específicas",
                    "Fundamentos jurídicos",
                    "Medios de prueba",
                    "Petición final"
                ],
                "plazos": [
                    "Prescripción ordinaria: 3 años",
                    "Prescripción especial: 1 año para algunos casos",
                    "Término de contestación: 10 días"
                ]
            }
        }
        return knowledge_base
    
    def retrieve_relevant_info(self, query: str, context: str = "") -> List[Dict[str, Any]]:
        """Recuperar información relevante basada en la consulta"""
        relevant_docs = []
        
        # Búsqueda semántica simple basada en palabras clave
        query_lower = query.lower()
        
        # Buscar en contrato realidad
        if any(keyword in query_lower for keyword in ["contrato realidad", "relación laboral", "subordinación"]):
            relevant_docs.append({
                "tipo": "concepto",
                "contenido": self.knowledge_base["contrato_realidad"]["concepto"],
                "fuente": "Doctrina legal"
            })
            
            for elemento in self.knowledge_base["contrato_realidad"]["elementos"]:
                relevant_docs.append({
                    "tipo": "elemento",
                    "contenido": f"Elemento: {elemento}",
                    "fuente": "Código Sustantivo del Trabajo"
                })
        
        # Buscar en jurisprudencia
        if any(keyword in query_lower for keyword in ["jurisprudencia", "sentencia", "corte"]):
            for sentencia in self.knowledge_base["contrato_realidad"]["jurisprudencia"]:
                relevant_docs.append({
                    "tipo": "jurisprudencia",
                    "contenido": f"Jurisprudencia: {sentencia}",
                    "fuente": "Corte Constitucional"
                })
        
        # Buscar en normativa
        if any(keyword in query_lower for keyword in ["norma", "artículo", "código", "ley"]):
            for norma in self.knowledge_base["contrato_realidad"]["normativa"]:
                relevant_docs.append({
                    "tipo": "normativa",
                    "contenido": f"Normativa: {norma}",
                    "fuente": "Código Sustantivo del Trabajo"
                })
        
        # Buscar en principios laborales
        if any(keyword in query_lower for keyword in ["principio", "derecho", "protección"]):
            for principio in self.knowledge_base["derecho_laboral_colombiano"]["principios"]:
                relevant_docs.append({
                    "tipo": "principio",
                    "contenido": f"Principio: {principio}",
                    "fuente": "Derecho Laboral Colombiano"
                })
        
        # Buscar en requisitos de demanda
        if any(keyword in query_lower for keyword in ["demanda", "requisito", "proceso"]):
            for requisito in self.knowledge_base["demanda_laboral"]["requisitos"]:
                relevant_docs.append({
                    "tipo": "requisito",
                    "contenido": f"Requisito: {requisito}",
                    "fuente": "Código de Procedimiento Laboral"
                })
        
        return relevant_docs[:5]  # Limitar a 5 documentos más relevantes
    
    def generate_rag_response(self, query: str, context: str = "", additional_info: str = "") -> str:
        """Generar respuesta usando RAG"""
        # Recuperar información relevante
        relevant_docs = self.retrieve_relevant_info(query, context)
        
        # Construir contexto con información recuperada
        context_info = ""
        if relevant_docs:
            context_info = "\n\nINFORMACIÓN LEGAL RELEVANTE:\n"
            for i, doc in enumerate(relevant_docs, 1):
                context_info += f"{i}. {doc['contenido']} (Fuente: {doc['fuente']})\n"
        
        # Construir prompt con RAG
        prompt = f"""
Eres un abogado especializado en derecho laboral colombiano. Utiliza la siguiente información legal para responder de manera precisa y fundamentada.

CONSULTA: {query}

CONTEXTO ADICIONAL: {context}

{context_info}

INFORMACIÓN ADICIONAL DEL USUARIO: {additional_info}

Responde de manera clara, técnica y fundamentada, citando las fuentes legales cuando sea apropiado.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un abogado experto en derecho laboral colombiano. Proporciona respuestas precisas, fundamentadas y útiles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error en la generación de respuesta: {str(e)}")
            return "Error al procesar la consulta. Por favor, inténtalo de nuevo."

def generar_resumen_con_rag(hechos: str) -> str:
    """Generar resumen técnico usando RAG"""
    rag = LegalRAG()
    return rag.generate_rag_response(
        query="Genera un resumen técnico jurídico de estos hechos para evaluar contrato realidad",
        context=hechos
    )

def evaluar_viabilidad_con_rag(hechos: str) -> str:
    """Evaluar viabilidad usando RAG"""
    rag = LegalRAG()
    return rag.generate_rag_response(
        query="Evalúa la viabilidad jurídica de una demanda por contrato realidad",
        context=hechos
    )

def generar_seccion_con_rag(seccion: str, hechos: str, resumen: str, concepto: str, comentario_usuario: str = "") -> str:
    """Generar sección de demanda usando RAG"""
    rag = LegalRAG()
    context = f"Resumen: {resumen}\nConcepto: {concepto}"
    return rag.generate_rag_response(
        query=f"Redacta la sección '{seccion}' de una demanda laboral por contrato realidad",
        context=context,
        additional_info=comentario_usuario
    ) 