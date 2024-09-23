import json
import requests
import time
import logging

BASE_URL = 'http://52.56.37.226:3378'
DETECTION_URL = f'{BASE_URL}/detection'
GEOPOSITION_URL = f'{BASE_URL}/geoposition'
HEARTBEAT_URL = f'{BASE_URL}/heartbeat'

# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

DRONE_MODELS = {
    1: "Inspire 1", 2: "Phantom 3 Series", 3: "Phantom 3 Series Pro",
    4: "Phantom 3 Std", 5: "M100", 6: "ACEONE", 7: "WKM", 8: "NAZA",
    9: "A2", 10: "A3", 11: "Phantom 4", 12: "MG1", 14: "M600",
    15: "Phantom 3 4k", 16: "Mavic Pro", 17: "Inspire 2", 18: "Phantom 4 Pro",
    20: "N2", 21: "Spark", 23: "M600 Pro", 24: "Mavic Air", 25: "M200",
    26: "Phantom 4 Series", 27: "Phantom 4 Adv", 28: "M210", 30: "M210RTK",
    31: "A3_AG", 32: "MG2", 34: "MG1A", 35: "Phantom 4 RTK",
    36: "Phantom 4 Pro V2.0", 38: "MG1P", 40: "MG1P-RTK", 41: "Mavic 2",
    44: "M200 V2 Series", 51: "Mavic 2 Enterprise", 53: "Mavic Mini",
    58: "Mavic Air 2", 59: "P4M", 60: "M300 RTK", 61: "FPV",
    63: "Mini 2", 64: "AGRAS T10", 65: "AGRAS T30", 66: "Air 2S",
    67: "M30", 68: "Mavic 3", 69: "Mavic 2 Enterprise Advanced", 70: "Mavic SE",
    73: "Mini 3 Pro", 75: "Avata", 76: "Inspire 3", 77: "Mavic 3 Enterprise E/T/M",
    78: "Flycart 30", 82: "AGRAS T25", 83: "AGRAS T50", 84: "Mavic 3 Pro",
    86: "Mavic 3 Classic", 87: "Mini 3", 88: "Mini 2 SE", 89: "M350 RTK",
    90: "Air 3", 91: "Matrice 3D/3TD", 93: "Mini4 Pro", 95: "T60",
    96: "T25P", 240: "YUNEEC H480",
}

def get_drone_model(drone_id):
    return DRONE_MODELS.get(drone_id, f'Unknown{drone_id}')

def send_request(url, data):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info(f"Successfully sent data to {url}! Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending data to {url}: {e}")

def send_detections(aeroscope_serial_number, serial, drone_latitude, drone_longitude, baro_height, 
                    app_gps_latitude, app_gps_longitude, home_latitude, home_longitude, 
                    vx_north_speed, vz_rise_speed, uuid, model):
    output = {
        "sensor-id": str(aeroscope_serial_number),
        "time": int(time.time() * 1000),
        "position": {
            "latitude": drone_latitude,
            "longitude": drone_longitude,
            "altitude": baro_height,
            "accuracy": 1,
        },
        "metadata": [
            {"key": "icao", "val": serial, "type": "primary"},
            {"key": "registration", "val": serial, "type": "primary"},
            {"key": "home_lat", "val": str(home_latitude)},
            {"key": "home_lng", "val": str(home_longitude)},
            {"key": "speed", "val": str(vx_north_speed)},
            {"key": "vspeed", "val": str(vz_rise_speed)},
            {"key": "uuid", "val": uuid},
            {"key": "manufacturer", "val": "DJI"},
            {"key": "model", "val": get_drone_model(int(model))},
        ]
    }
    send_request(DETECTION_URL, output)

def send_geoposition(aeroscope_serial_number, sensor_lat, sensor_lng):
    output = {
        "sensor-id": str(aeroscope_serial_number),
        "time": int(time.time() * 1000),
        "position": {
            "latitude": sensor_lat,
            "longitude": sensor_lng,
            "altitude": 0,
            "accuracy": 0,
            "speed-vertical": 0,
            "speed-horizontal": 0,
            "bearing": 0
        }
    }
    send_request(GEOPOSITION_URL, output)

def send_heartbeat(aeroscope_serial_number):
    heartbeat_json = {
        "time": int(time.time() * 1000),
        "sensor-id": str(aeroscope_serial_number),
    }
    send_request(HEARTBEAT_URL, heartbeat_json)
