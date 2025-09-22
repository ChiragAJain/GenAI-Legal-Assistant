import os
import docx
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY and GEMINI_API_KEY != 'your-gemini-api-key-here':
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try different model names in order of preference (prioritizing 2.0 Flash-Lite)
        model_names = [
            'gemini-2.0-flash-lite',    # Gemini 2.0 Flash-Lite (best quotas: 30 RPM, 1M TPM, 200 RPD)
            'models/gemini-2.0-flash-lite', # With models/ prefix
            'gemini-1.5-flash-8b',      # Gemini 1.5 Flash Lite fallback
            'gemini-1.5-flash',         # Standard Flash
            'models/gemini-1.5-flash-8b', # With models/ prefix
            'models/gemini-1.5-flash',  # With models/ prefix
            'gemini-1.5-pro',          # More capable but lower quotas
            'gemini-pro',              # Legacy name
        ]
        
        model = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # Test the model with a simple prompt
                test_response = model.generate_content("Hello")
                print(f"Using Gemini model: {model_name}")
                break
            except Exception as e:
                print(f"Model {model_name} not available: {str(e)}")
                continue
        
        if not model:
            print("No available Gemini models found. Listing available models...")
            try:
                available_models = genai.list_models()
                print("Available models:")
                for m in available_models:
                    if 'generateContent' in m.supported_generation_methods:
                        print(f"  - {m.name}")
            except Exception as e:
                print(f"Could not list models: {e}")
            model = None
            
    except Exception as e:
        print(f"Failed to configure Gemini API: {e}")
        model = None
else:
    print("GEMINI_API_KEY not found or not configured. GenAI features will not work.")
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
        return "GenAI service unavailable. Please check your GEMINI_API_KEY in the .env file."
    
    # Truncate document if too long (Gemini has input limits)
    max_input_length = 25000  # Conservative limit
    if len(document_text) > max_input_length:
        document_text = document_text[:max_input_length] + "\n\n[Document truncated due to length...]"
    
    prompt = f"""
    Analyze the following legal document and provide a comprehensive summary in exactly this format:

    **DOCUMENT SUMMARY**
    
    **Key Points:**
    * Point 1: Brief description
    * Point 2: Brief description  
    * Point 3: Brief description
    * Point 4: Brief description
    * Point 5: Brief description
    
    **Your Rights:**
    * Right 1: What you can do
    * Right 2: What you can expect
    * Right 3: What protections you have
    
    **Your Obligations:**
    * Obligation 1: What you must do
    * Obligation 2: What you must provide
    * Obligation 3: What you must avoid
    
    **Important Terms:**
    * Term 1: Definition in simple language
    * Term 2: Definition in simple language
    * Term 3: Definition in simple language
    
    Document to analyze:
    {document_text}
    
    FORMATTING RULES:
    - Each bullet point must start on a new line
    - Use exactly "* " (asterisk + space) for bullets
    - Keep each point to 1-2 sentences maximum
    - Use simple, clear language
    - No Unicode symbols or emojis
    - Each section should have 3-5 bullet points
    """
    
    try:
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return "Error: Empty response from Gemini API. The content might have been blocked by safety filters."
    except Exception as e:
        error_msg = str(e)
        
        if "404" in error_msg:
            return "Error: Gemini model not found. Please check if your API key is valid and has access to Gemini models."
        elif "403" in error_msg:
            return "Error: Access denied. Please check your API key permissions."
        elif "quota" in error_msg.lower():
            return "Error: API quota exceeded. Please check your Gemini API usage limits."
        else:
            return f"Error generating summary: {error_msg}"

def answer_question(document_text, user_question):
    """Answer specific questions about the document using Gemini API."""
    if not model:
        return "GenAI service unavailable. Please check your GEMINI_API_KEY in the .env file."
    
    # Truncate document if too long
    max_input_length = 20000  # Leave room for question and instructions
    if len(document_text) > max_input_length:
        document_text = document_text[:max_input_length] + "\n\n[Document truncated...]"
    
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
        if response.text:
            return response.text
        else:
            return "Error: Empty response from Gemini API. The question might have been blocked by safety filters."
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            return "Error: Gemini model not found. Please check your API key configuration."
        elif "403" in error_msg:
            return "Error: Access denied. Please verify your API key permissions."
        else:
            return f"Error answering question: {error_msg}"

def analyze_risks(document_text):
    """Identify potential risks and non-standard clauses using Gemini API."""
    if not model:
        return "GenAI service unavailable. Please check your GEMINI_API_KEY in the .env file."
    
    # Truncate document if too long
    max_input_length = 25000
    if len(document_text) > max_input_length:
        document_text = document_text[:max_input_length] + "\n\n[Document truncated due to length...]"
    
    prompt = f"""
    Analyze the following legal document and identify potentially risky or non-standard clauses for a consumer.
    
    Format your response exactly as:
    
    **RISK ANALYSIS**
    
    **HIGH RISK:**
    * Risk 1: Brief explanation of the concern
    * Risk 2: Brief explanation of the concern
    
    **MEDIUM RISK:**
    * Risk 1: Brief explanation of the concern  
    * Risk 2: Brief explanation of the concern
    
    **POINTS TO NOTE:**
    * Point 1: Important information to be aware of
    * Point 2: Important information to be aware of
    
    Document to analyze:
    {document_text}
    
    Focus on identifying:
    - Unusual liability limitations
    - Broad indemnification clauses
    - Automatic renewals or difficult cancellation
    - Data usage beyond normal expectations
    - Dispute resolution limitations
    - Unusual termination conditions
    
    FORMATTING RULES:
    - Each bullet point must start on a new line
    - Use exactly "* " (asterisk + space) for bullets
    - Keep each point to 1-2 sentences maximum
    - Use simple, clear language
    - No Unicode symbols, emojis, or special characters
    - Each section should have 2-3 bullet points
    """
    
    try:
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return "Error: Empty response from Gemini API. The content might have been blocked by safety filters."
    except Exception as e:
        error_msg = str(e)
        
        if "404" in error_msg:
            return "Error: Gemini model not found. Please check your API key configuration."
        elif "403" in error_msg:
            return "Error: Access denied. Please verify your API key permissions."
        elif "quota" in error_msg.lower():
            return "Error: API quota exceeded. Please check your Gemini API usage limits."
        else:
            return f"Error analyzing risks: {error_msg}"

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
    
    result = {
        "Document Analysis": summary,
        "Risk Assessment": risk_analysis
    }
    
    return result

def compile_final_summary(summaries):
    """Compile the final formatted summary for GenAI responses with proper bullet point handling."""
    header = "=" * 60 + "\n"
    header += "GENAI LEGAL ASSISTANT ANALYSIS\n"
    header += "=" * 60 + "\n\n"
    
    content_parts = []
    
    # Add the main document analysis (contains Key Points, Rights, Obligations, etc.)
    if "Document Analysis" in summaries and summaries["Document Analysis"]:
        summary_content = format_content_for_display(summaries["Document Analysis"])
        content_parts.append(summary_content)
    
    # Add the risk analysis with a clear separator
    if "Risk Assessment" in summaries and summaries["Risk Assessment"]:
        risk_content = format_content_for_display(summaries["Risk Assessment"])
        content_parts.append("\n" + "=" * 60 + "\n")
        content_parts.append(risk_content)
    
    # Fallback: Handle legacy key names for compatibility
    if "Summary" in summaries and summaries["Summary"]:
        summary_content = format_content_for_display(summaries["Summary"])
        content_parts.append(summary_content)
    
    if "Risk Analysis" in summaries and summaries["Risk Analysis"]:
        risk_content = format_content_for_display(summaries["Risk Analysis"])
        content_parts.append("\n" + "=" * 60 + "\n")
        content_parts.append(risk_content)
    
    # Handle any other sections (fallback for compatibility)
    for section_name, content in summaries.items():
        if section_name not in ["Document Analysis", "Risk Assessment", "Summary", "Risk Analysis"]:
            if content:
                section_header = f"\n{section_name.upper()}\n"
                section_header += "-" * len(section_name) + "\n"
                formatted_section = section_header + format_content_for_display(content)
                content_parts.append(formatted_section)
    
    if not content_parts:
        return "Error: No content was generated. Please check your API key and try again."
    
    footer = "\n\n" + "=" * 60 + "\n"
    footer += "IMPORTANT DISCLAIMER\n"
    footer += "=" * 60 + "\n"
    footer += "This analysis was generated by AI for informational purposes only.\n"
    footer += "It should not be considered as legal advice.\n"
    footer += "Please consult with qualified legal professionals for important decisions.\n"
    footer += "Always refer to the original document for complete terms.\n"
    
    final_summary = header + "\n".join(content_parts) + footer
    return final_summary

def format_content_for_display(content):
    """Format content to ensure proper bullet point structure."""
    if not content:
        return content
    
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue
        
        # Handle concatenated bullet points
        if ' * ' in line and not line.startswith('* '):
            # Split on bullet points
            parts = line.split(' * ')
            # Add the first part (might not be a bullet)
            if parts[0].strip():
                formatted_lines.append(parts[0].strip())
            # Add the rest as bullet points
            for part in parts[1:]:
                if part.strip():
                    formatted_lines.append('* ' + part.strip())
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def clean_text_for_pdf(text):
    """Clean text for PDF compatibility by replacing Unicode characters with ASCII equivalents."""
    # Dictionary of Unicode characters to ASCII replacements
    unicode_replacements = {
        '•': '* ',      # Bullet point
        '◦': '- ',      # White bullet
        '▪': '* ',      # Black small square
        '▫': '- ',      # White small square
        '–': '-',       # En dash
        '—': '--',      # Em dash
        ''': "'",       # Left single quotation mark
        ''': "'",       # Right single quotation mark
        '"': '"',       # Left double quotation mark
        '"': '"',       # Right double quotation mark
        '…': '...',     # Horizontal ellipsis
        '©': '(c)',     # Copyright symbol
        '®': '(R)',     # Registered trademark
        '™': '(TM)',    # Trademark symbol
        '°': ' deg',    # Degree symbol
        '§': 'Section', # Section symbol
        '¶': 'Para',    # Paragraph symbol
        '†': '+',       # Dagger
        '‡': '++',      # Double dagger
        '★': '*',       # Black star
        '☆': '*',       # White star
        '✓': 'v',       # Check mark
        '✗': 'x',       # Cross mark
        '→': '->',      # Right arrow
        '←': '<-',      # Left arrow
        '↑': '^',       # Up arrow
        '↓': 'v',       # Down arrow
        '⚠': '!',       # Warning sign
        '⚡': '!',       # High voltage sign
        '🚨': '!!!',    # Police car light
        '📋': '[*]',    # Clipboard
        '🔍': '[?]',    # Magnifying glass
        '📄': '[DOC]',  # Page facing up
        '📝': '[EDIT]', # Memo
        '🔑': '[KEY]',  # Key
        '⭐': '*',      # Star
        '❌': 'X',      # Cross mark
        '✅': 'OK',     # Check mark button
        '⚙': '[GEAR]', # Gear
        '🎯': '[TARGET]', # Direct hit
        '💡': '[IDEA]', # Light bulb
        '🔧': '[TOOL]', # Wrench
        '📊': '[CHART]', # Bar chart
        '🌐': '[WEB]',  # Globe with meridians
        '🏃': '[RUN]',  # Runner
        '🚀': '[ROCKET]', # Rocket
        '✨': '*',      # Sparkles
        '🎉': '[PARTY]', # Party popper
        '🛠': '[TOOLS]', # Hammer and wrench
        '📱': '[MOBILE]', # Mobile phone
        '💻': '[LAPTOP]', # Laptop computer
        '🖥': '[DESKTOP]', # Desktop computer
        '📈': '[UP]',   # Chart increasing
        '📉': '[DOWN]', # Chart decreasing
        '🔒': '[LOCK]', # Lock
        '🔓': '[UNLOCK]', # Unlock
        '🎨': '[ART]',  # Artist palette
        '🔍': '[SEARCH]', # Magnifying glass tilted left
        '📋': '[CLIP]', # Clipboard
        '📄': '[PAGE]', # Page facing up
        '🧠': '[BRAIN]', # Brain
        '🤖': '[BOT]',  # Robot
        '⚡': '[FAST]', # High voltage
        '🔥': '[HOT]',  # Fire
        '❄': '[COLD]', # Snowflake
        '🌟': '[STAR]', # Glowing star
        '💎': '[GEM]',  # Gem stone
        '🏆': '[TROPHY]', # Trophy
        '🎖': '[MEDAL]', # Military medal
        '🏅': '[MEDAL]', # Sports medal
        '🎪': '[CIRCUS]', # Circus tent
        '🎭': '[THEATER]', # Performing arts
        '🎬': '[MOVIE]', # Clapper board
        '🎵': '[MUSIC]', # Musical note
        '🎶': '[MUSIC]', # Multiple musical notes
        '🔊': '[SOUND]', # Speaker high volume
        '🔇': '[MUTE]',  # Speaker with cancellation stroke
        '📢': '[ANNOUNCE]', # Public address loudspeaker
        '📣': '[MEGAPHONE]', # Cheering megaphone
        '📯': '[HORN]',  # Postal horn
        '🔔': '[BELL]',  # Bell
        '🔕': '[NO_BELL]', # Bell with cancellation stroke
        '📞': '[PHONE]', # Telephone receiver
        '📱': '[MOBILE]', # Mobile phone
        '📲': '[CALL]',  # Mobile phone with arrow
        '☎': '[PHONE]', # Telephone
        '📠': '[FAX]',   # Fax machine
        '📧': '[EMAIL]', # E-mail
        '📨': '[INBOX]', # Incoming envelope
        '📩': '[OUTBOX]', # Envelope with arrow
        '📪': '[MAILBOX]', # Closed mailbox with lowered flag
        '📫': '[MAILBOX]', # Closed mailbox with raised flag
        '📬': '[MAILBOX]', # Open mailbox with raised flag
        '📭': '[MAILBOX]', # Open mailbox with lowered flag
        '📮': '[POSTBOX]', # Postbox
        '🗳': '[BALLOT]', # Ballot box with ballot
        '✏': '[PENCIL]', # Pencil
        '✒': '[PEN]',    # Black nib
        '🖋': '[PEN]',   # Fountain pen
        '🖊': '[PEN]',   # Pen
        '🖌': '[BRUSH]', # Paintbrush
        '🖍': '[CRAYON]', # Crayon
        '📝': '[MEMO]',  # Memo
        '💼': '[BRIEFCASE]', # Briefcase
        '📁': '[FOLDER]', # File folder
        '📂': '[OPEN_FOLDER]', # Open file folder
        '🗂': '[DIVIDERS]', # Card index dividers
        '📅': '[CALENDAR]', # Calendar
        '📆': '[CALENDAR]', # Tear-off calendar
        '🗓': '[CALENDAR]', # Spiral calendar
        '📇': '[ROLODEX]', # Card index
        '📈': '[CHART_UP]', # Chart with upwards trend
        '📉': '[CHART_DOWN]', # Chart with downwards trend
        '📊': '[BAR_CHART]', # Bar chart
        '📋': '[CLIPBOARD]', # Clipboard
        '📌': '[PIN]',   # Pushpin
        '📍': '[LOCATION]', # Round pushpin
        '📎': '[CLIP]',  # Paperclip
        '🖇': '[CLIPS]', # Linked paperclips
        '📏': '[RULER]', # Straight ruler
        '📐': '[TRIANGLE]', # Triangular ruler
        '✂': '[SCISSORS]', # Scissors
        '🗃': '[FILE_BOX]', # Card file box
        '🗄': '[CABINET]', # File cabinet
        '🗑': '[TRASH]', # Wastebasket
        '🔒': '[LOCKED]', # Locked
        '🔓': '[UNLOCKED]', # Unlocked
        '🔏': '[LOCKED_PEN]', # Locked with pen
        '🔐': '[LOCKED_KEY]', # Locked with key
        '🔑': '[KEY]',   # Key
        '🗝': '[OLD_KEY]', # Old key
        '🔨': '[HAMMER]', # Hammer
        '⛏': '[PICK]',  # Pick
        '⚒': '[HAMMER_PICK]', # Hammer and pick
        '🛠': '[TOOLS]', # Hammer and wrench
        '🗡': '[SWORD]', # Dagger
        '⚔': '[SWORDS]', # Crossed swords
        '🔫': '[GUN]',   # Pistol
        '🏹': '[BOW]',   # Bow and arrow
        '🛡': '[SHIELD]', # Shield
        '🔧': '[WRENCH]', # Wrench
        '🔩': '[NUT_BOLT]', # Nut and bolt
        '⚙': '[GEAR]',  # Gear
        '🗜': '[CLAMP]', # Compression
        '⚖': '[SCALE]', # Balance scale
        '🔗': '[LINK]',  # Link
        '⛓': '[CHAINS]', # Chains
        '🧰': '[TOOLBOX]', # Toolbox
        '🧲': '[MAGNET]', # Magnet
        '⚗': '[ALEMBIC]', # Alembic
        '🧪': '[TEST_TUBE]', # Test tube
        '🧫': '[PETRI]', # Petri dish
        '🧬': '[DNA]',   # DNA
        '🔬': '[MICROSCOPE]', # Microscope
        '🔭': '[TELESCOPE]', # Telescope
        '📡': '[SATELLITE]', # Satellite antenna
    }
    
    # Replace Unicode characters with ASCII equivalents
    for unicode_char, ascii_replacement in unicode_replacements.items():
        text = text.replace(unicode_char, ascii_replacement)
    
    # Handle any remaining non-ASCII characters by encoding to latin-1 with replacement
    try:
        # First try to encode as latin-1
        text.encode('latin-1')
        return text
    except UnicodeEncodeError:
        # If that fails, replace problematic characters
        return text.encode('latin-1', 'replace').decode('latin-1')

def save_summary_as_pdf(summary, output_path="static/summary_output.pdf"):
    """Create a professionally formatted PDF with proper bullet point handling."""
    os.makedirs("static", exist_ok=True)
    
    # Clean text for PDF compatibility
    summary = clean_text_for_pdf(summary)
    
    # Pre-process the text to ensure proper line breaks and bullet formatting
    summary = preprocess_text_for_pdf(summary)
    
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
    
    # Process content line by line
    lines = summary.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
        
        # Reset text color for each line
        pdf.set_text_color(0, 0, 0)
        
        # Handle different types of content
        if line.startswith('=') and line.endswith('='):
            # Main headers (surrounded by =)
            header_text = line.replace('=', '').strip()
            if header_text:
                pdf.set_font("Arial", style="B", size=14)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 8, header_text, ln=True, align="C")
                pdf.ln(3)
        
        elif line.startswith('**') and line.endswith('**'):
            # Section headers (bold)
            header_text = line.replace('**', '').strip()
            pdf.set_font("Arial", style="B", size=12)
            pdf.set_text_color(0, 102, 51)
            pdf.cell(0, 7, header_text, ln=True)
            pdf.ln(2)
        
        elif line.startswith('* '):
            # Bullet points
            bullet_text = line[2:].strip()  # Remove "* " prefix
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0, 0, 0)
            
            # Add bullet symbol and text
            pdf.cell(5, 6, chr(149), ln=False)  # Bullet character
            pdf.multi_cell(0, 6, bullet_text)
            pdf.ln(1)
        
        elif line.startswith('-'):
            # Separator lines
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 4, line, ln=True)
            pdf.ln(1)
        
        else:
            # Regular text
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, line)
            pdf.ln(1)
    
    # Add footer
    pdf.ln(10)
    pdf.set_font("Arial", style="I", size=9)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4, "This analysis was generated using Google's Gemini AI. Please consult legal professionals for important decisions.")
    
    pdf.output(output_path)

def preprocess_text_for_pdf(text):
    """Preprocess text to ensure proper formatting for PDF generation."""
    
    # Split text into lines
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
        
        # Handle concatenated bullet points (common issue from AI responses)
        if ' * ' in line and not line.startswith('* '):
            # Split on bullet points but preserve the first part
            parts = line.split(' * ')
            processed_lines.append(parts[0])
            for part in parts[1:]:
                if part.strip():
                    processed_lines.append('* ' + part.strip())
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

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

