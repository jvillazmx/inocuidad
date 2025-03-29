import streamlit as st
import pandas as pd
import os
import re
import gspread
from google.oauth2 import service_account

ARCHIVO_PREGUNTAS = "preguntas.csv"

# Credenciales completas embebidas (temporalmente)
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "encouraging-key-455121-q7",
    "private_key_id": "c4bc2d2ca3f15959cb0d9226664efa8c855582cd",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8mTQx2DhTwX4Q\nV5ARHJ08WiSOPj4WmVhUAvLFhXNoPQINqHTAxb2fbi+nEvZ3KmCtpuJCeFkMGnOj\nOG9qgN8HkXPzwOCNU6NabnYhM5uEV9zyClB8Y4JSMDZuOErfvLuQnGvciSPbEXgY\n8hR3lKceukFaaAD8Z5OBnPhA4wDSl38cfv7I5S6VLXtCGXFPquE1VMyVdcN6GCbp\nTFiZ7N8R9GLoOYDg1BN9l4tQydV1N6aXzH4euP4KuUYZV2RoLUnZgNhTof9ySujn\nBg8uA1qpqB85D8wlCuImkg0CEeGdp+QibUYeYtAh3+iD00zyRZhEtQXc1Hk86ZOV\n9Oa6NdvBAgMBAAECggEBAKX7OJ6uA6Yv2rzB8QLMcRWJWaBrq2Z5Z0CjU+j+Kkzu\nMJddD9uJTxImFbUtHQvV+d58rAG/YoIjKhYeB2XyGcAzSvkl+oij1eJBa+zlgjMR\ncbA5kIptdWbcxmkOPkzSuPccFGpFbRxSRe2EkMFRZwGHRjSeJlZ8p9rMn0gkBsyQ\nbkaLTDv4RwtjJP3IqEkU4kzECFl+SyHyO3YgzRGr9ivXTLqAf9BkYqGGHygplEgs\nGX+lB7ASkSTvw6tTyQlZ4/x63jMfJvW0OqntpbqkYNR/j1yb8Vh9Bg2ZJVRKrY+r\nsBQNFuw4qlrtW2MRoW+qgFaJLF3ERrHHquy2KUUMY7ECgYEA4YIlRLS3x6e0gmq2\nT2RclO0TwOe64vhnRM6Xj2Tym1m1A7qbVLxCtJebqqj4Y8Dah9ofItMXMJjqSPdi\nEK2BJGcjQZfqDDGoFtXFoJOnQ/7TSZGUO0UktA5wzQmSP2lsoqQtNKvsG90sALUi\nCfp2RlmOCUpydvEtLk3+yP0FZ+8CgYEA0SEOM4LNuypgR8qYypRVZSc0ieZHT6hB\nCv7tuoFVxcyNPeW54P2nEkZn2xQICmZNRX0DWfA0Xh5MGi40pyLoRj0pHGyvnO8X\n4efBxd02WcfhyurH1CZo3lvHta1Gn2WW8dBYqV3Z5zH5t5FgZcViFE6/j+WqMiQ9\nX6cZL7JTT78CgYEAu6dT53GMzKhOEutUAvQq9C5exQL4uT5ApFy09vRoP0CgLV1W\nP9dsmIXpA2RrsGZm7UuXyWGF+v0TRZhOcWxTvzYN65QogTbXZb9aLO4Dy+5cQAu5\nTjYhMI4bOeiTr0XwhG4Gp7Dfx8TVXcC+u0ZaaVPhvdRll5U1OshZ6B+MphECgYEA\nke5y1kZ+zVopdYOR+NRRM7E3plZDTvXjVydcNVrRBg5r01FktAyGXpZLLtd5Moc+\nKXAlVROj+rpUb2N0dtHK38a9KXLKPMFbg3J9To5z+lKoqKtgaIBZPXB32poMNnqE\nQMQ9wXt5N+H5efKmDtMZZAwlWICtEpoM0Ocd/h8vkl8CgYBhz7US3dzkuzP1zjPw\n9qZh0kAV0YZ5xrbOETPB+zVhxMaALWu7qnJxruEcNf/N1tvN9guvZ4RUt4N4nAYL\nmK5rOvo81VNkKpBh7bVL5tKnPkudYcAnkOZGLiyMGhKqMJfLPYrRnZ6H5OrKyfdi\nXjPAihqzptdBka2BYT+Wf9DCWw==\n-----END PRIVATE KEY-----\n",
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
