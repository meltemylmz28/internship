from flask import Flask, render_template, request, jsonify
import os
from utils import karne_sistemine_yukle

# Bu dosyanın (app.py) bulunduğu klasörün tam yolunu buluyoruz
current_dir = os.path.dirname(os.path.abspath(__file__))

# Flask'a templates ve static klasörlerinin tam yerini açık açık söylüyoruz
app = Flask(
    __name__,
    template_folder=os.path.join(current_dir, 'templates'),
    static_folder=os.path.join(current_dir, 'static')
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/karne-oku/', methods=['POST'])
def karne_oku():
    if 'karne_dosyasi' not in request.files:
        return jsonify({"status": "error", "message": "Dosya seçilmedi!"})
        
    dosya = request.files['karne_dosyasi']
    if dosya.filename == '':
        return jsonify({"status": "error", "message": "Boş dosya gönderildi!"})

    # Geçici dosyayı app.py ile aynı klasöre kaydet
    gecici_yol = os.path.join(current_dir, f"gecici_{dosya.filename}")
    dosya.save(gecici_yol)
    
    try:
        okunan_veri = karne_sistemine_yukle(gecici_yol)
        
        if os.path.exists(gecici_yol):
            os.remove(gecici_yol)
            
        return jsonify({"status": "success", "data": okunan_veri})
        
    except Exception as e:
        if os.path.exists(gecici_yol):
            os.remove(gecici_yol)
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=8000)