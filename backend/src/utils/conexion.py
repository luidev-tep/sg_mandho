import os
import urllib.parse
from typing import Optional, Tuple, Any
import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

load_dotenv()

_engine: Optional[Engine] = None

# Excepción unificada para que todos los repositorios capturen DatabaseError
DatabaseError = pyodbc.Error


def _build_odbc_connection_string() -> str:
    driver = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.environ.get("DB_SERVER", r"localhost\SQLEXPRESS")
    database = os.environ.get("DB_NAME", "sg_mandho")
    user = os.environ.get("DB_USER", "").strip()
    password = os.environ.get("DB_PASSWORD", "")
    default_encrypt = "yes" if user else "no"
    default_trust_cert = "no" if user else "yes"
    encrypt = os.environ.get("DB_ENCRYPT") or default_encrypt
    trust_cert = os.environ.get("DB_TRUST_CERT") or default_trust_cert
    timeout = os.environ.get("DB_CONNECT_TIMEOUT", "30")
    trusted_raw = os.environ.get("DB_TRUSTED_CONNECTION")
    if trusted_raw is None or not trusted_raw.strip():
        trusted_conn = not bool(user)
    else:
        trusted_conn = trusted_raw.strip().lower() in ("yes", "true", "1")

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        f"Encrypt={encrypt}",
        f"TrustServerCertificate={trust_cert}",
        f"Connection Timeout={timeout}",
        "ConnectRetryCount=3",
        "ConnectRetryInterval=10",
    ]
    if trusted_conn:
        parts.append("Trusted_Connection=yes")
    else:
        parts.append(f"UID={user}")
        escaped_pwd = password.replace("}", "}}")
        parts.append(f"PWD={{{escaped_pwd}}}")

    return ";".join(parts) + ";"


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        conn_str = _build_odbc_connection_string()
        odbc_url = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(conn_str)
        _engine = create_engine(
            odbc_url,
            poolclass=QueuePool,
            pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),
            max_overflow=int(os.environ.get("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.environ.get("DB_POOL_TIMEOUT", "30")),
            pool_pre_ping=True,
            pool_recycle=1800,
            # Desactivar autocommit en pyodbc para garantizar control transaccional explícito
            connect_args={"autocommit": False},
        )
    return _engine


def get_pool_status() -> dict[str, int]:
    """Utilidad de diagnóstico y para assertions en tests E2E de fugas de conexión."""
    engine = _get_engine()
    pool = engine.pool
    return {
        "size": pool.size(),
        "checkedin": pool.checkedin(),
        "checkedout": pool.checkedout(),
        "overflow": pool.overflow(),
    }


def get_engine_pool_status() -> dict[str, int]:
    """Alias para compatibilidad de interfaz con la SPEC."""
    return get_pool_status()


def dispose_engine() -> None:
    """Cierra todas las conexiones físicas del pool (útil en teardown de tests)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


def init_db_teardown(app) -> None:
    """Registra hook de teardown en Flask app si se requiere manejo por contexto."""
    @app.teardown_appcontext
    def close_db(exception=None):
        pass


class Conexion:
    """
    Gestiona una conexión a SQL Server obtenida del QueuePool de SQLAlchemy.

    Modos de uso:
    1. Autónomo (por defecto, compatible con los 31 módulos):
       db = Conexion()
       db.cursor.execute(...)
       db.save_changes()
       db.close_conexion()

    2. Transacción compartida (Unidad de Trabajo / Fase 2):
       with Conexion() as tx:
           repo_step_1(data, db=tx)  # internamente hace Conexion(shared_conn=tx)
           repo_step_2(data, db=tx)
           tx.save_changes()         # único commit al final
    """

    def __init__(self, shared_conn: Optional["Conexion"] = None) -> None:
        self._closed = False
        if shared_conn is not None:
            # Modo préstamo: participa en la transacción de shared_conn
            self._owns_connection = False
            self.conn = shared_conn.conn
            self.cursor = shared_conn.cursor
            self.__ruta = shared_conn.get_route()
        else:
            # Modo autónomo: toma una conexión del pool
            self._owns_connection = True
            server = os.environ.get("DB_SERVER", r"localhost\SQLEXPRESS")
            database = os.environ.get("DB_NAME", "sg_mandho")
            self.__ruta = f"{server}/{database}"
            try:
                self.conn = _get_engine().raw_connection()
                self.cursor = self.conn.cursor()
            except pyodbc.Error as e:
                print(f"Error al conectar con la base de datos SQL Server: {e}")
                raise

    def get_route(self) -> str:
        return self.__ruta

    def conexion(self) -> Tuple[Any, Any]:
        if self.conn is None or self.cursor is None:
            raise pyodbc.Error("La conexión o el cursor no están inicializados.")
        return self.conn, self.cursor

    def save_changes(self) -> None:
        """
        Hace commit de la transacción actual SOLO si esta instancia es dueña de la conexión.
        Si es una conexión prestada (_owns_connection=False), delega el commit al coordinador.
        """
        if not self._owns_connection:
            return
        try:
            self.conn.commit()
        except pyodbc.Error as e:
            print(f"Error al guardar los cambios (commit): {e}")
            raise

    def rollback(self) -> None:
        """Revierte explícitamente los cambios no confirmados en la conexión actual."""
        try:
            if self.conn:
                self.conn.rollback()
        except pyodbc.Error as e:
            print(f"Error al revertir los cambios (rollback): {e}")
            raise

    def close_conexion(self) -> None:
        """
        Devuelve la conexión al QueuePool si esta instancia es la dueña.
        Idempotente: llamar a close_conexion() dos veces no lanza error.
        """
        if not self._owns_connection or self._closed:
            return
        try:
            if self.cursor is not None:
                self.cursor.close()
            if self.conn is not None:
                # SQLAlchemy _ConnectionFairy ejecuta rollback() automático de cambios
                # no commiteados antes de devolver la conexión al QueuePool.
                self.conn.close()
            self._closed = True
        except pyodbc.Error as e:
            print(f"Error al devolver la conexión al pool: {e}")
            raise

    def __enter__(self) -> "Conexion":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._owns_connection:
            if exc_type is not None:
                try:
                    self.conn.rollback()
                except Exception:
                    pass
            self.close_conexion()
        return False
