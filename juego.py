import streamlit as st
import pandas as pd
import re
import json
import requests
import random
import os
from datetime import datetime

# Lista de archivos disponibles
ARCHIVOS_CUESTIONARIOS = [
    "cuestionarios/117_10_01.csv",
    "cuestionarios/117_10_02.csv",
    "cuestionarios/117_10_03.csv",
    "cuestionarios/117_10_04.csv",
    "cuestionarios/117_10_05.csv",
    "cuestionarios/117_10_06.csv",
    "cuestionarios/117_10_07.csv",
]

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxruyVe3qVkNICk613EpS_N86xFwYA5cB5UpyS1Y9WAzWkfK22BGkRReUbBr0mB52GAHQ/exec"


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
def cargar_preguntas(archivo):
    try:
        return pd.read_csv(archivo)
    except Exception as e:
        st.error(f"No se pudo cargar el archivo de preguntas: {e}")
        st.stop()

def guardar_resultado_en_google_apps_script():
    try:
        payload = {
            "cuestionario": os.path.basename(st.session_state.archivo_usado),
            "usuario": st.session_state.usuario,
            "puntos": st.session_state.puntos,
            "respuestas": " > ".join(st.session_state.historial),
            "historial": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        response = requests.post(WEB_APP_URL, json=payload)
        if response.status_code == 200:
            st.success("\u00a1Resultado enviado correctamente a Google Sheets! ✅")
        else:
            st.error(f"Error al guardar el resultado: {response.text}")
    except Exception as e:
        st.error(f"No se pudo conectar con Google Apps Script: {e}")

def mostrar_final():
    final = st.session_state.preguntas_df[st.session_state.preguntas_df[Columnas.ID] == st.session_state.current_q]
    if not final.empty:
        st.success(final.iloc[0][Columnas.PREGUNTA])

    if 'guardado' not in st.session_state:
        guardar_resultado_en_google_apps_script()
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
    pregunta_actual = st.session_state.preguntas_df[st.session_state.preguntas_df[Columnas.ID] == st.session_state.current_q]
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

# Inicialización de estado
st.session_state.setdefault("usuario", "")
st.session_state.setdefault("inicio_confirmado", False)
st.session_state.setdefault("current_q", "Q1")
st.session_state.setdefault("puntos", 0)
st.session_state.setdefault("historial", [])

if not st.session_state.usuario or not st.session_state.inicio_confirmado:
    st.markdown("### Bienvenido al juego")
    correo = st.text_input("Ingresa tu correo electrónico:", key="correo_input")
    if st.button("Iniciar juego"):
        if re.fullmatch(r"[^@]+@[^@]+\.[a-zA-Z]{2,}", correo):
            st.session_state.usuario = correo
            st.session_state.inicio_confirmado = True
            st.session_state.archivo_usado = random.choice(ARCHIVOS_CUESTIONARIOS)
            st.session_state.preguntas_df = cargar_preguntas(st.session_state.archivo_usado)
            st.rerun()
        else:
            st.warning("Por favor, introduce un correo válido.")
    st.stop()

# Cargar preguntas si no están ya cargadas
if "preguntas_df" not in st.session_state:
    st.session_state.archivo_usado = random.choice(ARCHIVOS_CUESTIONARIOS)
    st.session_state.preguntas_df = cargar_preguntas(st.session_state.archivo_usado)

# Mostrar preguntas
if st.session_state.current_q.startswith("FIN"):
    mostrar_final()
else:
    mostrar_pregunta()

# Barra lateral con progreso
st.sidebar.markdown("### Progreso")
st.sidebar.write("Correo:", st.session_state.usuario)
st.sidebar.write("Puntos:", st.session_state.puntos)
st.sidebar.markdown(" > ".join(st.session_state.historial))
