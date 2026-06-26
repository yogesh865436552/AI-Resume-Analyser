import streamlit as st

st.title("AI Resume Analyser")
st.write("Upload your resume and get feedback.")

#adding file upload
uploaded_file = st.file_uploader("Upload your resume PDF", type=["pdf"])
if uploaded_file:
    st.success(f"Loaded: {uploaded_file.name}")