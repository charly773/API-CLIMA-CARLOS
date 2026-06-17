import os

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

load_dotenv()

app = Flask(__name__)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def error_response(message, status_code, details=None):
    payload = {"ok": False, "error": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code


def normalize_weather_payload(data):
    main = data.get("main", {})
    temp_c = main.get("temp", 0)
    feels_like_c = main.get("feels_like", 0)

    return {
        "ok": True,
        "city": data.get("name"),
        "country": data.get("sys", {}).get("country"),
        "coordinates": {
            "lat": data.get("coord", {}).get("lat"),
            "lon": data.get("coord", {}).get("lon"),
        },
        "weather": {
            "main": data.get("weather", [{}])[0].get("main"),
            "description": data.get("weather", [{}])[0].get("description"),
            "icon": data.get("weather", [{}])[0].get("icon"),
        },
        "temperature": {
            "celsius": round(temp_c, 1),
            "fahrenheit": round(temp_c * 9 / 5 + 32, 1),
        },
        "feels_like": {
            "celsius": round(feels_like_c, 1),
            "fahrenheit": round(feels_like_c * 9 / 5 + 32, 1),
        },
        "humidity_percent": main.get("humidity"),
        "pressure_hpa": main.get("pressure"),
        "wind": {
            "speed_mps": data.get("wind", {}).get("speed"),
            "deg": data.get("wind", {}).get("deg"),
        },
        "visibility_m": data.get("visibility"),
        "sunrise": data.get("sys", {}).get("sunrise"),
        "sunset": data.get("sys", {}).get("sunset"),
    }


def fetch_weather_data(params):
    if not OPENWEATHER_API_KEY:
        return None, error_response("OpenWeather API key is missing. Set OPENWEATHER_API_KEY in .env", 401)

    try:
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=10)
    except requests.exceptions.Timeout:
        return None, error_response("Request to OpenWeather timed out", 504, {"hint": "Retry in a few seconds"})
    except requests.exceptions.RequestException as exc:
        return None, error_response("Unable to reach OpenWeather", 502, {"details": str(exc)})

    if response.status_code == 401:
        return None, error_response("Invalid or expired OpenWeather API key", 401)

    if response.status_code == 404:
        return None, error_response("Location not found", 404)

    if response.status_code >= 400:
        return None, error_response("OpenWeather request failed", response.status_code, {"details": response.text})

    try:
        data = response.json()
    except ValueError:
        return None, error_response("Invalid response from OpenWeather", 502)

    return normalize_weather_payload(data), None


def fetch_weather(params):
    data, error = fetch_weather_data(params)
    if error is not None:
        return error
    return jsonify({"ok": True, "data": data}), 200


@app.get("/health")
def health():
    return jsonify({"ok": True, "status": "healthy"})


@app.get("/")
def index():
    return jsonify({
        "ok": True,
        "message": "Weather API is running",
        "endpoints": {
            "GET /health": "Health check",
            "GET /weather?city=London": "Current weather by city",
            "GET /weather?lat=40.7128&lon=-74.0060": "Current weather by coordinates",
            "POST /weather/multiple": "Batch weather lookup",
            "GET /weather-ui": "HTML weather interface",
            "GET /cloud.png": "Generated cloud image",
        },
    })


@app.get("/weather-ui")
def weather_ui():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>ING DIAZ</title>
      <style>
        body { margin: 0; min-height: 100vh; background: #eaf4ff; color: #0f172a; font-family: Arial, sans-serif; display: flex; align-items: center; justify-content: center; padding: 24px; }
        .card { width: 100%; max-width: 560px; background: #ffffff; border-radius: 22px; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.12); padding: 28px; }
        h1 { margin-top: 0; font-size: 2rem; letter-spacing: 0.02em; }
        label { display: block; margin-top: 16px; font-weight: 600; }
        input { width: 100%; padding: 14px 16px; margin-top: 8px; border: 1px solid #cbd5e1; border-radius: 12px; font-size: 1rem; }
        button { margin-top: 18px; width: 100%; background: #0ea5e9; color: #ffffff; border: none; border-radius: 12px; padding: 14px 18px; font-size: 1rem; cursor: pointer; }
        button:hover { background: #0284c7; }
        #result { margin-top: 24px; }
        .weather-field { margin: 10px 0; line-height: 1.5; }
        #cloudImg { display: none; width: 120px; margin-bottom: 16px; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>ING DIAZ</h1>
        <label for="cityInput">Ingresa una ciudad:</label>
        <input id="cityInput" placeholder="Ej. Toluca" />
        <button id="getWeatherBtn">Clima</button>
        <div id="result">
          <img id="cloudImg" src="/cloud.png" alt="Nube" />
          <div id="weatherOutput"></div>
        </div>
      </div>
      <script>
        const output = document.getElementById('weatherOutput');
        const cloud = document.getElementById('cloudImg');

        async function showWeather() {
          const city = document.getElementById('cityInput').value.trim();
          if (!city) {
            output.innerHTML = '<p class="weather-field">Por favor ingresa una ciudad.</p>';
            cloud.style.display = 'none';
            return;
          }

          output.innerHTML = '<p class="weather-field">Consultando clima...</p>';
          cloud.style.display = 'none';

          try {
            const response = await fetch(`/weather?city=${encodeURIComponent(city)}`);
            const json = await response.json();
            if (!response.ok || !json.ok) {
              output.innerHTML = `<p class="weather-field">Error: ${json.error || 'No se encontró clima'}</p>`;
              return;
            }

            const data = json.data;
            output.innerHTML = `
              <div class="weather-field"><strong>Ciudad:</strong> ${data.city || ''} ${data.country ? ', ' + data.country : ''}</div>
              <div class="weather-field"><strong>Temperatura:</strong> ${data.temperature.celsius} °C</div>
              <div class="weather-field"><strong>Clima:</strong> ${data.weather.description || ''}</div>
              <div class="weather-field"><strong>Humedad:</strong> ${data.humidity_percent} %</div>
              <div class="weather-field"><strong>Viento:</strong> ${data.wind.speed_mps} m/s</div>
              <div class="weather-field"><strong>Presión:</strong> ${data.pressure_hpa} hPa</div>
            `;
            cloud.style.display = 'block';
          } catch (error) {
            output.innerHTML = '<p class="weather-field">Error al consultar la API.</p>';
          }
        }

        document.getElementById('getWeatherBtn').addEventListener('click', showWeather);
      </script>
    </body>
    </html>
    """


@app.get("/cloud.png")
def cloud_image():
    with Image(width=320, height=220, background=Color('skyblue')) as img:
        with Drawing() as draw:
            draw.fill_color = Color('white')
            draw.stroke_color = Color('lightgray')
            draw.stroke_width = 2
            draw.circle((120, 120), (80, 120))
            draw.circle((160, 100), (120, 100))
            draw.circle((200, 120), (170, 120))
            draw.circle((160, 140), (130, 150))
            draw.draw(img)
            draw.fill_color = Color('white')
            draw.stroke_color = Color('transparent')
            draw.rectangle(left=100, top=120, width=120, height=40)
            draw.draw(img)
        blob = img.make_blob('png')
    return Response(blob, mimetype='image/png')


@app.get("/weather")
def weather_by_query():
    city = request.args.get("city", "").strip()
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if city:
        params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        return fetch_weather(params)

    if lat is None or lon is None:
        return error_response("Provide either 'city' or both 'lat' and 'lon'", 400)

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return error_response("Coordinates out of range", 400, {"lat": "-90 to 90", "lon": "-180 to 180"})

    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    return fetch_weather(params)


@app.post("/weather/multiple")
def weather_multiple():
    payload = request.get_json(silent=True) or {}
    locations = payload.get("locations")

    if not isinstance(locations, list) or not locations:
        return error_response("Expected JSON body with a non-empty 'locations' array", 400)

    results = []
    for index, item in enumerate(locations):
        if not isinstance(item, dict):
            results.append({"ok": False, "error": "Each location must be an object", "index": index})
            continue

        city = str(item.get("city", "")).strip() if item.get("city") is not None else ""
        lat = item.get("lat")
        lon = item.get("lon")

        if city:
            data, error = fetch_weather_data({"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"})
            if error is not None:
                results.append({"index": index, "input": {"city": city}, "response": error[0].json if hasattr(error[0], "json") else error})
            else:
                results.append({"index": index, "input": {"city": city}, "response": {"ok": True, "data": data}})
            continue

        if lat is None or lon is None:
            results.append({"index": index, "ok": False, "error": "Provide either 'city' or both 'lat' and 'lon'"})
            continue

        try:
            lat_value = float(lat)
            lon_value = float(lon)
        except (TypeError, ValueError):
            results.append({"index": index, "ok": False, "error": "Latitude and longitude must be numbers"})
            continue

        if not (-90 <= lat_value <= 90 and -180 <= lon_value <= 180):
            results.append({"index": index, "ok": False, "error": "Coordinates out of range"})
            continue

        data, error = fetch_weather_data({"lat": lat_value, "lon": lon_value, "appid": OPENWEATHER_API_KEY, "units": "metric"})
        if error is not None:
            results.append({"index": index, "input": {"lat": lat_value, "lon": lon_value}, "response": error[0].json if hasattr(error[0], "json") else error})
        else:
            results.append({"index": index, "input": {"lat": lat_value, "lon": lon_value}, "response": {"ok": True, "data": data}})

    return jsonify({"ok": True, "results": results}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
