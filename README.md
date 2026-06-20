API Clima con Wand

API REST para consultar el clima en tiempo real con una interfaz web moderna e imágenes de nubes generadas dinámicamente con Wand.

Características

- API Weather Obtiene datos del clima en tiempo real de OpenWeather
- Interfaz Web HTML Página responsiva para consultar el clima
- Generación de Imágenes Crea imágenes de nubes con Wand
- Docker Listo para ejecutar en contenedores
- GitHub Actions**: CI/CD automático
- Codespaces Ejecutable desde GitHub con VS Code en la nube

Inicio Rápido
Para hacer las peticiones a la API de OpenWeather usar:
python3 -m pip install requests

Para poder leer las variables del archivo .env usar:
python3 -m pip install python-dotenv

El framework web para crear la API y las rutas usar:
python3 -m pip install flask

La librería para manipular y generar la imagen de la nube (cloud.png) usar:
python3 -m pip install Wand

y para ejecutar es 
python3 app.py ó PORT=5001 python3 app.py

Para docker es:
docker build -t weather-api 
docker run -d --name weather-api -p 8000:5000 weather-api
Abre: `http://localhost:5001/weather-ui`

Docker
http://localhost:8000/weather-ui

No cuenta con Codespace 
