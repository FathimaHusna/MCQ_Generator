import json
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from src.mcq_generator.utils import clean_json, safe_parse_json, extract_text_from_pdf
from src.mcq_generator.logger import logging  # ✅ make sure logger.py exists and is configured

# Default JSON format used in prompts
DEFAULT_RESPONSE_JSON = {
    "1": {
        "mcq": "What is the main function of the mitochondria in a cell?",
        "options": {
            "a": "Protein synthesis",
            "b": "DNA replication",
            "c": "Energy production",
            "d": "Photosynthesis"
        },
        "correct": "c"
    },
    "2": {
        "mcq": "Which gas is most responsible for the greenhouse effect?",
        "options": {
            "a": "Oxygen",
            "b": "Carbon Dioxide",
            "c": "Nitrogen",
            "d": "Hydrogen"
        },
        "correct": "b"
    }
}

from langchain.prompts import PromptTemplate

quiz_prompt_template = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template="""
Text: {text}

You are an experienced exam question setter for G.C.E. A/L {subject} students. 
Create exactly {number} higher-order thinking MCQs in a {tone} tone that reflect the style of past A/L examination papers.

Guidelines:
- Base each question strictly on the provided text.
- Ask conceptual, analytical, and inference-based questions.
- Avoid simple fact recall or direct copy-paste.
- Each question must have 4 distinct answer options: a, b, c, d.
- Mark the correct option as "correct".
- Ensure no repeated questions.

Return the output strictly in this JSON format:
{response_json}

Important: Output ONLY valid JSON. Do NOT use markdown or code blocks.
"""
)

review_prompt_template = PromptTemplate(
    input_variables=["subject", "quiz"],
    template="""
You are a G.C.E. A/L {subject} examiner. Review the following quiz:

1. Provide a 50-word analysis of cognitive complexity.
2. Adjust any question that lacks A/L standard depth.
3. Ensure tone and logic reflect past paper style.
4. Return updated quiz in the original JSON format.

Quiz:
{quiz}
"""
)


# # LangChain prompt for MCQ generation
# quiz_prompt_template = PromptTemplate(
#     input_variables=["text", "number", "subject", "tone", "response_json"],
#     template="""
# Text: {text}

# You are an expert MCQ maker. Create exactly {number} multiple choice questions for {subject} students in a {tone} tone.
# All questions should be based only on the provided text. Avoid repetition.

# Use this format strictly:
# {response_json}

# Important: Output only valid JSON. Do not use markdown or code fences.
# """
# )

# # LangChain prompt for MCQ review
# review_prompt_template = PromptTemplate(
#     input_variables=["subject", "quiz"],
#     template="""
# You are an expert English grammarian and teacher.

# Task:
# 1. Give a 50-word review on the cognitive and linguistic complexity of this quiz.
# 2. Revise any questions that may be too difficult.
# 3. Output final version in the same JSON format.

# Quiz:
# {quiz}
# """
# )

# Function to generate MCQs
def generate_quiz(model, text, number, subject, tone):
    try:
        prompt = quiz_prompt_template.format(
            text=text,
            number=number,
            subject=subject,
            tone=tone,
            response_json=json.dumps(DEFAULT_RESPONSE_JSON)
        )
        logging.info("Generating quiz with Gemini model...")
        raw_output = model.generate_content(prompt).text
        return clean_json(raw_output)  # ✅ Clean JSON using utils
    except Exception as e:
        logging.error(f"Error generating quiz: {e}")
        return "{}"

# Function to review the generated quiz
def review_quiz(model, quiz, subject):
    try:
        prompt = review_prompt_template.format(subject=subject, quiz=quiz)
        logging.info("Reviewing quiz for complexity and revisions...")
        raw_output = model.generate_content(prompt).text
        return clean_json(raw_output)
    except Exception as e:
        logging.error(f"Error reviewing quiz: {e}")
        return "{}"
