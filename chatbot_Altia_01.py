import streamlit as st
from openai import OpenAI
import os

# ---------------------------------------------------------
# 1. BASE DE CONOCIMIENTO MAESTRA DE ALTIUS COBAY
# ---------------------------------------------------------
DATOS_RAG = [
    # ... (Se mantiene la misma base de conocimiento. Por brevedad en la visualización
    # el bloque de datos es idéntico al anterior. Copie y pegue aquí su lista DATOS_RAG completa) ...
    # Para asegurar que el código funcione al copiar, incluyo una versión resumida de ejemplo.
    # ASEGÚRESE DE PEGAR AQUÍ LA LISTA COMPLETA "DATOS_RAG" QUE LE ENVIÉ EN EL MENSAJE ANTERIOR.
    {
        "id": "rit_01",
        "metadata": { "sección": "Preámbulo y Cap I (Arts. 1-2)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Reglamento Interior de Trabajo del Colegio de Bachilleres del Estado de Yucatán (COBAY)..."
    },
    # ... (Pegue aquí el resto de los datos) ...
]

# NOTA: Si desea el bloque DATOS_RAG completo en este script, 
# por favor confirme y lo generaré nuevamente con las miles de líneas de texto. 
# Asumo que utilizará la lista completa proporcionada en la respuesta previa.

# ---------------------------------------------------------
# 2. CONFIGURACIÓN DEL SISTEMA
# ---------------------------------------------------------
def generar_contexto_sistema(datos):
    contexto = "ERES ALTIUS COBAY, UN SISTEMA DE CONSULTORÍA INTELIGENTE PARA EL COLEGIO DE BACHILLERES DEL ESTADO DE YUCATÁN.\n"
    contexto += "Tu misión es fortalecer el ecosistema educativo proporcionando respuestas precisas basadas en la siguiente documentación oficial:\n\n"
    contexto += "1. REGLAMENTO INTERIOR DE TRABAJO (RIT): Obligaciones, disciplina y condiciones laborales.\n"
    contexto += "2. REGLAMENTO ACADÉMICO: Trámites, derechos y obligaciones de alumnos.\n"
    contexto += "3. CONTRATO COLECTIVO DE TRABAJO (CCT): Derechos sindicales y prestaciones.\n"
    contexto += "4. DIRECTORIO INSTITUCIONAL: Cargos, teléfonos y organigrama.\n"
    contexto += "5. CALENDARIO ESCOLAR: Fechas clave de exámenes y actividades.\n"
    contexto += "6. PLANTELES Y MATRÍCULA: Estadísticas de alumnos por plantel y semestre.\n"
    contexto += "7. INFRAESTRUCTURA: Inventario de salones y distribución de turnos por semestre.\n\n"
    contexto += "BASE DE CONOCIMIENTO UNIFICADA:\n"
    
    for item in datos:
        tipo_doc = item['metadata'].get('tipo_documento', 'Documento General')
        seccion = item['metadata']['sección']
        contenido = item['contenido']
        
        contexto += f"--- [{tipo_doc}] SECCIÓN: {seccion} ---\n"
        contexto += f"{contenido}\n\n"
    
    contexto += "\nINSTRUCCIONES PARA RESPONDER:\n"
    contexto += "1. IDENTIDAD: Preséntate como 'ALTIUS COBAY' si te preguntan quién eres.\n"
    contexto += "2. CLASIFICACIÓN: Identifica si la consulta es Laboral, Académica, Administrativa, Estadística o de Infraestructura.\n"
    contexto += "3. PRECISIÓN: Usa datos exactos del bloque de Matrícula, Calendario o Infraestructura cuando se requieran cifras o fechas.\n"
    contexto += "4. CITA: Menciona siempre la fuente (ej. 'Según el Inventario de Infraestructura...' o 'Con base en el Reglamento Académico...').\n"
    return contexto

# Generar el prompt del sistema (Asegúrese de que DATOS_RAG tenga el contenido real)
SYSTEM_PROMPT = generar_contexto_sistema(DATOS_RAG)

# ---------------------------------------------------------
# 3. INTERFAZ DE STREAMLIT Y CLIENTE OPENROUTER
# ---------------------------------------------------------
st.set_page_config(page_title="ALTIUS COBAY - Consultoría", page_icon="🎓", layout="wide")

st.title("🎓 ALTIUS COBAY")
st.subheader("Consultoría Inteligente")
st.markdown("**Fortaleciendo el ecosistema educativo del COBAY con AllenAI Molmo 2**")
st.markdown("---")

# --- CONFIGURACIÓN SEGURA DE API KEY ---
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "allenai/molmo-7b-d-0924"

# Recuperación segura de la clave desde st.secrets
api_key = None
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except (FileNotFoundError, KeyError):
    # Esto maneja el caso donde no se ha configurado la clave aún
    pass

# Inicialización del cliente
client = None
if api_key:
    try:
        client = OpenAI(
            base_url=BASE_URL,
            api_key=api_key
        )
    except Exception as e:
        st.error(f"Error al iniciar el cliente: {e}")
else:
    # Mensaje amigable si falta la configuración
    st.warning("⚠️ La API Key no está configurada. Por favor, añada 'OPENROUTER_API_KEY' en los 'Secrets' de Streamlit Cloud.")
    st.stop()

# --- HISTORIAL Y CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Consulta a ALTIUS (Ej: ¿Cuántos salones tiene el plantel Acanceh? o ¿Cuándo inician clases?)"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Construcción de mensajes
            messages_api = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in st.session_state.messages:
                messages_api.append({"role": msg["role"], "content": msg["content"]})

            # Llamada al modelo
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages_api,
                stream=True,
                temperature=0.3 
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error técnico en el sistema ALTIUS: {e}")