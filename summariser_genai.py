import os
import docx
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
from datetime import datetime

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    print("⚠️ GEMINI_API_KEY not found. GenAI features will not work.")
    model = None

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
    """Split text into manageable chunks for processing."""
    # For GenAI, we'll process the full text but may need to chunk for very large documents
    max_chunk_size = 30000  # Gemini has token limits
    
    if len(text) <= max_chunk_size:
        return {"Full Document": text}
    
    # Split into chunks if too large
    chunks = {}
    words = text.split()
    chunk_size = max_chunk_size // 4  # Conservative estimate for words to characters
    
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks[f"Section {i//chunk_size + 1}"] = chunk_text
    
    return chunks

def generate_summary(document_text):
    """Generate abstractive summary using Gemini API."""
    if not model:
        return "GenAI service unavailable. Please set GEMINI_API_KEY environment variable."
    
    prompt = f"""
    Analyze the following legal document and provide a comprehensive summary in exactly this format:

    **DOCUMENT SUMMARY**
    
    **Key Points:**
    • [5-7 bullet points covering the most important aspects]
    
    **Your Rights:**
    • [3-4 bullet points about user/consumer rights]
    
    **Your Obligations:**
    • [3-4 bullet points about user/consumer responsibilities]
    
    **Important Terms:**
    • [3-4 key definitions or terms to understand]
    
    Document to analyze:
    {document_text}
    
    Keep the language simple and accessible for non-lawyers. Focus on practical implications.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def answer_question(document_text, user_question):
    """Answer specific questions about the document using Gemini API."""
    if not model:
        return "GenAI service unavailable. Please set GEMINI_API_KEY environment variable."
    
    prompt = f"""
    Based on the following legal document, answer the user's question clearly and concisely.
    
    Document:
    {document_text}
    
    Question: {user_question}
    
    Instructions:
    - Provide a direct answer in plain language
    - Quote relevant sections if helpful
    - If the document doesn't contain the answer, say so clearly
    - Keep the response under 200 words
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error answering question: {str(e)}"

def analyze_risks(document_text):
    """Identify potential risks and non-standard clauses using Gemini API."""
    if not model:
        return "GenAI service unavailable. Please set GEMINI_API_KEY environment variable."
    
    prompt = f"""
    Analyze the following legal document and identify 3-5 potentially risky or non-standard clauses for a consumer.
    
    Format your response as:
    
    **RISK ANALYSIS**
    
    **🚨 High Risk:**
    • [Most concerning clauses with brief explanation]
    
    **⚠️ Medium Risk:**
    • [Moderately concerning clauses with brief explanation]
    
    **ℹ️ Points to Note:**
    • [Other important but less risky items]
    
    Document to analyze:
    {document_text}
    
    Focus on:
    - Unusual liability limitations
    - Broad indemnification clauses
    - Automatic renewals or difficult cancellation
    - Data usage beyond normal expectations
    - Dispute resolution limitations
    - Unusual termination conditions
    
    Explain each risk in simple terms that a non-lawyer can understand.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing risks: {str(e)}"

def summarize_sections(sections, min_length=150, max_length=300):
    """Process sections and generate comprehensive analysis."""
    if not sections:
        return {}
    
    # Combine all sections for full document analysis
    full_text = "\n\n".join(sections.values())
    
    # Generate summary
    summary = generate_summary(full_text)
    
    # Generate risk analysis
    risk_analysis = analyze_risks(full_text)
    
    return {
        "Summary": summary,
        "Risk Analysis": risk_analysis
    }

def compile_final_summary(summaries):
    """Compile the final formatted summary."""
    header = "=" * 60 + "\n"
    header += "📄 GENAI LEGAL ASSISTANT ANALYSIS\n"
    header += "=" * 60 + "\n\n"
    
    formatted_sections = []
    
    for section_name, content in summaries.items():
        section_header = f"📋 {section_name.upper()}\n"
        section_header += "-" * (len(section_name) + 4) + "\n"
        formatted_section = section_header + content + "\n"
        formatted_sections.append(formatted_section)
    
    footer = "\n" + "=" * 60 + "\n"
    footer += "⚠️  IMPORTANT DISCLAIMER\n"
    footer += "=" * 60 + "\n"
    footer += "This analysis was generated by AI for informational purposes only.\n"
    footer += "It should not be considered as legal advice.\n"
    footer += "Please consult with qualified legal professionals for important decisions.\n"
    footer += "Always refer to the original document for complete terms.\n"
    
    final_summary = header + "\n\n".join(formatted_sections) + footer
    return final_summary

def clean_text_for_pdf(text):
    """Clean text for PDF compatibility."""
    return text.encode('latin-1', 'replace').decode('latin-1')

def save_summary_as_pdf(summary, output_path="static/summary_output.pdf"):
    """Create a professionally formatted PDF."""
    os.makedirs("static", exist_ok=True)
    
    summary = clean_text_for_pdf(summary)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add header
    pdf.set_font("Arial", style="B", size=16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "GenAI Legal Assistant Analysis", ln=True, align="C")
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
        
        elif line.startswith('**') and line.endswith('**'):
            # Bold headers
            pdf.set_font("Arial", style="B", size=11)
            pdf.set_text_color(0, 51, 102)
            clean_line = line.replace('**', '').encode('ascii', 'ignore').decode('ascii')
            pdf.cell(0, 6, clean_line, ln=True)
            pdf.ln(1)
        
        elif line.startswith('•'):
            # Bullet points
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0, 0, 0)
            clean_line = line.encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 5, clean_line)
            pdf.ln(1)
        
        elif line.startswith('-'):
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 4, line, ln=True)
            pdf.ln(1)
        
        elif line.startswith('⚠️') or line.startswith('🚨') or line.startswith('ℹ️'):
            pdf.set_font("Arial", style="B", size=10)
            pdf.set_text_color(204, 102, 0)
            clean_line = line.encode('ascii', 'ignore').decode('ascii')
            pdf.multi_cell(0, 5, clean_line)
            pdf.ln(2)
        
        else:
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 5, line, align="J")
            pdf.ln(1)
    
    # Add footer
    pdf.ln(10)
    pdf.set_font("Arial", style="I", size=9)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4, "This analysis was generated using Google's Gemini AI. Please consult legal professionals for important decisions.")
    
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