from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename

try:
    from utils import process_excel_file
except ImportError:
    from pdf_okuyucu.utils import process_excel_file

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'xml', 'pdf', 'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tif', 'tiff', 'doc', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Dosya seçilmedi."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Boş dosya ismi."}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            result = process_excel_file(file_path)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

        return jsonify(result)

    return jsonify({"error": "Geçersiz dosya uzantısı. Desteklenen formatlar: Excel, CSV, XML, PDF, görsel, Word ve TXT."}), 400


if __name__ == '__main__':
    app.run(debug=True)