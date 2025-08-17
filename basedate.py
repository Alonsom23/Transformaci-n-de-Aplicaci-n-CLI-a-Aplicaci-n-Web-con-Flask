import redis
import os
from dotenv import load_dotenv
from redis.exceptions import ConnectionError, RedisError

# Cargar variables de entorno desde .env
load_dotenv()

# --- Configuración de la Conexión a KeyDB ---
KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
KEYDB_PORT = int(os.getenv("KEYDB_PORT", 6379))
KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD") # Será None si no está en .env o está vacío

_redis_client = None # Variable global para el cliente de Redis

def get_redis_client():
    """
    Establece una conexión a KeyDB (Redis) y devuelve el cliente.
    Maneja errores de conexión y reutiliza la conexión existente.
    """
    global _redis_client
    if _redis_client is None:
        try:
            # Conectar a Redis/KeyDB
            _redis_client = redis.StrictRedis(
                host=KEYDB_HOST,
                port=KEYDB_PORT,
                password=KEYDB_PASSWORD,
                decode_responses=True # Decodifica automáticamente las respuestas a strings de Python
            )
            # Intenta ejecutar un comando simple para verificar la conexión
            _redis_client.ping()
            print(f"Conexión a KeyDB exitosa. Host: {KEYDB_HOST}, Puerto: {KEYDB_PORT}")
        except ConnectionError as e:
            print(f"Error de conexión a KeyDB: {e}")
            print("Asegúrate de que KeyDB esté ejecutándose y que la configuración en .env sea correcta.")
            _redis_client = None
            return None
        except RedisError as e:
            print(f"Error general de Redis/KeyDB: {e}")
            _redis_client = None
            return None
    return _redis_client

# Función para cerrar la conexión (opcional, pero buena práctica)
def close_db_connection():
    """Cierra la conexión activa de KeyDB."""
    global _redis_client
    if _redis_client:
        _redis_client.close()
        print("Conexión a KeyDB cerrada.")
        _redis_client = None

if __name__ == "__main__":
    # Si ejecutas database.py directamente, intentará conectar
    client = get_redis_client()
    if client:
        print("Cliente de KeyDB listo para operar.")
    close_db_connection()