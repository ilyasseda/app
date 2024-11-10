import os
import sys
from pathlib import Path
from kerykeion import AstrologicalSubject, Report
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import pytz

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Swiss Ephemeris Path
sweph_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1Kerykeion", "kerykeion", "sweph")
os.environ["SWISSEPH_PATH"] = sweph_path

print(f"Swiss Ephemeris dosyalarının konumu: {sweph_path}")

# Output Directory
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

def serialize_house(house_obj):
    """Helper function to serialize house data"""
    if not house_obj:
        return None
    return {
        'name': str(house_obj.get('name', '')),
        'sign': str(house_obj.get('sign', '')),
        'position': float(house_obj.get('position', 0)),  # Changed 'pos' to 'position'
        'abs_position': float(house_obj.get('abs_position', 0)),
        'quality': str(house_obj.get('quality', '')),
        'element': str(house_obj.get('element', ''))
    }

def serialize_planet(planet_obj):
    """Helper function to serialize planet data"""
    if not planet_obj:
        return None
    return {
        'name': str(planet_obj.get('name', '')),
        'sign': str(planet_obj.get('sign', '')),
        'position': float(planet_obj.get('position', 0)),
        'house': str(planet_obj.get('house', '')),
        'quality': str(planet_obj.get('quality', '')),
        'element': str(planet_obj.get('element', ''))
    }

def get_timezone_for_coordinates(lat, lng):
    """Helper function to determine timezone from coordinates"""
    try:
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=float(lat), lng=float(lng))
        return timezone_str or "UTC"
    except Exception as e:
        logging.exception("Timezone belirlenirken hata oluştu:")
        return "UTC"

@app.route('/calculate_chart', methods=['POST'])
def calculate_chart():
    try:
        data = request.json

        # Get timezone from coordinates or use provided timezone
        timezone = data.get('tz_str') or get_timezone_for_coordinates(
            data.get('lat'), 
            data.get('lng')
        )

        # Create astrological subject
        subject = AstrologicalSubject(
            name=data.get('name'),
            year=data.get('year'),
            month=data.get('month'),
            day=data.get('day'),
            hour=data.get('hour'),
            minute=data.get('minute'),
            lng=data.get('lng'),
            lat=data.get('lat'),
            tz_str=timezone
        )

        # Define the order for houses and planets
        houses_order = [
            'first_house', 'second_house', 'third_house', 'fourth_house',
            'fifth_house', 'sixth_house', 'seventh_house', 'eighth_house',
            'ninth_house', 'tenth_house', 'eleventh_house', 'twelfth_house'
        ]

        planets_order = [
            'sun', 'moon', 'mercury', 'venus', 'mars',
            'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'
        ]

        # Get houses data in order
        houses_data = []
        for house_key in houses_order:
            house = serialize_house(getattr(subject, house_key))
            if house:
                house['house'] = house_key  # Add house key for formatting
                houses_data.append(house)

        # Get planets data in order
        planets_data = []
        for planet_key in planets_order:
            planet = serialize_planet(getattr(subject, planet_key))
            if planet:
                planets_data.append(planet)

        # Create report
        report = Report(subject)
        report_text = report.get_full_report()

        # Return complete data
        return jsonify({
            'report': report_text,
            'houses': houses_data,
            'planets': planets_data,
            'timezone_used': timezone,
            'coordinates': {
                'latitude': data.get('lat'),
                'longitude': data.get('lng')
            }
        })

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
