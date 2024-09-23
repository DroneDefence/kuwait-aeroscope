import json
import socketserver
import argparse
import logging
import signal
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from aerotrackerSend import send_detections, send_geoposition, send_heartbeat

# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

class MyTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        buffer = ""
        while True:
            data = self.rfile.readline().strip()
            if not data:
                break
            buffer += data.decode('utf-8')
            while buffer:
                try:
                    obj, idx = json.JSONDecoder().raw_decode(buffer)
                    logging.info(f"Raw JSON data: {data.decode('utf-8')}")
                    buffer = buffer[idx:].strip()  # Remove parsed object from buffer
                    self.process_json_object(obj)
                    
                except json.JSONDecodeError:
                    break  # Wait for more data to be read
                except Exception as e:
                    logging.error(f"Error processing data: {e}")
                    buffer = ""  # Clear buffer in case of a non-JSON error

    def process_json_object(self, obj):
        try:
            # Log the full object as a JSON string
            logging.info(f"Received JSON object: {json.dumps(obj, indent=2)}")
            
            # Extract values from the JSON and assign them to variables
            serial = obj.get("SERIAL")
            drone_latitude = obj.get("LATITUDE")
            drone_longitude = obj.get("LONGITUDE")
            app_gps_latitude = obj.get("APP_GPS_LATITUDE")
            app_gps_longitude = obj.get("APP_GPS_LONGITUDE")
            home_longitude = obj.get("HOME_LONGITUDE")
            home_latitude = obj.get("HOME_LATITUDE")
            product_type = obj.get("PRODUCT_TYPE")
            status_info = obj.get("STATUS_INFO")
            vx_north_speed = obj.get("VX_NORTH_SPEED")
            vy_east_speed = obj.get("VY_EAST_SPEED")
            vz_rise_speed = obj.get("VZ_RISE_SPEED")
            yaw = obj.get("YAW")
            abs_gps_height = obj.get("ABS_GPS_HEIGHT")
            baro_height = obj.get("BARO_HEIGHT")
            sequence_number = obj.get("SEQUENCE_NUMBER")
            uuid = obj.get("UUID")
            model = obj.get("PRODUCT_TYPE")
            timestamp = obj.get("TIMESTAMP")
            aeroscope_serial_number = obj.get("AEROSCOPE_SERIAL_NUMBER")
            sensor_lat = obj.get("LOCATION_LATITUDE")
            sensor_lng = obj.get("LOCATION_LONGITUDE")
            serial_number = obj.get("SERIAL_NUMBER")

            # Send the drone data
            if drone_latitude is not None and drone_longitude is not None:
                send_detections(
                    aeroscope_serial_number, drone_latitude, drone_longitude, baro_height, 
                    app_gps_latitude, app_gps_longitude, home_latitude, home_longitude, 
                    vx_north_speed, vz_rise_speed, uuid, model
                )
            
            send_geoposition(serial_number, sensor_lat, sensor_lng)
            send_heartbeat(serial_number)

        except Exception as e:
            logging.error(f"Error processing JSON object: {e}")

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Server is running")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found")

def start_http_server(bind, port):
    http_server = HTTPServer((bind, port), StatusHandler)
    logging.info(f"Starting HTTP server on {bind}:{port}")
    http_server.serve_forever()

def signal_handler(sig, frame):
    logging.info("Shutting down the server...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description='Process JSON data from the integration engine.')
    parser.add_argument('--bind', default='0.0.0.0', help='Interface to bind to. Default is 0.0.0.0')
    parser.add_argument('--port', default='3333', help='Port to listen to. Default is 3333.')
    args = parser.parse_args()

    # Start the TCP server in a separate thread
    tcp_server_thread = Thread(target=lambda: socketserver.TCPServer((args.bind, int(args.port)), MyTCPHandler).serve_forever())
    tcp_server_thread.start()

    # Start the HTTP server for status checks
    status_port = int(args.port) + 1  # Use a port one higher than the main port
    start_http_server(args.bind, status_port)
