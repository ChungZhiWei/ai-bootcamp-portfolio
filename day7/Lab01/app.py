import streamlit as st
from dotenv import load_dotenv

from parse import read_resume_pdf
from analyzer import (
    extract_resume_profile, extract_jd_profile, analyse_keyword_match,
    analyse_bullets, analyse_jargon, analyse_structure,
    #analyse_background_fit, 
    analyse_degree_alignment, summarise_overall, compute_overall_score
)

load_dotenv()
VALID_DEGREES = ["RTIS", "IMGD", "UXGD", "BFA"]

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description", height=250)
degree = st.selectbox("Select Degree", VALID_DEGREES)
run = st.button("Analyze Resume")

if run:
    if not resume_file or not jd_text:
        st.error("Please upload resume and paste job description.")
        st.stop()
    # ... call read_resume_pdf(resume_file), then each analyse_* function in turn,
    #     exactly as main.py's 8-step pipeline does — see Solutions/ for the full version.
    else:
        import os
        model = os.getenv("MODEL")
        print(f"Using model: {model}")

        print(f"[1/8] Parsing résumé: {resume_file}")
        resume_text = read_resume_pdf(resume_file)

        print(f"[2/8] Reading JD: {jd_text}")

        print("[3/8] Extracting résumé profile (LLM)...")
        resume_profile = extract_resume_profile(resume_text)

        print("[4/8] Extracting JD profile (LLM)...")
        jd_profile = extract_jd_profile(jd_text)

        print("[5/8] Keyword match (LLM)...")
        keyword_match = analyse_keyword_match(resume_profile, jd_profile)

        print("[6/8] Bullet audit (LLM)...")
        bullets = analyse_bullets(resume_profile)

        print("[7/8] Jargon, structure, background fit (LLM x3)...")
        jargon         = analyse_jargon(resume_profile, jd_profile)
        structure      = analyse_structure(resume_text)
        #background_fit = analyse_background_fit(resume_profile, jd_profile)
        degree_alignment = analyse_degree_alignment(jd_profile, degree)#resume_profile["education"]["degree"])

        report = {
            "meta": {
                "resume_path": resume_text,
                "job_path": jd_text,
                "model": model
            },
            "resume_profile":  resume_profile,
            "jd_profile":      jd_profile,
            "keyword_match":   keyword_match,
            "bullets":         bullets,
            "jargon":          jargon,
            "structure":       structure,
            "degree_alignment":  degree_alignment,
            #"background_fit":  background_fit,
        }
        report["overall_score"]       = compute_overall_score(report)
        report["passes_ats_threshold"] = report["overall_score"] >= 60


        st.success("Process Resume Success!")
        st.write("[8/8] Final summary (LLM)...")
        report["summary"] = summarise_overall(report)
        st.write(report["summary"])

        verdict = "PASS" if report["passes_ats_threshold"] else "FAIL"
        st.write(verdict)
        st.write(
            f"Score: {report['overall_score']}/100  "
            f"({verdict} 60% ATS threshold)"
        )
