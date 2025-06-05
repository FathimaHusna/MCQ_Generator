import streamlit as st
from dotenv import load_dotenv
import os
from src.mcq_generator.mcq_generator import generate_quiz, review_quiz
from src.mcq_generator.utils import safe_parse_json, extract_text_from_pdf
from src.config import RESPONSE_JSON_TEMPLATE
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

st.title("MCQ Generator using Gemini")

# --- Input options ---
input_mode = st.radio("Choose input method:", ["Type Text", "Upload PDF"])

if input_mode == "Type Text":
    text = st.text_area("Paste your lesson text here")
else:
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    text = ""
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)

# --- Additional inputs ---
subject = st.text_input("Enter subject", value="Biology")
tone = st.selectbox("Select tone", ["simple", "intermediate", "advanced"])
number = st.slider("Number of questions", 1, 10, 5)

# --- Generate button ---
if st.button("Generate MCQs"):
    if not text.strip():
        st.warning("Please provide some input text or upload a PDF.")
    else:
        with st.spinner("Generating..."):
            quiz = generate_quiz(model, text, number, subject, tone)
            review = review_quiz(model, quiz, subject)

            st.subheader("Quiz (Raw JSON)")
            st.code(quiz, language="json")

            # Try parsing and displaying formatted quiz
            try:
                parsed = safe_parse_json(quiz)
                st.subheader("Formatted Questions")
                for qid, q in parsed.items():
                    st.markdown(f"**Q{qid}. {q['mcq']}**")
                    for k, v in q["options"].items():
                        st.write(f"{k}) {v}")
                    st.success(f"✅ Correct: {q['correct']}")
            except Exception as e:
                st.error("❌ Could not parse quiz. Check format.")
                st.text(quiz)

            st.subheader("Review")
            st.write(review)
