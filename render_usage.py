import os
import logging
from flask import Flask
import configparser
from datetime import datetime

# Change the current directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load configurations from config.ini file
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'config.ini'))

USE_RENDER_WEB_SERVICE = config['RENDER'].get('USE_RENDER_WEB_SERVICE', 'NO').upper() == 'YES'
RENDER_PORT = int(config['RENDER'].get('RENDER_PORT', 8080))  # Default port is 8080

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)

if USE_RENDER_WEB_SERVICE:
    app = Flask(__name__)

    @app.route('/')
    def health_check():
        return "The re-stake service is running!"

    @app.route('/status')
    def status():
        return {"status": "Running", "timestamp": datetime.utcnow().isoformat()}

    if __name__ == "__main__":
        logging.info(f"Render Web Service enabled on port {RENDER_PORT}.")
        app.run(host='0.0.0.0', port=RENDER_PORT, use_reloader=False, debug=False)
else:
    logging.info("Render Web Service disabled. No action will be taken.")