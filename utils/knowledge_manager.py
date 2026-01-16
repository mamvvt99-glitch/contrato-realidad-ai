# utils/knowledge_manager.py

import json
import os
from typing import List, Dict, Any
from datetime import datetime
import streamlit as st

class LegalKnowledgeManager:
    def __init__(self, knowledge_file: str = "legal_knowledge.json"):
        self.knowledge_file = knowledge_file
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Cargar base de conocimiento desde archivo JSON"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error cargando base de conocimiento: {str(e)}")
                return self._get_default_knowledge()
        else:
            return self._get_default_knowledge()
    
    def _get_default_knowledge(self) -> Dict[str, Any]:
        """Obtener base de conocimiento por defecto"""
        return {
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
    
    def save_knowledge_base(self):
        """Guardar base de conocimiento en archivo JSON"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Error guardando base de conocimiento: {str(e)}")
            return False
    
    def add_legal_document(self, category: str, doc_type: str, content: str, source: str = ""):
        """Agregar nuevo documento legal a la base de conocimiento"""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        
        if doc_type not in self.knowledge_base[category]:
            self.knowledge_base[category][doc_type] = []
        
        new_doc = {
            "content": content,
            "source": source,
            "added_date": datetime.now().isoformat()
        }
        
        self.knowledge_base[category][doc_type].append(new_doc)
        return self.save_knowledge_base()
    
    def get_knowledge_categories(self) -> List[str]:
        """Obtener categorías disponibles"""
        return list(self.knowledge_base.keys())
    
    def get_document_types(self, category: str) -> List[str]:
        """Obtener tipos de documentos en una categoría"""
        if category in self.knowledge_base:
            return list(self.knowledge_base[category].keys())
        return []
    
    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Buscar en la base de conocimiento"""
        results = []
        query_lower = query.lower()
        
        for category, content in self.knowledge_base.items():
            for doc_type, documents in content.items():
                if isinstance(documents, list):
                    for doc in documents:
                        if isinstance(doc, dict) and "content" in doc:
                            if query_lower in doc["content"].lower():
                                results.append({
                                    "category": category,
                                    "type": doc_type,
                                    "content": doc["content"],
                                    "source": doc.get("source", ""),
                                    "date": doc.get("added_date", "")
                                })
                elif isinstance(documents, str):
                    if query_lower in documents.lower():
                        results.append({
                            "category": category,
                            "type": doc_type,
                            "content": documents,
                            "source": "",
                            "date": ""
                        })
        
        return results
    
    def export_knowledge_base(self) -> str:
        """Exportar base de conocimiento como JSON"""
        return json.dumps(self.knowledge_base, ensure_ascii=False, indent=2)
    
    def import_knowledge_base(self, json_data: str) -> bool:
        """Importar base de conocimiento desde JSON"""
        try:
            new_knowledge = json.loads(json_data)
            self.knowledge_base = new_knowledge
            return self.save_knowledge_base()
        except Exception as e:
            st.error(f"Error importando base de conocimiento: {str(e)}")
            return False

def render_knowledge_manager():
    """Renderizar interfaz para gestionar la base de conocimiento"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">📚 Gestor de Conocimiento Legal</h1>
        <p style="color: white; font-size: 1.1rem; margin-top: 0.5rem;">Administra tu base de conocimiento jurídico</p>
    </div>
    """, unsafe_allow_html=True)
    
    km = LegalKnowledgeManager()
    
    # Pestañas para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Ver Base", "➕ Agregar", "🔍 Buscar", "📤 Exportar/Importar"])
    
    with tab1:
        st.subheader("Base de Conocimiento Actual")
        
        for category in km.get_knowledge_categories():
            with st.expander(f"📁 {category}"):
                category_data = km.knowledge_base[category]
                for doc_type, content in category_data.items():
                    st.write(f"**{doc_type}:**")
                    if isinstance(content, list):
                        for i, item in enumerate(content):
                            if isinstance(item, dict):
                                st.write(f"  {i+1}. {item.get('content', str(item))}")
                                if item.get('source'):
                                    st.caption(f"Fuente: {item['source']}")
                            else:
                                st.write(f"  {i+1}. {item}")
                    else:
                        st.write(f"  {content}")
    
    with tab2:
        st.subheader("Agregar Nuevo Documento Legal")
        
        category = st.selectbox("Categoría:", km.get_knowledge_categories())
        doc_type = st.text_input("Tipo de documento:")
        content = st.text_area("Contenido:", height=200)
        source = st.text_input("Fuente (opcional):")
        
        if st.button("➕ Agregar Documento", type="primary", use_container_width=True):
            if category and doc_type and content:
                if km.add_legal_document(category, doc_type, content, source):
                    st.success("✅ Documento agregado exitosamente")
                    st.rerun()
                else:
                    st.error("❌ Error al agregar documento")
            else:
                st.warning("Por favor, completa todos los campos obligatorios")
    
    with tab3:
        st.subheader("Buscar en Base de Conocimiento")
        
        search_query = st.text_input("Término de búsqueda:")
        if search_query:
            results = km.search_knowledge(search_query)
            
            if results:
                st.write(f"**Resultados encontrados: {len(results)}**")
                for result in results:
                    with st.expander(f"📄 {result['category']} - {result['type']}"):
                        st.write(f"**Contenido:** {result['content']}")
                        if result['source']:
                            st.caption(f"**Fuente:** {result['source']}")
                        if result['date']:
                            st.caption(f"**Fecha:** {result['date']}")
            else:
                st.info("No se encontraron resultados para tu búsqueda")
    
    with tab4:
        st.subheader("Exportar/Importar Base de Conocimiento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Exportar:**")
            if st.button("📤 Exportar JSON"):
                json_data = km.export_knowledge_base()
                st.download_button(
                    label="📥 Descargar Base de Conocimiento",
                    data=json_data,
                    file_name="legal_knowledge_base.json",
                    mime="application/json"
                )
        
        with col2:
            st.write("**Importar:**")
            uploaded_file = st.file_uploader("Seleccionar archivo JSON", type=['json'])
            if uploaded_file is not None:
                try:
                    json_data = uploaded_file.read().decode('utf-8')
                    if st.button("📥 Importar Base de Conocimiento"):
                        if km.import_knowledge_base(json_data):
                            st.success("✅ Base de conocimiento importada exitosamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al importar")
                except Exception as e:
                    st.error(f"Error leyendo archivo: {str(e)}") 