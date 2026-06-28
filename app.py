import streamlit as st
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import os
import re
import time

st.set_page_config(
    page_title="AI Resume Analyser",
    page_icon="🎯",
    layout="wide"
)

st.title("AI Resume Analyser")
st.write("Upload your resume and get feedback.")

# load API key from .env file - dont hardcode this
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Could not connect to Gemini: {e}")
    client = None

def extract_text_from_pdf(uploaded_file):
    # reads each page - some pages return None so checking that
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def analyze_resume(resume_text, job_description, company_name=""):
    company_context = ""
    if company_name.strip():
        company_context = f"""
    Candidate is applying to {company_name}.
    Factor in what {company_name} typically looks for
    based on their known hiring culture and tech stack.
    """
    prompt = f"""
You are a senior engineering hiring manager reviewing a resume.
Be direct and practical.

Start your response with exactly this line:
MATCH_SCORE: [number 0-100]%

Then give feedback in this format:

### Profile Fit Summary
2-3 honest sentences on whether this person fits the role.

### Missing Skills
What is clearly missing compared to the job description?

### Resume Line Rewrite
Pick one weak bullet and rewrite it stronger.
- Original: "[weak line]"
- Rewrite: "[stronger version with impact]"

### Git Commit Suggestions
Write 3 realistic git commits the candidate should push to prove
they have hands-on experience with the missing skills:
- feat(...): ...
- fix(...): ...
- feat(...): ...

### What To Do Next
3 practical steps they can take this week.

---
RESUME:
{resume_text}

---
JOB DESCRIPTION:
{job_description}

---
COMPANY: {company_name if company_name.strip() else "Not specified"}
{company_context}
"""
    # kept getting 503 on pro so added flash as fallback
    models_to_try = ['gemini-2.5-flash', 'gemini-2.5-pro']

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                if "503" in str(e):
                    wait = (attempt + 1) * 3
                    st.info(f"Servers busy, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    return f"Something went wrong: {e}"
        st.warning(f"{model_name} not responding, trying next model...")
    return "Both models overloaded. Try again in a minute."

# two column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Job Description")
    job_desc = st.text_area(
        "Paste the job posting here:",
        height=250,
        placeholder="Copy and paste the full job description..."
    )
    company_name = st.text_input(
        "Company you are applying to (optional):",
        placeholder="e.g. Google, Infosys, Swiggy, TCS..."
    )

with col2:
    st.subheader("Your Resume (PDF)")
    uploaded_file = st.file_uploader(
        "Upload your resume as a PDF",
        type=["pdf"],
        accept_multiple_files=False
    )
    if uploaded_file:
        st.success(f"Loaded: {uploaded_file.name}")

st.markdown("---")

if st.button("Analyse Resume", use_container_width=True):
    if not job_desc.strip():
        st.warning("Please paste a job description first.")
    elif not uploaded_file:
        st.warning("Please upload your resume PDF.")
    elif not client:
        st.error("API key missing. Check your .env file.")
    else:
        with st.spinner("Analysing your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            result = analyze_resume(resume_text, job_desc, company_name)
            score_match = re.search(r"MATCH_SCORE:\s*(\d+)%", result)

            if score_match:
                score = int(score_match.group(1))
                clean_result = re.sub(r"MATCH_SCORE:\s*\d+%", "", result).strip()

                if score >= 85:
                    st.success(f"Strong match: {score}%")
                elif score >= 60:
                    st.warning(f"Partial match: {score}%")
                else:
                    st.error(f"Low match: {score}%")

                if clean_result.strip():
                    tab1, tab2 = st.tabs(["Full Analysis", "Git Commit Suggestions"])
                    with tab1:
                        st.markdown(clean_result)
                    with tab2:
                        st.info("Build these features and push with these commit messages to prove hands-on experience with missing skills.")
                else:
                    st.warning("Analysis came back empty. Try again.")
            else:
                st.markdown(result)

# footer
st.markdown("---")
st.write("Made by Yogesh Madhukumar — learning by building 🚀")