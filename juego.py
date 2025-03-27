
import streamlit as st
import pandas as pd

# Cargar datos
preguntas_df = pd.read_csv("preguntas.csv")

# Inicializar estado
if 'current_q' not in st.session_state:
    st.session_state.current_q = "Q1"
    st.session_state.puntos = 0
    st.session_state.historial = []

# Buscar pregunta actual
pregunta_actual = preguntas_df[preguntas_df["id"] == st.session_state.current_q]

if pregunta_actual.empty:
    st.write("Pregunta no encontrada.")
else:
    fila = pregunta_actual.iloc[0]
    st.markdown(f"### {fila['pregunta']}")

    opciones = []
    for i in range(1, 4):
        if f"opcion{i}" in fila and pd.notna(fila[f"opcion{i}"]):
            opciones.append({
                "texto": fila[f"opcion{i}"],
                "ir_a": fila[f"ir_a{i}"],
                "puntos": fila[f"puntos{i}"]
            })

    for op in opciones:
        if st.button(op["texto"]):
            st.session_state.puntos += op["puntos"]
            st.session_state.historial.append(st.session_state.current_q)
            st.session_state.current_q = op["ir_a"]
            try:
                st.experimental_rerun()
            except:
                pass

# Mostrar estado
st.sidebar.markdown("### Progreso")
st.sidebar.write("Puntos:", st.session_state.puntos)
st.sidebar.write("Historial:", st.session_state.historial)

# Mostrar final si corresponde
if st.session_state.current_q.startswith("FIN"):
    final = preguntas_df[preguntas_df["id"] == st.session_state.current_q]
    if not final.empty:
        st.success(final.iloc[0]["pregunta"])
    if st.button("Reiniciar juego"):
        st.session_state.clear()
