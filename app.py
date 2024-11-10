import os
import sys
from pathlib import Path
from kerykeion import AstrologicalSubject, Report
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Flask uygulamasını oluştur
app = Flask(__name__)
CORS(app)

# Logging ayarları
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Swiss Ephemeris dosyalarının yolu
sweph_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1Kerykeion", "kerykeion", "sweph")
os.environ["SWISSEPH_PATH"] = sweph_path

print(f"Swiss Ephemeris dosyalarının konumu: {sweph_path}")

# Çıktı dizini
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

@app.route('/calculate_chart', methods=['POST'])
def calculate_chart():
    try:
        data = request.json
        name = data.get('name')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        hour = data.get('hour')
        minute = data.get('minute')
        lat = data.get('lat')
        lng = data.get('lng')

        # AstrologicalSubject oluştur
        # Doğru sıralama: (name, year, month, day, hour, minute, lng, lat, tz_str)
        subject = AstrologicalSubject(
            name,
            year,
            month,
            day,
            hour,
            minute,
            lng=lng,  # Longitude direkt olarak verilmeli
            lat=lat,  # Latitude direkt olarak verilmeli
            tz_str="Europe/Istanbul",
            houses_system="P"  # Placidus ev sistemi
        )

        # Rapor oluştur
        report = Report(subject)
        report_text = report.get_full_report()

        # Chart verilerini hazırla
        chart_data = {
            'report': report_text,
            'coordinates': {
                'lat': lat,
                'lng': lng
            }
        }

        return jsonify(chart_data)

    except Exception as e:
        logging.exception("Bir hata oluştu:")
        return jsonify({'error': str(e)}), 500

@app.route('/version', methods=['GET'])
def get_version():
    try:
        import kerykeion
        kerykeion_version = kerykeion.__version__
    except AttributeError:
        kerykeion_version = "Belirlenemedi"

    return jsonify({
        'kerykeion_version': kerykeion_version,
        'python_version': sys.version
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)