import streamlit as st
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import os

st.title("AI Resume Analyser")
st.write("Upload your resume and get feedback.")

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Could not connect to Gemini: {e}")
    client = None

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# basic analysis - just testing if API responds correctly first
def analyze_resume(resume_text, job_description, company_name=""):
    company_context = ""
    if company_name.strip():
        company_context = f"""
    Candidate is applying to {company_name}.
    Factor in what {company_name} typically looks for
    based on their known hiring culture and tech stack.
    """
    prompt = f"""
    Review this resume against the job description.
    Start with: MATCH_SCORE: [0-100]%
    {company_context}
    RESUME: {resume_text}
    JOB: {job_description}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

uploaded_file = st.file_uploader("Upload your resume PDF", type=["pdf"])
if uploaded_file:
    st.success(f"Loaded: {uploaded_file.name}")

job_desc = st.text_area(
    "Paste the job posting here:",
    height=250,
    placeholder="Copy and paste the full job description..."
)

company_name = st.text_input(
    "Company you are applying to (optional):",
    placeholder="e.g. Google, Infosys, Swiggy, TCS..."
)
