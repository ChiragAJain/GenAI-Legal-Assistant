import os
import docx
import json
import time
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfReader
from transformers import PegasusTokenizer, AutoModelForSeq2SeqLM
from fpdf import FPDF
from keybert import KeyBERT

# Load models
tokenizer = PegasusTokenizer.from_pretrained("nsi319/legal-pegasus")
model = AutoModelForSeq2SeqLM.from_pretrained("nsi319/legal-pegasus")
keybert_model = KeyBERT()

# Text extraction functions remain the same
def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text_from_pdf(file_path):
    pdf_reader = PdfReader(file_path)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

# Split text into sections based on legal terms
def split_into_sections(text):
    sections = {}
    current_section = "Introduction"
    sections[current_section] = []

    for line in text.splitlines():
        if any(heading in line for heading in [
            "DEFINITIONS", "PAYMENT OF FEES", "LICENSE", 
            "CONFIDENTIALITY", "LIMITATION OF LIABILITY", 
            "INDEMNITIES", "TERMINATION", "WARRANTIES", "GOVERNING LAW"
        ]):
            current_section = line.strip()
            sections[current_section] = []
        else:
            sections[current_section].append(line)
    
    for section, lines in sections.items():
        sections[section] = " ".join(lines).strip()
    
    return sections

# Extract keywords using KeyBERT
def extract_keywords(text, num_keywords=10):
    keywords = keybert_model.extract_keywords(text, top_n=num_keywords)
    return ", ".join([kw[0] for kw in keywords])

# Summarize a single text chunk
def summarize_chunk(chunk, min_length=300, max_length=800):
    key_phrases = extract_keywords(chunk)
    chunk_with_keywords = key_phrases + " " + chunk

    inputs = tokenizer.encode(chunk_with_keywords, return_tensors="pt", truncation=True)
    outputs = model.generate(
        inputs,
        max_length=max_length,
        min_length=min_length,
        num_beams=4,
        length_penalty=2.0,
        no_repeat_ngram_size=3
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Summarize all sections with customizable length
def summarize_sections(sections, min_length=150, max_length=300, chunk_size=2000):
    summaries = {}
    for section, content in sections.items():
        if len(content.split()) > chunk_size:
            chunks = [content[i:i + chunk_size] for i in range(0, len(content.split()), chunk_size)]
        else:
            chunks = [content]

        section_summaries = []
        with ThreadPoolExecutor() as executor:
            section_summaries = list(executor.map(lambda chunk: summarize_chunk(chunk, min_length, max_length), chunks))
        combined_section_summary = ' '.join(section_summaries)
        if len(combined_section_summary.split()) > max_length * 1.5:
            inputs = tokenizer.encode(combined_section_summary, return_tensors="pt", truncation=True)
            outputs = model.generate(
                inputs,
                max_length=int(max_length * 0.75),
                min_length=min_length,
                num_beams=4,
                length_penalty=2.5,
                no_repeat_ngram_size=3
            )
            combined_section_summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

        bullet_points = combined_section_summary.split('. ')
        bullet_points = [f"- {point.strip()}" for point in bullet_points if point]

        glossary_terms = extract_keywords(content, num_keywords=5)
        if glossary_terms:
            bullet_points.append(f"\nKey Terms: {glossary_terms}")
        summaries[section] = "\n".join(bullet_points)
    
    return summaries

# Compile the summaries into a single text output
def compile_final_summary(summaries):
    final_summary = "\n\n".join(f"{section}:\n{summary}" for section, summary in summaries.items())
    return final_summary

# Helper function to format text for PDF
def clean_text_for_pdf(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

# Save the summary as a formatted PDF
def save_summary_as_pdf(summary, output_path="summary_output_legal.pdf"):
    summary = clean_text_for_pdf(summary)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    for section_summary in summary.split("\n\n"):
        if ":\n" in section_summary:
            section, content = section_summary.split(":\n", 1)
            pdf.set_font("Arial", style="B", size=12)
            pdf.multi_cell(0, 6, section + ":")
            pdf.set_font("Arial", size=12) 
            pdf.multi_cell(0, 6, content, align="J")
        else:
            pdf.multi_cell(0, 6, section_summary, align="J")
    pdf.output(output_path)

# Function for customizable summary length
def summarize_with_custom_length(text, custom_min_length, custom_max_length):
    sections = split_into_sections(text)
    summaries = summarize_sections(sections, min_length=custom_min_length, max_length=custom_max_length)
    final_summary = compile_final_summary(summaries)
    return final_summary

# Feedback collection function
def store_feedback(feedback_text, feedback_file="feedback.json"):
    with open(feedback_file, "a") as file:
        json.dump({"feedback": feedback_text}, file)
        file.write("\n")
