import os
import shutil
from flask import Flask, request, render_template, send_file, redirect, url_for
from ocr_utils import handle_file, run_ocr
from nlp_utils import extract_columns_and_data
from gemini_utils import analyze_with_gemini
from db_utils import init_db, save_data, get_data_by_id
import io
import sqlite3

app = Flask(__name__)
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    ocr_results = nlp_data = gemini_response = suggestion = file_id = ""

    if request.method == "POST":
        file = request.files['file']
        filename = file.filename.lower()
        if not (filename.endswith('.pdf') or filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))):
            return "❌ Only PDF or image files are allowed."

        try:
            file_ext = os.path.splitext(filename)[1]
            file_bytes = file.read()
            file.stream.seek(0)  # Reset pointer after reading

            image_paths, temp_dir = handle_file(file)
            ocr_results = run_ocr(image_paths)
            nlp_data = extract_columns_and_data(ocr_results)
            gemini_response = analyze_with_gemini(nlp_data)
            suggestion = gemini_response[0]

            # Save to DB
            file_id = save_data(
                file_bytes=file_bytes,
                file_ext=file_ext,
                ocr_results=ocr_results,
                nlp_data=str(nlp_data),
                gemini_response=str(gemini_response)
            )

        finally:
            shutil.rmtree(temp_dir)

        return render_template("result.html",
                               ocr_results=ocr_results,
                               nlp_data=nlp_data,
                               gemini_response=gemini_response,
                               suggestion=suggestion,
                               file_id=file_id,
                               file_url=url_for('view_file', file_id=file_id))

    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        file_id = request.form["file_id"]
        data = get_data_by_id(file_id)
        if data:
            timestamp, file_ext, ocr_results, nlp_data, gemini_response = data
            return render_template("result.html",
                                   file_id=file_id,
                                   file_url=url_for('view_file', file_id=file_id),
                                   ocr_results=ocr_results,
                                   nlp_data=nlp_data,
                                   gemini_response=gemini_response,
                                   suggestion=gemini_response)
        else:
            return "❌ No data found for the provided ID."

    return render_template("search.html")

@app.route("/file/<file_id>")
def view_file(file_id):
    data = get_data_by_id(file_id)
    if data:
        _, file_ext, _, _, _, = data
        with sqlite3.connect("user_data.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file FROM data WHERE id=?", (file_id,))
            file_bytes = cursor.fetchone()[0]
        return send_file(
            io.BytesIO(file_bytes),
            mimetype="application/pdf" if file_ext == ".pdf" else f"image/{file_ext.lstrip('.')}",
            download_name=f"{file_id}{file_ext}"
        )
    return "❌ File not found."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501)
