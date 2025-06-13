import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

# Cargar usuarios
users_df = pd.read_csv("users.csv")

st.title("Lab Login")

if "stage" not in st.session_state:
    st.session_state.stage = "login"
    st.session_state.username = ""
    st.session_state.answers_correct = [False, False, False]

# Login
if st.session_state.stage == "login":
    username = st.text_input("User")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = users_df[(users_df["username"] == username) & (users_df["password"] == password)]
        if not user.empty:
            st.session_state.stage = "download"
            st.session_state.username = username
            st.success("Login successful!")
        else:
            st.error("Wrong credentials!")

# File download
if st.session_state.stage == "download":
    user_row = users_df[users_df["username"] == st.session_state.username].iloc[0]
    filename = user_row["file"]

    with open(filename, "rb") as f:
        content = f.read()

    st.download_button("Download ZIP file", data=content, file_name=filename, mime="application/zip")

    if st.button("Continue to REP-1"):
        st.session_state.stage = "rep1"

# REP-1
if st.session_state.stage == "rep1":
    user_row = users_df[users_df["username"] == st.session_state.username].iloc[0]
    answer = st.number_input("REP-1: How many packets do you see in the capture?", step=1)
    if st.button("Submit REP-1"):
        if answer == user_row["REP-1"]:
            st.success("Correct!")
            st.session_state.answers_correct[0] = True
            st.session_state.stage = "rep2"
        else:
            st.error("Incorrect")

# REP-2
if st.session_state.stage == "rep2":
    user_row = users_df[users_df["username"] == st.session_state.username].iloc[0]
    answer = st.number_input("REP-2: What is the highest packet length in the capture?", step=1)
    if st.button("Submit REP-2"):
        if answer == user_row["REP-2"]:
            st.success("Correct!")
            st.session_state.answers_correct[1] = True
            st.session_state.stage = "rep3"
        else:
            st.error("Incorrect")

# REP-3
if st.session_state.stage == "rep3":
    user_row = users_df[users_df["username"] == st.session_state.username].iloc[0]
    answer = st.text_input("REP-3: What is the IP-destination of the last packet?")
    if st.button("Submit REP-3"):
        if answer.strip() == str(user_row["REP-3"]).strip():
            st.success("Correct!")
            st.session_state.answers_correct[2] = True
            st.session_state.stage = "finished"
        else:
            st.error("Incorrect")

# Final stage: send email
if st.session_state.stage == "finished":
    st.balloons()
    st.success("Lab completed. Thank you!")

    if "email_sent" not in st.session_state:
        team_name = st.session_state.username
        to_email = "felix.iglesias@tuwien.ac.at"  
        recipients = ["felix.iglesias@tuwien.ac.at", "tanja.zseby@tuwien.ac.at"]

        smtp_user = st.secrets["SMTP_EMAIL"]
        smtp_pass = st.secrets["SMTP_PASSWORD"]

        msg = EmailMessage()
        msg.set_content(f"{team_name} finished the lab example")
        msg["Subject"] = f"Lab completed by {team_name}"
        msg["From"] = smtp_user
        msg["To"] = ", ".join(recipients)

        try:
            # Configura correctamente según tu proveedor SMTP
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)

            st.info("Confirmation email sent.")
            st.session_state.email_sent = True
        except Exception as e:
            st.warning(f"Could not send email: {e}")

