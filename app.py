import os
import sys
from pathlib import Path
from kerykeion import AstrologicalSubject, Report
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

sweph_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1Kerykeion", "kerykeion", "sweph")
os.environ["SWISSEPH_PATH"] = sweph_path

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
        city = data.get('city', 'Unknown')
        nation = data.get('nation', 'Unknown')
        lat = data.get('lat')
        lng = data.get('lng')
        timezone = data.get('timezone', 'UTC')  # Varsayılan olarak UTC kullan

        # AstrologicalSubject oluştur
        subject = AstrologicalSubject(
            name, year, month, day, hour, minute,
            city=city, nation=nation,
            lat=lat, lng=lng,
            tz_str=timezone,  # Dinamik timezone kullan
            houses_system="P"  # Placidus ev sistemi
        )

        # Rapor oluştur
        report = Report(subject)
        report_text = report.get_full_report()

        # Chart verilerini hazırla
        chart_data = {
            'report': report_text,
            'houses': {},
            'planets': {},
            'coordinates': {
                'lat': lat,
                'lng': lng
            },
            'timezone': timezone,
            'location': f"{city}, {nation}"
        }

        # Evleri ekle
        for house_num in range(1, 13):
            house_obj = getattr(subject, f'house_{house_num}')
            chart_data['houses'][f'house_{house_num}'] = {
                'sign': house_obj['sign'],
                'position': house_obj['pos'],
                'absolute_position': house_obj['abs_pos']
            }

        # Gezegenleri ekle
        for planet in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 
                      'saturn', 'uranus', 'neptune', 'pluto']:
            planet_obj = getattr(subject, planet)
            chart_data['planets'][planet] = {
                'sign': planet_obj['sign'],
                'position': planet_obj['pos'],
                'house': planet_obj['house'],
                'retrograde': planet_obj['retrograde']
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