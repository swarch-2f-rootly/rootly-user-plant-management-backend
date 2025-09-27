# -*- coding: utf-8 -*-
import psycopg2
import sys
from datetime import datetime

print(f"=== Diagnóstico PostgreSQL - {datetime.now()} ===")

try:
    print("1. Importando psycopg2...")
    import psycopg2
    print("   ✅ psycopg2 importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando psycopg2: {e}")
    sys.exit(1)

# Probar diferentes configuraciones de conexión
connection_configs = [
    {
        "name": "URL completa",
        "dsn": "postgresql://postgres:postgres@localhost:5432/rootly"
    },
    {
        "name": "Parámetros individuales", 
        "kwargs": {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "postgres",
            "database": "rootly",
            "connect_timeout": 5
        }
    },
    {
        "name": "Sin base de datos específica",
        "kwargs": {
            "host": "localhost", 
            "port": 5432,
            "user": "postgres",
            "password": "postgres",
            "database": "postgres",  # DB por defecto
            "connect_timeout": 5
        }
    }
]

for config in connection_configs:
    print(f"\n2. Probando conexión: {config['name']}")
    try:
        if 'dsn' in config:
            conn = psycopg2.connect(config['dsn'])
        else:
            conn = psycopg2.connect(**config['kwargs'])
        
        print("   ✅ Conexión exitosa")
        
        # Probar una consulta simple
        cur = conn.cursor()
        cur.execute("SELECT version(), current_database(), current_user")
        result = cur.fetchone()
        print(f"   ✅ PostgreSQL: {result[0]}")
        print(f"   ✅ Base de datos: {result[1]}")
        print(f"   ✅ Usuario: {result[2]}")
        
        cur.close()
        conn.close()
        break  # Si una conexión funciona, salir
        
    except psycopg2.OperationalError as e:
        print(f"   ❌ Error operacional: {e}")
    except psycopg2.Error as e:
        print(f"   ❌ Error de PostgreSQL: {e}")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

print("\n=== Diagnóstico completado ===")
