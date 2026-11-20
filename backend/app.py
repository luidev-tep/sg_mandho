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
#print(f"El valor de mi variable de prueba es: {os.environ.get('TEST_VARIABLE')}")

# Importaciones de tus rutas
from src.routes.user_route import user_route
from src.routes.account_route import account_route
from src.routes.search_real_time import search_route
from src.routes.security_route import security_route
from src.routes.payment_route import payment_route
from src.routes.analitycs_route import analitycs_route
from src.routes.home_route import home_route
from src.utils.conexion import Conexion, get_pool_status, init_db_teardown


app = Flask(__name__)
init_db_teardown(app)

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("No se encontró la SECRET_KEY en el entorno. La aplicación no puede iniciar de forma segura.")
app.config['JWT_SECRET_KEY'] = secret_key

# Configuración de los tiempos de expiración
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=20)
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
#print("Configuración detallada de CORS")   
#print(os.environ.get("URL_FRONTEND"))

# Obtener las URLs del frontend
frontend_urls = os.environ.get("URL_FRONTEND", "http://localhost:5173")
# Convertir a lista si hay múltiples URLs separadas por coma
origins_list = [url.strip().rstrip('/') for url in frontend_urls.split(',') if url.strip()]

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

@app.get('/health')
def health():
    try:
        with Conexion() as db:
            db.cursor.execute('SELECT 1')
            db.cursor.fetchone()
        return {'status': 'ok', 'database': 'up', 'pool': get_pool_status()}, 200
    except Exception:
        return {'status': 'degraded', 'database': 'down'}, 503


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').strip().lower() in ('true', '1', 'yes')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')), debug=debug_mode)
