#app.py

# Fichero el cual creara la instancia de flask # 
import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# --- CORRECCIÓN 1: Cargar el .env PRIMERO ---
# Esta línea DEBE estar al principio, antes de acceder a cualquier variable de entorno.
load_dotenv()

# --- CORRECCIÓN 2: Comprobar la variable de prueba aquí ---
# Ahora que .env está cargado, la variable de prueba SÍ se encontrará.
print(f"El valor de mi variable de prueba es: {os.environ.get('TEST_VARIABLE')}")

# Importaciones de tus rutas
from src.routes.user_route import user_route
from src.routes.account_route import account_route
from src.routes.search_real_time import search_route
from src.routes.security_route import security_route
from src.routes.payment_route import payment_route
from src.routes.analitycs_route import analitycs_route
from src.routes.home_route import home_route


app = Flask(__name__)

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("No se encontró la SECRET_KEY en el entorno. La aplicación no puede iniciar de forma segura.")
app.config['JWT_SECRET_KEY'] = secret_key

# Configuración de los tiempos de expiración
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)

#Registro de blueprints
app.register_blueprint(user_route)
app.register_blueprint(account_route)
app.register_blueprint(search_route)
app.register_blueprint(security_route)
app.register_blueprint(payment_route)
app.register_blueprint(analitycs_route)
app.register_blueprint(home_route)

# Configuración detallada de CORS - CORREGIDA PARA EDGE
print("Configuración detallada de CORS")   
print(os.environ.get("URL_FRONTEND"))

# Obtener las URLs del frontend
frontend_urls = os.environ.get("URL_FRONTEND", "http://localhost:5173")
# Convertir a lista si hay múltiples URLs separadas por coma
origins_list = [url.strip() for url in frontend_urls.split(',')]

CORS(app, resources={
    r"/*": {
        "origins": origins_list,  # Usar lista en lugar de string
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        "expose_headers": ["Content-Disposition"],
        "supports_credentials": True,
        "max_age": 86400,
        "send_wildcard": False,  # IMPORTANTE: Edge requiere esto en False
        "always_send": True  # Enviar headers CORS siempre, incluso en OPTIONS
    }
})

# Handler adicional para OPTIONS (preflight) - CRÍTICO PARA EDGE
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in origins_list:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept,Origin,Access-Control-Request-Method,Access-Control-Request-Headers')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '86400')
    return response

if __name__ == '__main__':
    app.run(debug=True)