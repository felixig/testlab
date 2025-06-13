import streamlit as st
import pandas as pd

# Cargar usuarios
users_df = pd.read_csv("users.csv")

st.title("Login")

username = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

if st.button("Entrar"):
    user = users_df[(users_df["username"] == username) & (users_df["password"] == password)]
    if not user.empty:
        st.success("Login correcto")
        filename = user.iloc[0]["file"]
        with open(filename, "r") as f:
            content = f.read()
        st.text_area("Archivo asignado", content, height=200)
        # Para descarga:
        st.download_button("Descargar archivo", data=content, file_name=filename)
    else:
        st.error("Usuario o contraseña incorrectos")
