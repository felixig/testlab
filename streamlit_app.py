import streamlit as st
import pandas as pd
import json
import smtplib
from email.message import EmailMessage
import os

if "stage" not in st.session_state:
    st.session_state.stage = "login"
    st.session_state.username = ""
    st.session_state.correct_reps = {}
    st.session_state.current_block_index = 0

with open("contents/exercises.json", "r", encoding="utf-8") as f:
    blocks = json.load(f)

st.title("Lab Login")

if st.session_state.stage == "login":
    username = st.text_input("User")
    password = st.text_input("Password", type="password")
    course_code = st.text_input("Course code")

    if st.button("Login"):
        course_file_path = f"courses/{course_code}.csv"
        if os.path.exists(course_file_path):
            users_df = pd.read_csv(course_file_path)
            user = users_df[(users_df["username"] == username) & (users_df["password"] == password)]
            if not user.empty:
                st.session_state.stage = "download"
                st.session_state.username = username
                st.session_state.users_df = users_df
                st.success("Login successful!")
            else:
                st.error("Wrong credentials!")
        else:
            st.error("Invalid course code!")

if st.session_state.stage == "download":
    users_df = st.session_state.users_df
    user_row = users_df[users_df["username"] == st.session_state.username].iloc[0]
    filename = user_row["file"]

    with open(filename, "rb") as f:
        content = f.read()

    st.download_button("Download ZIP file", data=content, file_name=filename, mime="application/zip")

    if st.button("Continue"):
        st.session_state.stage = "exercise"
        st.session_state.current_block_index = 0

def show_block(block):
    for item in block["contents"]:
        if item["type"] == "text":
            st.markdown(item["value"])
        elif item["type"] == "image":
            st.image(item["value"], use_column_width=True)

def handle_question(block, user_row):
    rep_id = block["rep"]
    if rep_id == -1:
        return

    key = f"rep_{rep_id}_answer"
    if rep_id not in st.session_state.correct_reps:
        st.session_state.correct_reps[rep_id] = False

    if isinstance(user_row[f"REP-{rep_id}"], (int, float)):
        answer = st.number_input(f"Your answer to REP-{rep_id}:", key=key, step=1)
    else:
        answer = st.text_input(f"Your answer to REP-{rep_id}:", key=key)

    if st.button(f"Submit REP-{rep_id}", key=f"submit_{rep_id}"):
        expected = str(user_row[f"REP-{rep_id}"]).strip().lower()
        received = str(answer).strip().lower()
        if expected == received:
            st.success("Correct!")
            st.session_state.correct_reps[rep_id] = True
        else:
            st.error("Incorrect")
            
if st.session_state.stage == "exercise":
    users_df = st.session_state.users_df
    user_row = users_df[users_df["username"] == st.session_state.username].iloc[0]
    i = st.session_state.current_block_index

    reached_newpage = False
    while i < len(blocks) and not reached_newpage:
        block = blocks[i]
        show_block(block)
        handle_question(block, user_row)
        if block["newpage"]:
            reached_newpage = True
        i += 1

    page_blocks = blocks[st.session_state.current_block_index:i]
    all_questions_correct = all(
        st.session_state.correct_reps.get(block["rep"], True)
        for block in page_blocks if block["rep"] != -1
    )

    if all_questions_correct and st.button("Next"):
        st.session_state.current_block_index = i
        if st.session_state.current_block_index >= len(blocks):
            st.session_state.stage = "finished"
    elif not all_questions_correct:
        st.warning("Please answer all questions correctly before continuing.")

if st.session_state.stage == "finished":
    st.balloons()
    st.success("Lab completed. Thank you!")

    if "email_sent" not in st.session_state:
        team_name = st.session_state.username
        to_email = st.secrets["EMAIL_PROF1"]
        recipients = [st.secrets["EMAIL_PROF1"], st.secrets["EMAIL_PROF2"]]

        smtp_user = st.secrets["SMTP_EMAIL"]
        smtp_pass = st.secrets["SMTP_PASSWORD"]

        msg = EmailMessage()
        msg.set_content(f"{team_name} finished the lab example")
        msg["Subject"] = f"Lab completed by {team_name}"
        msg["From"] = smtp_user
        msg["To"] = ", ".join(recipients)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)
            st.info("Confirmation email sent.")
            st.session_state.email_sent = True
        except Exception as e:
            st.warning(f"Could not send email: {e}")

