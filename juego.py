import streamlit as st
import pandas as pd
import os
import re
import json
import gspread
from google.oauth2 import service_account

ARCHIVO_PREGUNTAS = "preguntas.csv"
SHEET_ID = "1JKFHKOJQcC1UHrnDIs5w7JrclKaXlBuEUsrvxQ4NvEY"

class Columnas:
    ID = "id"
    PREGUNTA = "pregunta"
    OPCION1 = "opcion1"
    OPCION2 = "opcion2"
    OPCION3 = "opcion3"
    IR_A1 = "ir_a1"
    IR_A2 = "ir_a2"
    IR_A3 = "ir_a3"
    PUNTOS1 = "puntos1"
    PUNTOS2 = "puntos2"
    PUNTOS3 = "puntos3"

@st.cache_data
def cargar_preguntas():
    try:
        return pd.read_csv(ARCHIVO_PREGUNTAS)
    except Exception as e:
        st.error(f"No se pudo cargar el archivo de preguntas: {e}")
        st.stop()

preguntas_df = cargar_preguntas()

st.session_state.setdefault("usuario", "")
st.session_state.setdefault("inicio_confirmado", False)
st.session_state.setdefault("current_q", "Q1")
st.session_state.setdefault("puntos", 0)
st.session_state.setdefault("historial", [])

def obtener_credenciales_google():
    try:
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if not creds_json:
            raise ValueError("Variable de entorno 'GOOGLE_CREDENTIALS_JSON' no encontrada.")
        info = json.loads(creds_json)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        return service_account.Credentials.from_service_account_info(info, scopes=scope)
    except Exception as e:
        st.error(f"Error cargando credenciales de Google: {e}")
        st.stop()

def guardar_resultado_google():
    credentials = obtener_credenciales_google()
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SHEET_ID).sheet1
    sheet.append_row([
        st.session_state.usuario,
        st.session_state.puntos,
        " > ".join(st.session_state.historial)
    ])

def mostrar_final():
    final = preguntas_df[preguntas_df[Columnas.ID] == st.session_state.current_q]
    if not final.empty:
        st.success(final.iloc[0][Columnas.PREGUNTA])

    if 'guardado' not in st.session_state:
        guardar_resultado_google()
        st.session_state.guardado = True

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reiniciar juego"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        if st.button("Terminar"):
            st.write("Gracias por participar. Puedes cerrar esta pestaña.")
    st.stop()

def mostrar_pregunta():
    pregunta_actual = preguntas_df[preguntas_df[Columnas.ID] == st.session_state.current_q]
    if pregunta_actual.empty:
        st.error("Pregunta no encontrada.")
        st.stop()

    fila = pregunta_actual.iloc[0]
    st.markdown(f"### {fila[Columnas.PREGUNTA]}")

    opciones = []
    for i in range(1, 4):
        texto = fila.get(f"opcion{i}")
        if pd.notna(texto):
            opciones.append({
                "texto": texto,
                "ir_a": fila.get(f"ir_a{i}"),
                "puntos": fila.get(f"puntos{i}", 0)
            })

    textos_opciones = [op["texto"] for op in opciones]

    if "respuesta" in st.session_state and st.session_state["respuesta"] not in textos_opciones:
        del st.session_state["respuesta"]

    seleccion = st.radio("Selecciona una opción:", textos_opciones, key="respuesta", index=None)

    if seleccion:
        elegida = next(op for op in opciones if op["texto"] == seleccion)
        st.session_state.puntos += elegida["puntos"]
        st.session_state.historial.append(st.session_state.current_q)
        st.session_state.current_q = elegida["ir_a"]
        del st.session_state["respuesta"]
        st.rerun()

if not st.session_state.usuario or not st.session_state.inicio_confirmado:
    st.markdown("### Bienvenido al juego")
    correo = st.text_input("Ingresa tu correo electrónico:", key="correo_input")
    if st.button("Iniciar juego"):
        if re.fullmatch(r"[^@]+@[^@]+\.[a-zA-Z]{2,}", correo):
            st.session_state.usuario = correo
            st.session_state.inicio_confirmado = True
            st.rerun()
        else:
            st.warning("Por favor, introduce un correo válido.")
    st.stop()

if st.session_state.current_q.startswith("FIN"):
    mostrar_final()
else:
    mostrar_pregunta()

st.sidebar.markdown("### Progreso")
st.sidebar.write("Correo:", st.session_state.usuario)
st.sidebar.write("Puntos:", st.session_state.puntos)
st.sidebar.markdown(" > ".join(st.session_state.historial))
