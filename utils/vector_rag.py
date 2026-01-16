# utils/vector_rag.py

import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
import hashlib

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class VectorLegalRAG:
    def __init__(self):
        self.client = client
        self.documents = self._load_legal_documents()
        self.embeddings_cache = {}
        
    def _load_legal_documents(self) -> List[Dict[str, Any]]:
        """Cargar documentos legales con embeddings"""
        documents = [
            {
                "id": "contrato_realidad_concepto",
                "content": "El contrato realidad es una figura jurídica que permite reconocer una relación laboral cuando existe una relación de trabajo subordinado pero se ha disfrazado bajo otra figura contractual como prestación de servicios, contrato civil o comercial.",
                "metadata": {
                    "tipo": "concepto",
                    "fuente": "Doctrina legal",
                    "categoria": "contrato_realidad"
                }
            },
            {
                "id": "subordinacion_juridica",
                "content": "La subordinación jurídica es el elemento esencial del contrato de trabajo. Se manifiesta cuando el trabajador está sometido a las órdenes, dirección y control del empleador en la prestación del servicio.",
                "metadata": {
                    "tipo": "elemento",
                    "fuente": "Código Sustantivo del Trabajo Art. 23",
                    "categoria": "contrato_realidad"
                }
            },
            {
                "id": "prestacion_personal",
                "content": "La prestación personal del servicio significa que el trabajador debe realizar personalmente la labor contratada, sin poder delegarla a terceros, salvo autorización expresa del empleador.",
                "metadata": {
                    "tipo": "elemento",
                    "fuente": "Código Sustantivo del Trabajo",
                    "categoria": "contrato_realidad"
                }
            },
            {
                "id": "continuidad_servicio",
                "content": "La continuidad en la prestación del servicio implica que la relación laboral se mantiene de manera estable y permanente, no ocasional o esporádica.",
                "metadata": {
                    "tipo": "elemento",
                    "fuente": "Jurisprudencia Corte Constitucional",
                    "categoria": "contrato_realidad"
                }
            },
            {
                "id": "remuneracion_periodica",
                "content": "La remuneración periódica es el pago regular que recibe el trabajador por su labor, que puede ser salario, comisiones, bonificaciones u otras formas de retribución.",
                "metadata": {
                    "tipo": "elemento",
                    "fuente": "Código Sustantivo del Trabajo",
                    "categoria": "contrato_realidad"
                }
            },
            {
                "id": "sentencia_c614_2009",
                "content": "La Sentencia C-614 de 2009 de la Corte Constitucional establece que el contrato realidad busca proteger al trabajador cuando se simula una relación contractual diferente a la laboral para evadir las obligaciones legales.",
                "metadata": {
                    "tipo": "jurisprudencia",
                    "fuente": "Corte Constitucional",
                    "categoria": "contrato_realidad"
                }
            },
            {
                "id": "articulo_23_cst",
                "content": "Artículo 23 del Código Sustantivo del Trabajo: 'Contrato de trabajo es aquel por el cual una persona natural se obliga a prestar un servicio personal a otra persona natural o jurídica, bajo la continuada dependencia o subordinación de la segunda y mediante remuneración.'",
                "metadata": {
                    "tipo": "normativa",
                    "fuente": "Código Sustantivo del Trabajo",
                    "categoria": "normativa_laboral"
                }
            },
            {
                "id": "articulo_25_cst",
                "content": "Artículo 25 del CST: 'Se presume que toda relación de trabajo personal está regida por un contrato de trabajo.'",
                "metadata": {
                    "tipo": "normativa",
                    "fuente": "Código Sustantivo del Trabajo",
                    "categoria": "normativa_laboral"
                }
            },
            {
                "id": "principio_proteccion",
                "content": "El principio de protección al trabajador establece que en caso de duda sobre la naturaleza de la relación contractual, debe interpretarse a favor del trabajador.",
                "metadata": {
                    "tipo": "principio",
                    "fuente": "Derecho Laboral Colombiano",
                    "categoria": "principios_laborales"
                }
            },
            {
                "id": "principio_realidad",
                "content": "El principio de realidad sobre las formas establece que la verdadera naturaleza de la relación laboral debe determinarse por los hechos reales y no por la denominación que las partes le hayan dado.",
                "metadata": {
                    "tipo": "principio",
                    "fuente": "Derecho Laboral Colombiano",
                    "categoria": "principios_laborales"
                }
            },
            {
                "id": "requisitos_demanda",
                "content": "Los requisitos de una demanda laboral incluyen: competencia del juez laboral, identificación clara de las partes, narración de hechos, pretensiones específicas, fundamentos jurídicos, medios de prueba y petición final.",
                "metadata": {
                    "tipo": "proceso",
                    "fuente": "Código de Procedimiento Laboral",
                    "categoria": "proceso_laboral"
                }
            },
            {
                "id": "prescripcion_laboral",
                "content": "La prescripción ordinaria en materia laboral es de 3 años, contados desde el día siguiente a la terminación del contrato de trabajo.",
                "metadata": {
                    "tipo": "plazo",
                    "fuente": "Código de Procedimiento Laboral",
                    "categoria": "proceso_laboral"
                }
            }
        ]
        return documents
    
    def get_embedding(self, text: str) -> List[float]:
        """Obtener embedding de un texto usando OpenAI"""
        # Crear hash del texto para cache
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Verificar cache
        if text_hash in self.embeddings_cache:
            return self.embeddings_cache[text_hash]
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
            self.embeddings_cache[text_hash] = embedding
            return embedding
        except Exception as e:
            st.error(f"Error obteniendo embedding: {str(e)}")
            return []
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Búsqueda semántica usando embeddings"""
        query_embedding = self.get_embedding(query)
        
        if not query_embedding:
            return []
        
        similarities = []
        for doc in self.documents:
            doc_embedding = self.get_embedding(doc["content"])
            if doc_embedding:
                similarity = cosine_similarity(
                    [query_embedding], 
                    [doc_embedding]
                )[0][0]
                similarities.append((doc, similarity))
        
        # Ordenar por similitud y retornar top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def retrieve_relevant_documents(self, query: str, context: str = "") -> List[Dict[str, Any]]:
        """Recuperar documentos relevantes usando búsqueda semántica"""
        # Combinar query con contexto para mejor búsqueda
        search_query = f"{query} {context}".strip()
        
        # Realizar búsqueda semántica
        search_results = self.semantic_search(search_query, top_k=5)
        
        relevant_docs = []
        for doc, similarity in search_results:
            if similarity > 0.3:  # Umbral de similitud
                relevant_docs.append({
                    "contenido": doc["content"],
                    "metadata": doc["metadata"],
                    "similarity": similarity
                })
        
        return relevant_docs
    
    def generate_rag_response(self, query: str, context: str = "", additional_info: str = "") -> str:
        """Generar respuesta usando RAG con embeddings"""
        # Recuperar documentos relevantes
        relevant_docs = self.retrieve_relevant_documents(query, context)
        
        # Construir contexto con información recuperada
        context_info = ""
        if relevant_docs:
            context_info = "\n\nINFORMACIÓN LEGAL RELEVANTE:\n"
            for i, doc in enumerate(relevant_docs, 1):
                context_info += f"{i}. {doc['contenido']} (Fuente: {doc['metadata']['fuente']})\n"
        
        # Construir prompt con RAG
        prompt = f"""
Eres un abogado especializado en derecho laboral colombiano. Utiliza la siguiente información legal para responder de manera precisa y fundamentada.

CONSULTA: {query}

CONTEXTO ADICIONAL: {context}

{context_info}

INFORMACIÓN ADICIONAL DEL USUARIO: {additional_info}

Responde de manera clara, técnica y fundamentada, citando las fuentes legales cuando sea apropiado. Incluye referencias específicas a la normativa y jurisprudencia relevante.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un abogado experto en derecho laboral colombiano. Proporciona respuestas precisas, fundamentadas y útiles, citando fuentes legales específicas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error en la generación de respuesta: {str(e)}")
            return "Error al procesar la consulta. Por favor, inténtalo de nuevo."

def generar_resumen_vector_rag(hechos: str) -> str:
    """Generar resumen técnico usando RAG vectorial"""
    rag = VectorLegalRAG()
    return rag.generate_rag_response(
        query="Genera un resumen técnico jurídico de estos hechos para evaluar contrato realidad",
        context=hechos
    )

def evaluar_viabilidad_vector_rag(hechos: str) -> str:
    """Evaluar viabilidad usando RAG vectorial"""
    rag = VectorLegalRAG()
    return rag.generate_rag_response(
        query="Evalúa la viabilidad jurídica de una demanda por contrato realidad, considerando los elementos del contrato de trabajo y la jurisprudencia aplicable",
        context=hechos
    )

def generar_seccion_vector_rag(seccion: str, hechos: str, resumen: str, concepto: str, comentario_usuario: str = "") -> str:
    """Generar sección de demanda usando RAG vectorial"""
    rag = VectorLegalRAG()
    context = f"Resumen: {resumen}\nConcepto: {concepto}"
    return rag.generate_rag_response(
        query=f"Redacta la sección '{seccion}' de una demanda laboral por contrato realidad, incluyendo fundamentos jurídicos y referencias legales",
        context=context,
        additional_info=comentario_usuario
    ) 