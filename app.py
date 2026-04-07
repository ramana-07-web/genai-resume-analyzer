from dotenv import load_dotenv
load_dotenv()  # Load .env before anything else

from flask import Flask, request, jsonify, render_template
import os
import uuid

from utils.affinda_parser import parse_resume
from utils.gemini_llm import analyze_resume

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_join(items) -> str:
    return ", ".join([str(x) for x in items if x])


def save_upload(file) -> str:
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(file_path)
    return file_path


# -------------------- HOME --------------------
@app.route("/")
def home():
    return "Gemini Resume Analyzer is running ✅"


# -------------------- UI --------------------
@app.route("/ui")
def ui():
    return render_template("index.html")


# -------------------- UI ANALYSIS --------------------
@app.route("/analyze-ui", methods=["POST"])
def analyze_ui():
    try:
        file = request.files.get("resume")
        job_desc = request.form.get("job_desc", "").strip()

        if not file or not file.filename:
            return "<h3>❌ No file uploaded.</h3>"
        if not allowed_file(file.filename):
            return "<h3>❌ Only PDF files are supported.</h3>"
        if not job_desc:
            return "<h3>❌ Job description is required.</h3>"

        file_path = save_upload(file)

        try:
            parsed_data = parse_resume(file_path)

            if "error" in parsed_data:
                return f"<h3>❌ Parsing Error: {parsed_data['error']}</h3>"

            parse_source = parsed_data.pop("source", "unknown")

            try:
                analysis = analyze_resume(parsed_data, job_desc)
                analysis_source = "Gemini AI"
            except Exception as e:
                analysis = f"Gemini is currently unavailable: {str(e)}"
                analysis_source = "Fallback"

            return f"""
            <div style="text-align:center; margin-top:50px; font-family:'Segoe UI',Arial,sans-serif;">
                <h2>🚀 Resume Analysis Result</h2>
                <p style="color:#888; font-size:13px;">
                    Parsed via: <b>{parse_source}</b> &nbsp;|&nbsp; Analysis via: <b>{analysis_source}</b>
                </p>

                <div style="width:65%; margin:auto; background:#f4f6f8; padding:25px;
                            border-radius:12px; text-align:left; box-shadow:0 2px 8px #ccc;">

                    <h3>📄 Parsed Resume Data</h3>
                    <p><b>Name:</b> {parsed_data.get('name') or '—'}</p>
                    <p><b>Skills:</b> {safe_join(parsed_data.get('skills', [])) or '—'}</p>
                    <p><b>Education:</b> {safe_join(parsed_data.get('education', [])) or '—'}</p>
                    <p><b>Experience:</b> {safe_join(parsed_data.get('experience', [])) or '—'}</p>

                    <hr style="margin:20px 0;">

                    <h3>🤖 AI Analysis</h3>
                    <pre style="white-space:pre-wrap; font-family:inherit; font-size:15px;">{analysis}</pre>
                </div>

                <br>
                <a href="/ui" style="text-decoration:none; font-size:16px;">⬅ Analyze Another Resume</a>
            </div>
            """
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        return f"<h3>❌ Unexpected Error: {str(e)}</h3>"


# -------------------- API --------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("resume")
        job_desc = request.form.get("job_desc", "").strip()

        if not file or not file.filename:
            return jsonify({"error": "No file uploaded"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files are supported"}), 400
        if not job_desc:
            return jsonify({"error": "job_desc is required"}), 400

        file_path = save_upload(file)

        try:
            parsed_data = parse_resume(file_path)

            if "error" in parsed_data:
                return jsonify(parsed_data), 400

            parse_source = parsed_data.pop("source", "unknown")

            try:
                analysis = analyze_resume(parsed_data, job_desc)
                analysis_source = "Gemini"
            except Exception as e:
                app.logger.error(f"Gemini error: {e}")
                analysis = f"Gemini unavailable: {str(e)}"
                analysis_source = "Fallback"

            return jsonify({
                "parsed_data":    parsed_data,
                "analysis":       analysis,
                "parse_source":   parse_source,
                "analysis_source": analysis_source,
            })
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------- RUN --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)