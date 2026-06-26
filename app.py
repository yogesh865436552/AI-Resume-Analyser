import streamlit as st
from pypdf import PdfReader

st.title("AI Resume Analyser")
st.write("Upload your resume and get feedback.")

# reads each page - some pages return None so checking that
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

uploaded_file = st.file_uploader("Upload your resume PDF", type=["pdf"])
if uploaded_file:
    st.success(f"Loaded: {uploaded_file.name}")
 
job_desc = st.text_area(
    "Paste the job posting here:",
    height=250,
    placeholder="Copy and paste the full job descrption..."
    )   
    
