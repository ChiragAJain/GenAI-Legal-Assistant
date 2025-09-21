from flask import Flask, request, jsonify, send_file, render_template
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global variables to store document text for Q&A
current_document_text = ""
current_document_name = ""

try:
    # Try to import the GenAI-powered version first
    from summariser_genai import extract_text_from_pdf, extract_text_from_txt, extract_text_from_docx, split_into_sections, summarize_sections, compile_final_summary, save_summary_as_pdf, store_feedback, answer_question
    AI_MODE = "GenAI"
    print(" GenAI mode loaded successfully")
except ImportError as e:
    print(f" GenAI mode failed to load: {e}")
    try:
        # Fallback to the full AI-powered version
        from summariser import extract_text_from_pdf, extract_text_from_txt, extract_text_from_docx, split_into_sections, summarize_sections, compile_final_summary, save_summary_as_pdf, store_feedback
        AI_MODE = "AI"
        print(" AI mode loaded successfully")
        # Add dummy answer_question function for compatibility
        def answer_question(text, question):
            return "Q&A feature requires GenAI mode. Please set GEMINI_API_KEY environment variable."
    except ImportError as e2:
        # Final fallback to lightweight version
        print(f" AI mode failed to load: {e2}")
        try:
            from summariser_lite import extract_text_from_pdf, extract_text_from_txt, extract_text_from_docx, split_into_sections, summarize_sections, compile_final_summary, save_summary_as_pdf, store_feedback
            AI_MODE = "Lite"
            print(" Lite mode loaded successfully")
            # Add dummy answer_question function for compatibility
            def answer_question(text, question):
                return "Q&A feature requires GenAI mode. Please set GEMINI_API_KEY environment variable."
        except ImportError as e3:
            print(f" All modes failed to load: {e3}")
            raise

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # Set file size limit to 8MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'  # Switch to SQLite

@app.route('/')
def index():
    return render_template('index.html', ai_mode=AI_MODE)

@app.route('/health')
def health_check():
    """Health check endpoint for deployment."""
    return jsonify({"status": "healthy", "mode": AI_MODE}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_document_text, current_document_name
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = f"temp_{file.filename}"
    file.save(file_path)

    # Get optional custom summary length parameters from the request
    custom_min_length = int(request.form.get("min_length", 150))
    custom_max_length = int(request.form.get("max_length", 300))

    try:
        # Extract text based on file type
        if file.filename.endswith('.txt'):
            text = extract_text_from_txt(file_path)
        elif file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            os.remove(file_path)
            return jsonify({"error": "Unsupported file type"}), 400

        # Store document text for Q&A functionality
        current_document_text = text
        current_document_name = file.filename

        # Summarize sections with custom length
        sections = split_into_sections(text)
        section_summaries = summarize_sections(sections, min_length=custom_min_length, max_length=custom_max_length)
        final_summary = compile_final_summary(section_summaries)

        # Save summary as PDF
        pdf_path = "static/summary_output.pdf"
        save_summary_as_pdf(final_summary, output_path=pdf_path)

        # Cleanup temporary file
        os.remove(file_path)

        # Respond with summary and download link
        return jsonify({
            "summary": final_summary,
            "download_link": f"/download/summary_output.pdf",
            "has_document": True,
            "document_name": file.filename
        })

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    global current_document_text, current_document_name
    
    data = request.json
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Get optional custom summary length parameters
    custom_min_length = int(data.get("min_length", 150))
    custom_max_length = int(data.get("max_length", 300))
    
    try:
        # Store document text for Q&A functionality
        current_document_text = text
        current_document_name = "Pasted Text"
        
        # Process the text directly
        sections = split_into_sections(text)
        section_summaries = summarize_sections(sections, min_length=custom_min_length, max_length=custom_max_length)
        final_summary = compile_final_summary(section_summaries)
        
        # Save summary as PDF
        pdf_path = "static/summary_output.pdf"
        save_summary_as_pdf(final_summary, output_path=pdf_path)
        
        # Respond with summary and download link
        return jsonify({
            "summary": final_summary,
            "download_link": f"/download/summary_output.pdf",
            "has_document": True,
            "document_name": "Pasted Text"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(f"static/{filename}", as_attachment=True)

# New Q&A endpoint
@app.route('/ask', methods=['POST'])
def ask_question():
    global current_document_text, current_document_name
    
    if not current_document_text:
        return jsonify({"error": "No document uploaded. Please upload a document first."}), 400
    
    data = request.json
    question = data.get("question", "").strip()
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        answer = answer_question(current_document_text, question)
        return jsonify({
            "answer": answer,
            "question": question,
            "document_name": current_document_name
        })
    except Exception as e:
        return jsonify({"error": f"Failed to answer question: {str(e)}"}), 500

@app.route('/test-formatting', methods=['GET'])
def test_formatting():
    """Test endpoint to verify bullet point formatting works correctly."""
    test_content = """**DOCUMENT SUMMARY**

**Key Points:**
* This is the first key point about the document
* This is the second key point with more details
* This is the third key point explaining important aspects
* This is the fourth key point about user responsibilities
* This is the fifth key point about terms and conditions

**Your Rights:**
* You have the right to access your data
* You have the right to request corrections
* You have the right to delete your account

**Your Obligations:**
* You must provide accurate information
* You must comply with the terms of service
* You must not misuse the platform

**RISK ANALYSIS**

**HIGH RISK:**
* Automatic renewal clauses that are difficult to cancel
* Broad liability limitations that favor the company

**MEDIUM RISK:**
* Data retention periods that may be excessive
* Third-party data sharing without clear consent

**POINTS TO NOTE:**
* Terms may change with limited notice
* Dispute resolution may be limited to arbitration"""

    try:
        # Test the formatting functions
        from summariser_genai import format_content_for_display, clean_text_for_pdf, preprocess_text_for_pdf
        
        formatted_content = format_content_for_display(test_content)
        cleaned_content = clean_text_for_pdf(formatted_content)
        preprocessed_content = preprocess_text_for_pdf(cleaned_content)
        
        return jsonify({
            "original": test_content,
            "formatted": formatted_content,
            "cleaned": cleaned_content,
            "preprocessed": preprocessed_content,
            "status": "Formatting test completed successfully"
        })
    except Exception as e:
        return jsonify({"error": f"Formatting test failed: {str(e)}"}), 500

# Endpoint to collect user feedback
@app.route('/feedback', methods=['POST'])
def collect_feedback():
    data = request.json
    feedback_text = data.get("feedback")
    if not feedback_text:
        return jsonify({"error": "No feedback provided"}), 400
    
    try:
        store_feedback(feedback_text)
        return jsonify({"status": "Feedback received"})
    except Exception as e:
        return jsonify({"error": f"Failed to save feedback: {str(e)}"}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
