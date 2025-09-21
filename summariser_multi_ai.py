import os
import docx
import json
from PyPDF2 import PdfReader
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

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
    max_chunk_size = 25000
    
    if len(text) <= max_chunk_size:
        return {"Full Document": text}
    
    chunks = {}
    words = text.split()
    chunk_size = max_chunk_size // 4
    
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks[f"Section {i//chunk_size + 1}"] = chunk_text
    
    return chunks

def call_huggingface_api(text, api_key):
    """Call Hugging Face Inference API for text summarization."""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Use a free legal text summarization model
        api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        
        # Truncate text if too long
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        payload = {"inputs": text}
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('summary_text', 'No summary generated')
        
        return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def call_openai_api(text, api_key):
    """Call OpenAI API for text summarization."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        api_url = "https://api.openai.com/v1/chat/completions"
        
        prompt = f"""
        Analyze this legal document and provide a brief summary with:
        1. Key points (3-4 main aspects)
        2. User rights (2-3 rights)
        3. User obligations (2-3 obligations)
        4. Important terms to know
        
        Document: {text[:2000]}...
        
        Keep it concise and in plain language.
        """
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        
        return f"OpenAI API Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def generate_ai_summary(document_text):
    """Try multiple AI APIs in order of preference."""
    
    # Try Gemini first (if available)
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key and gemini_key != 'your-gemini-api-key-here':
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            # Try Gemini 2.0 Flash-Lite first (best quotas)
            model_names = [
                'gemini-2.0-flash-lite',
                'models/gemini-2.0-flash-lite',
                'gemini-1.5-flash-8b',
                'gemini-1.5-flash'
            ]
            
            model = None
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    break
                except:
                    continue
            
            if not model:
                model = genai.GenerativeModel('gemini-1.5-flash')  # Final fallback
            
            prompt = f"""
            Analyze this legal document and provide a summary with:
            
            **Key Points:**
            * Point 1: Brief description
            * Point 2: Brief description
            * Point 3: Brief description
            
            **Your Rights:**
            * Right 1: What you can do
            * Right 2: What you can expect
            
            **Your Obligations:**
            * Obligation 1: What you must do
            * Obligation 2: What you must provide
            
            Document: {document_text[:3000]}
            """
            
            response = model.generate_content(prompt)
            if response.text:
                return response.text
        except Exception as e:
            print(f"Gemini failed: {e}")
    
    # Try OpenAI API (if available)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        result = call_openai_api(document_text, openai_key)
        if not result.startswith('Error') and not result.startswith('OpenAI API Error'):
            return result
    
    # Try Hugging Face API (if available)
    hf_key = os.getenv('HUGGINGFACE_API_KEY')
    if hf_key:
        result = call_huggingface_api(document_text, hf_key)
        if not result.startswith('Error') and not result.startswith('API Error'):
            return f"""
            **Document Summary:**
            {result}
            
            **Note:** This is a basic AI summary. For detailed analysis including rights, obligations, and risk assessment, please configure a more advanced AI API key.
            """
    
    # Fallback to rule-based summary
    return generate_rule_based_summary(document_text)

def generate_rule_based_summary(text):
    """Generate a rule-based summary as final fallback."""
    sentences = text.split('.')[:10]  # Take first 10 sentences
    important_keywords = ['shall', 'must', 'required', 'prohibited', 'liable', 'responsible', 'rights', 'obligations']
    
    key_sentences = []
    for sentence in sentences:
        if any(keyword.lower() in sentence.lower() for keyword in important_keywords):
            key_sentences.append(sentence.strip())
    
    if not key_sentences:
        key_sentences = sentences[:5]  # Take first 5 if no keywords found
    
    summary = """
**Document Summary (Rule-Based Analysis):**

**Key Points:**
"""
    
    for i, sentence in enumerate(key_sentences[:3], 1):
        if sentence:
            summary += f"* Point {i}: {sentence}.\n"
    
    summary += """
**Important Note:**
This is a basic rule-based analysis. For advanced AI-powered analysis with risk assessment and interactive Q&A, please configure an AI API key (Gemini, OpenAI, or Hugging Face).
"""
    
    return summary

def summarize_sections(sections, min_length=150, max_length=300):
    """Process sections and generate analysis."""
    if not sections:
        return {}
    
    full_text = "\n\n".join(sections.values())
    summary = generate_ai_summary(full_text)
    
    return {
        "Document Analysis": summary,
        "Risk Assessment": "Risk analysis requires advanced AI API. Currently using fallback mode."
    }

def answer_question(document_text, user_question):
    """Answer questions about the document."""
    return "Interactive Q&A requires an AI API key. Please configure Gemini, OpenAI, or Hugging Face API access."

def compile_final_summary(summaries):
    """Compile the final formatted summary."""
    header = "=" * 60 + "\n"
    header += "LEGAL DOCUMENT ANALYSIS\n"
    header += "=" * 60 + "\n\n"
    
    content_parts = []
    
    for section_name, content in summaries.items():
        if content:
            content_parts.append(content)
    
    if not content_parts:
        return "Error: No content was generated. Please check your configuration."
    
    footer = "\n\n" + "=" * 60 + "\n"
    footer += "IMPORTANT DISCLAIMER\n"
    footer += "=" * 60 + "\n"
    footer += "This analysis was generated for informational purposes only.\n"
    footer += "It should not be considered as legal advice.\n"
    footer += "Please consult with qualified legal professionals for important decisions.\n"
    
    final_summary = header + "\n\n".join(content_parts) + footer
    return final_summary

def clean_text_for_pdf(text):
    """Clean text for PDF compatibility."""
    unicode_replacements = {
        '•': '* ',
        '–': '-',
        '—': '--',
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"',
        '…': '...',
    }
    
    for unicode_char, ascii_replacement in unicode_replacements.items():
        text = text.replace(unicode_char, ascii_replacement)
    
    try:
        text.encode('latin-1')
        return text
    except UnicodeEncodeError:
        return text.encode('latin-1', 'replace').decode('latin-1')

def save_summary_as_pdf(summary, output_path="static/summary_output.pdf"):
    """Create a PDF with the summary."""
    os.makedirs("static", exist_ok=True)
    
    summary = clean_text_for_pdf(summary)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add header
    pdf.set_font("Arial", style="B", size=16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "Legal Document Analysis", ln=True, align="C")
    pdf.ln(5)
    
    # Add generation date
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ln=True, align="C")
    pdf.ln(10)
    
    # Process content
    lines = summary.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
        
        pdf.set_text_color(0, 0, 0)
        
        if line.startswith('=') and line.endswith('='):
            header_text = line.replace('=', '').strip()
            if header_text:
                pdf.set_font("Arial", style="B", size=14)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 8, header_text, ln=True, align="C")
                pdf.ln(3)
        
        elif line.startswith('**') and line.endswith('**'):
            header_text = line.replace('**', '').strip()
            pdf.set_font("Arial", style="B", size=12)
            pdf.set_text_color(0, 102, 51)
            pdf.cell(0, 7, header_text, ln=True)
            pdf.ln(2)
        
        elif line.startswith('* '):
            bullet_text = line[2:].strip()
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(5, 6, chr(149), ln=False)
            pdf.multi_cell(0, 6, bullet_text)
            pdf.ln(1)
        
        else:
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, line)
            pdf.ln(1)
    
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