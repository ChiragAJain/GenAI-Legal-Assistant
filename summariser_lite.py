import os
import docx
import json
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
from datetime import datetime

def extract_text_from_txt(file_path):
    """Extract text from TXT file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text_from_pdf(file_path):
    """Extract text from PDF file."""
    pdf_reader = PdfReader(file_path)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file."""
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

def split_into_sections(text):
    """Split text into logical sections based on common legal headings."""
    sections = {}
    current_section = "Introduction"
    sections[current_section] = []

    # Common legal section headers
    legal_headers = [
        "DEFINITIONS", "PAYMENT", "LICENSE", "CONFIDENTIALITY", 
        "LIABILITY", "INDEMNITIES", "TERMINATION", "WARRANTIES", 
        "GOVERNING LAW", "PRIVACY", "COOKIES", "DATA", "SERVICES",
        "ACCOUNT", "CONTENT", "INTELLECTUAL PROPERTY", "DISPUTE"
    ]

    for line in text.splitlines():
        line_upper = line.strip().upper()
        
        # Check if line contains a legal header
        if any(header in line_upper for header in legal_headers):
            current_section = line.strip()
            sections[current_section] = []
        else:
            sections[current_section].append(line)
    
    # Join lines for each section
    for section, lines in sections.items():
        sections[section] = " ".join(lines).strip()
    
    return sections

def extract_key_terms(text, num_terms=5):
    """Extract key terms using simple text analysis (no AI required)."""
    # Common legal terms to look for
    legal_terms = [
        "agreement", "contract", "terms", "conditions", "service", "user",
        "liability", "damages", "warranty", "license", "privacy", "data",
        "payment", "fee", "refund", "termination", "breach", "dispute",
        "intellectual property", "copyright", "trademark", "confidential"
    ]
    
    text_lower = text.lower()
    found_terms = []
    
    for term in legal_terms:
        if term in text_lower:
            found_terms.append(term)
        if len(found_terms) >= num_terms:
            break
    
    return ", ".join(found_terms[:num_terms])

def create_simple_summary(text, max_sentences=3):
    """Create a simple summary by extracting key sentences."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Prioritize sentences with legal keywords
    important_keywords = ['shall', 'must', 'required', 'prohibited', 'liable', 'responsible']
    scored_sentences = []
    
    for sentence in sentences:
        score = sum(1 for keyword in important_keywords if keyword.lower() in sentence.lower())
        scored_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    top_sentences = [sent[1] for sent in scored_sentences[:max_sentences]]
    
    return top_sentences

def summarize_sections(sections, min_length=150, max_length=300):
    """Create summaries for each section using rule-based approach."""
    summaries = {}
    
    for section_name, content in sections.items():
        if not content.strip():
            continue
            
        # Create simple summary
        key_sentences = create_simple_summary(content, max_sentences=3)
        
        # Format as numbered points
        formatted_summary = ""
        for i, sentence in enumerate(key_sentences, 1):
            formatted_summary += f"{i}. {sentence.strip()}.\n"
        
        # Add key terms
        key_terms = extract_key_terms(content)
        if key_terms:
            formatted_summary += f"\n📋 Key Terms: {key_terms}\n"
        
        summaries[section_name] = formatted_summary.strip()
    
    return summaries

def compile_final_summary(summaries):
    """Compile summaries with enhanced formatting."""
    header = "=" * 60 + "\n"
    header += "📄 TERMS & CONDITIONS SUMMARY\n"
    header += "=" * 60 + "\n\n"
    
    if len(summaries) > 1:
        header += "🔍 EXECUTIVE OVERVIEW\n"
        header += "-" * 25 + "\n"
        header += "This document has been analyzed and summarized into key sections below.\n"
        header += "Each section contains the most important points in plain language.\n\n"
    
    formatted_sections = []
    
    for section_name, summary in summaries.items():
        section_header = f"📋 {section_name.upper()}\n"
        section_header += "-" * (len(section_name) + 4) + "\n"
        
        formatted_section = section_header + summary + "\n"
        formatted_sections.append(formatted_section)
    
    footer = "\n" + "=" * 60 + "\n"
    footer += "⚠️  IMPORTANT DISCLAIMER\n"
    footer += "=" * 60 + "\n"
    footer += "This is a rule-based summary for informational purposes only.\n"
    footer += "Please refer to the original document for complete legal terms.\n"
    footer += "Consult with legal professionals for important decisions.\n"
    
    final_summary = header + "\n\n".join(formatted_sections) + footer
    return final_summary

def clean_text_for_pdf(text):
    """Clean text for PDF compatibility."""
    return text.encode('latin-1', 'replace').decode('latin-1')

def save_summary_as_pdf(summary, output_path="static/summary_output.pdf"):
    """Create a professionally formatted PDF."""
    # Ensure static directory exists
    os.makedirs("static", exist_ok=True)
    
    summary = clean_text_for_pdf(summary)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add header
    pdf.set_font("Arial", style="B", size=16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "Terms & Conditions Summary", ln=True, align="C")
    pdf.ln(5)
    
    # Add generation date
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ln=True, align="C")
    pdf.ln(10)
    
    # Reset text color
    pdf.set_text_color(0, 0, 0)
    
    # Process content
    lines = summary.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
            
        if line.startswith('='):
            if not line.replace('=', '').strip():
                pdf.ln(2)
            else:
                pdf.set_font("Arial", style="B", size=14)
                pdf.set_text_color(0, 51, 102)
                header_text = line.replace('=', '').strip()
                if header_text:
                    pdf.cell(0, 8, header_text, ln=True, align="C")
                    pdf.ln(3)
        
        elif line.startswith('📋') or line.startswith('🔍'):
            pdf.set_font("Arial", style="B", size=12)
            pdf.set_text_color(0, 102, 51)
            clean_line = line.encode('ascii', 'ignore').decode('ascii')
            pdf.cell(0, 8, clean_line, ln=True)
            pdf.ln(2)
        
        elif line.startswith('-'):
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 4, line, ln=True)
            pdf.ln(1)
        
        elif line.startswith('⚠️'):
            pdf.set_font("Arial", style="B", size=10)
            pdf.set_text_color(204, 102, 0)
            clean_line = line.encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 5, clean_line)
            pdf.ln(2)
        
        elif any(line.startswith(str(i) + '.') for i in range(1, 10)):
            pdf.set_font("Arial", size=11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, line, align="J")
            pdf.ln(2)
        
        elif line.startswith('Key Terms:') or line.startswith('📋 Key Terms:'):
            pdf.set_font("Arial", style="I", size=10)
            pdf.set_text_color(51, 51, 153)
            clean_line = line.encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 5, clean_line)
            pdf.ln(3)
        
        else:
            pdf.set_font("Arial", size=11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, line, align="J")
            pdf.ln(2)
    
    # Add footer
    pdf.ln(10)
    pdf.set_font("Arial", style="I", size=9)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4, "This summary was generated using rule-based text analysis. Please consult the original document and legal professionals for complete information.")
    
    pdf.output(output_path)

def store_feedback(feedback_text, feedback_file="feedback.json"):
    """Store user feedback."""
    feedback_data = {
        "feedback": feedback_text,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        with open(feedback_file, "a") as file:
            json.dump(feedback_data, file)
            file.write("\n")
    except Exception as e:
        print(f"Error storing feedback: {e}")