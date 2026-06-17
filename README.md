# 🌤️ API Clima con Wand

API REST para consultar el clima en tiempo real con una interfaz web moderna e imágenes de nubes generadas dinámicamente con Wand.

## ✨ Características

- **API Weather**: Obtiene datos del clima en tiempo real de OpenWeather
- **Interfaz Web HTML**: Página responsiva para consultar el clima
- **Generación de Imágenes**: Crea imágenes de nubes con Wand
- **Docker**: Listo para ejecutar en contenedores
- **GitHub Actions**: CI/CD automático
- **Codespaces**: Ejecutable desde GitHub con VS Code en la nube

## 🚀 Inicio Rápido

### Local
```bash
pip install -r requirements.txt
python app.py
```
Abre: `http://localhost:5000/weather-ui`

### Docker
```bash
docker build -t weather-api .
docker run -d -p 8000:5000 weather-api
```
Abre: `http://localhost:8000/weather-ui`

### GitHub Codespaces
1. Presiona `.` en el repositorio o haz clic en **Code > Codespaces > Create codespace on main**
2. Espera a que se cargue el contenedor
3. En la terminal, ejecuta: `python app.py`
4. Cuando veas el link, haz clic en **Open in Browser**

## 📝 Variables de Entorno

Para ejecutar localmente, crea un archivo `.env` en la raíz:
```
OPENWEATHER_API_KEY=tu_clave_aqui
PORT=5000
```

> Nota: no subas el archivo `.env` al repositorio. Ya está agregado a `.gitignore`.

### GitHub Actions

Para que el pipeline pueda ejecutar el contenedor en CI, agrega un secret en GitHub:
- Name: `OPENWEATHER_API_KEY`
- Value: tu clave de OpenWeather

GitHub Actions usará ese secret para el job de smoke test del contenedor.

## 📚 Endpoints

- `GET /` - Información de la API
- `GET /health` - Health check
- `GET /weather?city=Toluca` - Clima por ciudad
- `GET /weather?lat=40.7128&lon=-74.0060` - Clima por coordenadas
- `GET /weather-ui` - Interfaz web
- `GET /cloud.png` - Imagen de nube generada

## 🛠️ Tecnologías

- **Backend**: Flask
- **Clima**: OpenWeatherMap API
- **Imágenes**: Wand (ImageMagick)
- **Contenedores**: Docker
- **CI/CD**: GitHub Actions

## 📦 Dependencias

```
Flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
Wand==0.6.13
```

## 🐳 Dockerfile

La imagen incluye ImageMagick y libmagickwand-dev necesarios para Wand.

## ✅ GitHub Actions

Los tests se ejecutan automáticamente en GitHub Actions al hacer push.

---

**Creado por**: ING DIAZ  
**Repositorio**: https://github.com/charly773/API-CLIMA-CON-WAND
