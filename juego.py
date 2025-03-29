import streamlit as st
import pandas as pd
import os
import re
import gspread
from google.oauth2 import service_account

ARCHIVO_PREGUNTAS = "preguntas.csv"

# Credenciales completas embebidas correctamente desde JSON
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "encouraging-key-455121-q7",
    "private_key_id": "c4bc2d2ca3f15959cb0d9226664efa8c855582cd",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8mTQx2DhTwX4Q\nrdOQvYFJt7o2u2ou6y0c/Vp9vf11Sw945IhelxaTgZe6m6+HEZjWLbQuaTNqtfsR\nClf/pwKlkS2C42/XELU1QeOh8lAlz1MnPCs5oqOjg4xvyiJ59vNy+wudfd36yJsL\ntVk9zDBbp15E3Xb23goWcIL8xvO0wjhAxOWUibpA4SdjvIqF9ELOyg1V5U4p7Aa7\nWhokl4yEpDJCUlySqUmQNmwq/VNKVtfznCn7rz9Y/PX00+KWn4NpIla3W5k9qLtq\nAa5xwUOkbzctIm2EfY2Uu7Qfa7LLleIzJLQFTgBuND6OPkza1wEZuLcqbOemFMhy\n6fVJ35BxAgMBAAECggEADVEWBeT6CTPy5lOXyjMPU3i1HdM66qgxbcgX4SQOpv8P\nTx534JHzhqPSZltC2BsuewUMIXDNMB48ZZYg44zT24P2PjU3+uwTl3iZDaDR9vF+\nMhmGBdJNkqihvGz95TXCN96xEcRG7cPHatq5u+rUiUw2lE887K598Nqt7RJRN/SV\nkMkpg576cLL4fQnNc7RuNCfzXGjASuAThUrveadOorjOd/6ZCfayKU+X+zaLUTpl\nkbk2LP9iRUgFElNCBBxsPXeS1/0dgL8gwgEvsHkMZlRXlybZAh1vIdKlNvJcaECY\n6oCTprX1IboIFI5WPDSFFsLVCak7noFehJ94UeDs/wKBgQD2AK84FNBHJykJGAMe\nu1ZOxHduHGQCXT6vZKqp/YoerbHAGkWbg5zOEnEtLdcFvC3i+5XjJYglvJxfYHAj\nsqrwuwzdTig4aIoRu7K6nhNXp4kpjSDcLwcs0fNd95QvzBb8pZHJwJLQzjIUTb5i\nrgQOa5sbz0w0F945uGYrvwmQ1wKBgQDEQ07yTZqFgz/zJQLHIHRpdI8dcsGt2Yvu\nyc/JTFLQVn5tIhldlmEzRM2ORnL6D2geF/waZt7Ox4okiwWnFPIlpcSwEKk2oT+p\nbLNEZM1S5H0Ou1adlvBD3m2NTldlM39ioRpOTSllI2pfqPN+KFtFexYC4/NLbWh7\n3Uj0wbqX9wKBgE0NE9Sd+EqBAoJdqgSDKtpLARlU/SIccJjhD+9kgVFwl/8Se4Dl\nLUUCU76R4Apk0X6JzH2z8LvZIqVhAF6+BHqYK8RZSZG5dJ1vS+DVyDspN3XzRTqR\n5E5uiCqDdD+wTfbeKRanIZUTMG5Zl2szFAQsQg3o1PZwD2PG1QGYuXdLAoGAcf4q\nL4A1fNCz5xSbHW9TTiD+MvuBVOmjZilff6rN+uYR/m8sznfWswGGZtmyVF14euox\namBPj0jEit8YhGgdERLMP/sdXXag1FYndVUbEMdXf6P99gBCQxlBBi73gfc8SNwL\nvGkC3xSH51HpQ2BLSvrn2PvvRuMgKbloc4jGSRcCgYEA81LlTF1rWC5JeZDg/tog\nsTQluqWETTR77K7vNuTh/MHXMPvYoeonZ1ZqhxytuZfBEHPIZTFCeKeFDAO9hkl7\nCPuuMySYl6ddeQWyCmsPZTlLz/OtvORcDPlC4U7ocFvXeVUFNDxmDVeGlW/OYqpe\nQeFi0XAcF7NKA5Xh5X771fE=\n-----END PRIVATE KEY-----\n",
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
