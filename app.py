from flask import Flask, request, jsonify, send_file
from summariser import extract_text_from_pdf, extract_text_from_txt, extract_text_from_docx, split_into_sections, summarize_sections, compile_final_summary, save_summary_as_pdf
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  #Setting the file size to 8MB
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    file_path = f"temp_{file.filename}"
    file.save(file_path)
    try:
        if file.filename.endswith('.txt'):
            text = extract_text_from_txt(file_path)
        elif file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            os.remove(file_path)
            return jsonify({"error": "Unsupported file type"}), 400

        sections = split_into_sections(text)
        section_summaries = summarize_sections(sections)
        final_summary = compile_final_summary(section_summaries)
        pdf_path = "static/summary_output.pdf"
        save_summary_as_pdf(final_summary, output_path=pdf_path)

        # Cleaning up the temporary file
        os.remove(file_path)

        # Returns a JSON response and link to download the PDF
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
