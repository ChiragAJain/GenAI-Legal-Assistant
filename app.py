from flask import Flask, request, jsonify, send_file, render_template
import os

try:
    # Try to import the full AI-powered version
    from summariser import extract_text_from_pdf, extract_text_from_txt, extract_text_from_docx, split_into_sections, summarize_sections, compile_final_summary, save_summary_as_pdf, store_feedback
    AI_MODE = True
    print("✅ AI mode loaded successfully")
except ImportError as e:
    # Fallback to lightweight version for deployment
    print(f"⚠️ AI mode failed to load: {e}")
    try:
        from summariser_lite import extract_text_from_pdf, extract_text_from_txt, extract_text_from_docx, split_into_sections, summarize_sections, compile_final_summary, save_summary_as_pdf, store_feedback
        AI_MODE = False
        print("✅ Lite mode loaded successfully")
    except ImportError as e2:
        print(f"❌ Both modes failed to load: {e2}")
        raise

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # Set file size limit to 8MB

@app.route('/')
def index():
    return render_template('index.html', ai_mode=AI_MODE)

@app.route('/health')
def health_check():
    """Health check endpoint for Railway deployment."""
    return jsonify({"status": "healthy", "mode": "AI" if AI_MODE else "Lite"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
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
            "download_link": f"/download/summary_output.pdf"
        })

    except Exception as e:
        os.remove(file_path)
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(f"static/{filename}", as_attachment=True)

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
    app.run(host='0.0.0.0', port=port, debug=False)
