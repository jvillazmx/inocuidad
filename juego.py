import streamlit as st
import pandas as pd
import os
import re
import gspread
from google.oauth2 import service_account

ARCHIVO_PREGUNTAS = "preguntas.csv"

# Credenciales completas embebidas correctamente desde nueva clave JSON
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "encouraging-key-455121-q7",
    "private_key_id": "c92708db11ab682d59e80089533eee9edaf40df6",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDrI/tbgnk+Lr71\n7Qg3ypto/L5UD/vMwLipJZW6EbbKgD0IT6jqOVVmV/PD5ywCw9ETO5qh7U+j1jhd\nOIx34wFEujhqD80LEolf+VfzX72vzm+atgUlGh/rKK2Fc2s2/glJFj/UW3Qq7wmc\n/1Rp84SE+p3RoZOgAYwMkPwdBXVAL+mFUUG3I6dFKgBFp88NtCM8BSuDVNNEcDrg\n/ZwA0YtqaDwro3zgHqT7IGHfRvYbdS2eprOXykMwnaS8PWZgAvFeFWIs36QPkuIO\n2Cv1YqDSEC9jq5coO4QbAeYycPDOPA4MvOSWi0twmRLm+atVmPxmcMMGh4vN8PC5\n8GphlvsJAgMBAAECggEADCbJ4JeRIgnsZTntbzF4CPVQW971/KwHXvmWqUAtGbEf\nqYRKwf/ztKkRUd7Q3KId9eGvD6f7ftRqCUQMDk4CGZK+EGazClvYEy7UwSEB5OOR\ny1IvJeGzVvjwYeS7D7AR7sYvLXXXpQUnxaAN6FCYJcvsLl8sb9v+NTZw5CPaEVab\n83eRr+z2BSbPBk47hk5x9NAjy/6YSCEbPUh/YGw2l1+ES9niDfqutG9PYrTkG4rF\naunhqVQfBZFwUo3OgFP78cOqDKpUY0XqzaiGwKymysqE0tFoT7gAGYi5g7jPCeod\nhrxaXImpfLI8aRCTtBAeivQ8O32FHvsw2DJyMmrVuQKBgQD+EQZz2gFhTXN78nTX\n5s7Y763iFPqjT8xY1WXjbCZrPilNzxdWkWSzxH0/8xluOuYeq3vnaWfYMyT3Xi3t\nQbrCH7Uf4MnWlDihRvyGBXqwvzIOIIsg338Rf0l5fagves6ygbu4hvGPophNa0RN\nikIi4Y63MOipDcIMLsgJ8628YwKBgQDs7hW+wRZVpq5PVFf8Zv8H1lONVCtc1IQv\nFb3EbHyjZNZu/7ZdZ/ozUD7ECqJEY90VO3tcV08SPlnn/mMVe9KcMxFE158Ur2Tr\nlIoSwMEQzMZF/MhczTPUTXhl9dNXJXFzi7WIJmVdWoawfhU2viPT3+wdkqs0plbB\ndO2ZqNJYowKBgBRoKayEhjfakLwT7W6qC1NBbSYLqVYUwsUf3t81gKB8jbTCPY2m\ngAAweB7618AS2wj7nSgpPz4OXZnA5s93yBhvk4zL8Wpa3XGW0hGxvvkTYmHgG0y4\npuww3SX1Ad1Ob+vGn91ieWSgGrudMg9IW6eRlnUAaK+rezqfR1IFUJ8hAoGASxdu\nVuXVkVHhnwzpUfrGy5IXKwzJLYPBXTbzzSRhIFweRlHPV61TtB2ztuhz418PO+J9\nR5f4XJzcW9XZS37SEmVxDLOWHLU2NCAA3s6uogd0s8vZKOh0i8394brWv6EDYw6d\ne0hICh1d4OQlDxOWQVmP+RN6JZaummPXxkKmYCcCgYEA6B19Tl1QY7qbQtXrDooa\njMW2aTeVCLp8WxuHDz3WApyyZSpUlsJ0ukvs09C/5EY5Ipfi9XcD5Fiy/WHhhesM\nDN3IVoP36bAEWf6qLc38s/u4JOovhxzBoM/aeQGmOFEFo3FtJeJPOkxpVnIL3461\npwjKSchouin2z6VvW/Fz5iQ=\n-----END PRIVATE KEY-----\n",
    "client_email": "streamlit-sheets@encouraging-key-455121-q7.iam.gserviceaccount.com",
    "client_id": "111324100562432468989",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-sheets@encouraging-key-455121-q7.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

SHEET_ID = "1JKFHKOJQcC1UHrnDIs5w7JrclKaXlBuEUsrvxQ4NvEY"

# Clase para nombres de columnas
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

if not st.session_state.usuario or not st.session_state.inicio_confirmado:
    st.markdown("### Bienvenido al juego")
    correo = st.text_input("Ingresa tu correo electrónico:", key="correo_input")
    if st.button("Iniciar juego"):
        if re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            st.session_state.usuario = correo
            st.session_state.inicio_confirmado = True
            st.rerun()
        else:
            st.warning("Por favor, introduce un correo válido.")
    st.stop()

def guardar_resultado_google():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=scope
    )
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

if st.session_state.current_q.startswith("FIN"):
    mostrar_final()
else:
    mostrar_pregunta()

st.sidebar.markdown("### Progreso")
st.sidebar.write("Correo:", st.session_state.usuario)
st.sidebar.write("Puntos:", st.session_state.puntos)
st.sidebar.write("Historial:", st.session_state.historial)
