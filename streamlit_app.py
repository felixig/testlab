import streamlit as st
import pandas as pd

# Cargar usuarios
users_df = pd.read_csv("users.csv")

st.title("Login")

username = st.text_input("User")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = users_df[(users_df["username"] == username) & (users_df["password"] == password)]
    if not user.empty:
        st.success("Right credentials")
        filename = user.iloc[0]["file"]
        with open(filename, "rb") as f:
            content = f.read()
        
        st.download_button(
            label="Download ZIP file",
            data=content,
            file_name=filename,
            mime="application/zip"
        )
      
    else:
        st.error("Wrong user or password!")

