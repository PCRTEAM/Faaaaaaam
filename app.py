from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Hardcode FLASK_SECRET_KEY
app.secret_key = "be371ed4228d5c23ff65bf124e63a479"

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)

# Flask-Limiter setup
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# API endpoint and headers
url = "https://westeros.famapp.in/txn/create/payout/add/"
AUTH_TOKEN = "eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoicGEwWmVNd255eFBKYXB5ZU9udXlkV1J1OEJWbFlMY1l2YkliUC1FOXhkdUo2dzNGbmNOTDFHMlZqVm9ZZWktOGEzRlRaX29tdGFRIn0sImFsZyI6IkVDREgtRVMifQ.._Fz2hxuGqpjf7V1pCeznsA.g4R7FbdRU3R7m1j3bkSyEljVTsqv8lLCEDy4Vsh2-06j1w1lw4f7ME6j6HB_B_8GMV6H63BR2mU-ogNBW1uKIDDiJQFKn4KkmOdbZX_Gr7y6BIty5FwqV6Tx4pk2NVMdl07eNPyLZZExpp9whLOOxrB02fSxMTptvHMYsSAkQaEt1eHaLkERPSj84loywzsFjWSmgYlr9Tt0MaFoB4Va348_ZFs1JI1sDpq9ZEicW2RBnz2vka2tz_zki-5rj7Enhi9HP5xMoo9XOwvmnvZAAQ.tWG08-yG0nr1vF7VKDUUC4zLHbkB3rYegjW47kP5Vk8"

headers = {
    "User-Agent": "A015 | Android 15 | Dalvik/2.1.0 | Tetris | 318D0D6589676E17F88CCE03A86C2591C8EBAFBA | 3.11.5 (Build 525) | 3DB5HIEMMG",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json; charset=UTF-8",
    "x-device-details": "A015 | Android 15 | Dalvik/2.1.0 | Tetris | 318D0D6589676E17F88CCE03A86C2591C8EBAFBA | 3.11.5 (Build 525) | 3DB5HIEMMG",
    "x-app-version": "525",
    "x-platform": "1",
    "device-id": "290db21f38c0907b",
    "authorization": f"Token {AUTH_TOKEN}"
}

# File to store API keys
API_KEYS_FILE = 'api_keys.json'

# Load API keys
def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return []

# Save API keys
def save_api_keys(keys):
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=4)

# Check if API is stopped
STOP_API = False

# Format response with emojis
def format_response(resp_json):
    if not resp_json:
        return "No response received 😕"
    
    output = "🎉 FamUPI Response:\n\n"
    output += f"Add Beneficiary Required: {resp_json.get('add_beneficiary_required', False)} {'✅' if not resp_json.get('add_beneficiary_required') else '❌'}\n"
    output += f"Beneficiary State: {resp_json.get('beneficiary_state', 'N/A')} {'🟢' if resp_json.get('beneficiary_state') == 'active' else '🔴'}\n"
    output += f"Type: {resp_json.get('type', 'N/A')} {'👤' if resp_json.get('type') == 'user' else '🏦'}\n"
    
    user = resp_json.get('user', {})
    output += "\n👤 User Details:\n"
    output += f"  Username: {user.get('display_username', 'N/A')} 😎\n"
    output += f"  Name: {user.get('first_name', '')} {user.get('last_name', '')} 🧑\n"
    contact = user.get('contact', {})
    output += f"  Phone: {contact.get('code', '')}{contact.get('phone_number', 'N/A')} 📞\n"
    output += f"  Image: {user.get('image', 'N/A')} 🖼️\n"
    
    fvpas = user.get('fvpas', [])
    if fvpas:
        output += "  UPI Addresses:\n"
        for f in fvpas:
            output += f"    - {f.get('vpa', {}).get('address', 'N/A')} 💳\n"
    
    upi_params = user.get('upi_params', {})
    output += "\n💸 UPI Params:\n"
    output += f"  Amount: {upi_params.get('amount', 'N/A')} 💰\n"
    output += f"  Description: {upi_params.get('description', 'N/A')} 📝\n"
    output += f"  Min Amount: {upi_params.get('min_amount', 'N/A')} 🪙\n"
    
    output += f"\nUser Beneficiary State: {resp_json.get('user_beneficiary_state', 'N/A')} {'🟢' if resp_json.get('user_beneficiary_state') == 'active' else '🔴'}\n"
    return output

# Root route for main domain (displays "Android is watching you 🪦" in large text)
@app.route('/')
def main_landing():
    return """
    <html>
        <head>
            <title>FamUPI Payout App</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f0f0f0;
                    font-family: Arial, sans-serif;
                }
                h1 {
                    font-size: 48px;
                    text-align: center;
                    color: #333;
                }
            </style>
        </head>
        <body>
            <h1>Android is watching you 🪦</h1>
        </body>
    </html>
    """

# Query Route (supports ?key=<API_KEY>&upi=<UPI_ID> on main domain)
@app.route('/query')
def query_payout():
    global STOP_API
    api_key = request.args.get('key')
    upi_id = request.args.get('upi')
    
    if STOP_API:
        return jsonify({"message": "Android says he is sleeping 😴"}), 200

    if not api_key or api_key not in load_api_keys():
        return jsonify({"message": "Invalid or missing API key 🔐"}), 401

    if not upi_id:
        return jsonify({"message": "UPI ID is required ❗"}), 400

    data = {
        "upi_string": f"upi://pay?pa={upi_id}",
        "init_mode": "00",
        "is_uploaded_from_gallery": False
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        resp_json = response.json()
        return jsonify({"message": format_response(resp_json)})
    except Exception as e:
        return jsonify({"message": "Android says he is sleeping 😴"}), 500

# Admin routes (render.prohec.admin123.com)
@app.route('/', subdomain='render.prohec.admin123')
@limiter.limit("10 per minute")
def admin_index():
    return redirect(url_for('admin_panel', _external=True, _scheme='https'))

@app.route('/admin', methods=['GET'], subdomain='render.prohec.admin123')
@limiter.limit("10 per minute")
def admin_panel():
    keys = load_api_keys()
    return render_template('admin_panel.html', keys=keys, api_stopped=STOP_API)

@app.route('/api/keys', methods=['POST'], subdomain='render.prohec.admin123')
@limiter.limit("10 per minute")
def create_key():
    keys = load_api_keys()
    new_key = f"key_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(keys) + 1}"
    keys.append(new_key)
    save_api_keys(keys)
    return jsonify({"message": f"API Key created: {new_key} 🔑"})

@app.route('/api/keys', methods=['GET'], subdomain='render.prohec.admin123')
@limiter.limit("10 per minute")
def list_keys():
    keys = load_api_keys()
    return jsonify({"message": f"Total keys: {len(keys)} 🔑\nKeys: {', '.join(keys) if keys else 'None'}"})

@app.route('/api/keys/<key>', methods=['DELETE'], subdomain='render.prohec.admin123')
@limiter.limit("10 per minute")
def delete_key(key):
    keys = load_api_keys()
    if key in keys:
        keys.remove(key)
        save_api_keys(keys)
        return jsonify({"message": f"API Key {key} removed 🗑️"})
    return jsonify({"message": f"API Key {key} not found 😕"}), 404

@app.route('/api/stop', methods=['POST'], subdomain='render.prohec.admin123')
@limiter.limit("10 per minute")
def stop_api():
    global STOP_API
    STOP_API = True
    return jsonify({"message": "Android says he is sleeping 😴"})

@app.route('/api/resume', methods=['POST'], subdomain='render.prohec.admin123')
@limiter.limit("10 per minute")
def resume_api():
    global STOP_API
    STOP_API = False
    return jsonify({"message": "API resumed 🚀"})

# User route (render.prohec.foruser.com)
@app.route('/key=<api_key>.fam=<upi_id>', subdomain='render.prohec.foruser')
def payout(api_key, upi_id):
    global STOP_API
    if STOP_API:
        return jsonify({"message": "Android says he is sleeping 😴"}), 200

    if not api_key or api_key not in load_api_keys():
        return jsonify({"message": "Invalid or missing API key 🔐"}), 401

    if not upi_id:
        return jsonify({"message": "UPI ID is required ❗"}), 400

    data = {
        "upi_string": f"upi://pay?pa={upi_id}",
        "init_mode": "00",
        "is_uploaded_from_gallery": False
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        resp_json = response.json()
        return jsonify({"message": format_response(resp_json)})
    except Exception as e:
        return jsonify({"message": "Android says he is sleeping 😴"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
