from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route("/api/hello")
def greeting():
    # Get client IP address, considering proxies and load balancers
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        client_ip = request.remote_addr
    
    visitor_name = request.args.get("visitor_name", default='Guest', type=str)
    client_info = get_client_city(client_ip)
    city = client_info.get("city")
    lat = client_info.get("lat")
    lon = client_info.get('lon')
    
    if lat and lon:
        weather_info = get_temp(lon, lat)
        if weather_info:
            temp = weather_info.get('main', {}).get('temp')
            if temp is not None:
                response = {
                    "client_ip": client_ip,
                    "location": city,
                    "greeting": f"Hello, {visitor_name}!, the temperature is {int(temp)} degree Celsius in {city}."
                }
                return jsonify(response)
    
    return jsonify({"error": "Failed to retrieve weather information."}), 500

@app.route("/")
def index():
    return jsonify({
        "Message": "Welcome to Home Page"
    })

def get_client_city(ip_address):
    url = f"https://ipinfo.io/{ip_address}"
    params = {
        "token": "725d6d9de86576"
    }
    try:
        response = requests.get(url, params=params).json()
        city = response.get("city", "Newyork")  # Default to Newyork if city not found
        loc = response.get('loc', '0,0')  # Default to '0,0' if loc not found
        longitude, latitude = loc.split(',')
        
        data = {
            "city": city,
            "lon": longitude,
            "lat": latitude
        }
        return data
    
    except Exception as e:
        print(f"Error fetching city information: {str(e)}")
        return {"city": "Unknown", "lon": "0", "lat": "0"}  # Return default values in case of error

def get_temp(longitude, latitude):
    WEATHER_API_KEY = 'a53a8066ad9b9ec896f571174cc52a25'
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}&units=metric'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch weather data: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"Error getting weather information: {str(e)}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
